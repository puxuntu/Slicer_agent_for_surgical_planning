"""MCP transports for the Claude Code + Slicer-skill baseline.

Two mechanisms live here. The one the panel uses is :class:`BaselineMCPBridge`.

``BaselineMCPBridge`` -- DEFAULT. Attaches to the stand-alone
``slicer-mcp-server.py`` that ships with the Slicer skill and that the user
pastes into Slicer's Python console, exactly as the skill's own documentation
prescribes. While a baseline step is armed it swaps that server's
``execute_python`` handler for one that routes the code through the agent's
CodeValidator + SafeExecutor and advances the workflow step; disarming puts the
original handler back. Nothing else about the skill's setup changes, so the
condition under test really is "Claude Code + the Slicer skill as shipped".

``BaselineMCPServer`` -- fallback, not used by the panel. A self-hosted endpoint
with the same tool surface on its own port, for the case where the console
script cannot be used. Kept because it needs no console paste; selecting it is a
deliberate deviation from the skill's documented setup and should be recorded as
such.

--------------------------------------------------------------------------

MCP endpoint hosted by the agent, used by the Claude Code + Slicer-skill baseline.

An external Claude Code session (running the ``slicer-skill`` skill) talks to
this endpoint over the MCP Streamable-HTTP transport in JSON-response mode, the
same shape as the stand-alone ``slicer-mcp-server.py`` reference script. The
tool surface is deliberately identical (``list_nodes``, ``get_node_properties``,
``execute_python``, ``screenshot``) so that skill works here unchanged.

The one addition is *arming*. While the workflow panel has armed the server for
a baseline step, an incoming ``execute_python`` call is not exec'd raw: the code
is handed to the armed callback, which pushes it through the agent's own
CodeValidator -> SafeExecutor path and then advances the workflow step -- so the
Claude Code condition executes through exactly the same tail as the other two
baselines. The tool's return value still carries the real stdout/stderr, so
Claude Code sees what happened and can iterate as it normally would.

Disarmed, the endpoint behaves like the plain reference server.

Runs entirely on the Qt main thread: Slicer's WebServer dispatches requests
through the Qt event loop, which is why the armed callback may execute code
synchronously and return its output in the same response.
"""

import base64
import json
import logging
import os
import threading
import traceback
import urllib.parse
from typing import Any, Callable, Dict, List, Optional, Tuple

import qt
import slicer

logger = logging.getLogger(__name__)


DEFAULT_PORT = 2027
MCP_PATH = b"/mcp"
PROTOCOL_VERSION = "2025-03-26"
SERVER_INFO = {"name": "slicer-ai-agent-baseline", "version": "1.0.0"}
SERVER_CAPABILITIES = {"tools": {}}


# ---------------------------------------------------------------------------
# Tool schemas + default (disarmed) handlers
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "list_nodes",
        "description": (
            "List MRML nodes in the Slicer scene. Returns name, id and class "
            "for each node."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "className": {
                    "type": "string",
                    "description": (
                        "MRML node class filter (e.g. 'vtkMRMLScalarVolumeNode'). "
                        "Default: all nodes."
                    ),
                }
            },
        },
    },
    {
        "name": "get_node_properties",
        "description": "Get the full property dump of an MRML node by its ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "MRML node ID (e.g. 'vtkMRMLScalarVolumeNode1')",
                }
            },
            "required": ["id"],
        },
    },
    {
        "name": "execute_python",
        "description": (
            "Execute Python code in the running Slicer environment. Set the "
            "variable __result to return a value to the caller."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"],
        },
    },
    {
        "name": "screenshot",
        "description": "Capture the Slicer application window as a PNG image.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _text(message: str) -> List[Dict[str, str]]:
    return [{"type": "text", "text": str(message)}]


def _tool_list_nodes(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    class_name = args.get("className") or "vtkMRMLNode"
    nodes = slicer.util.getNodesByClass(class_name)
    payload = [
        {"name": node.GetName(), "id": node.GetID(), "class": node.GetClassName()}
        for node in nodes
    ]
    return _text(json.dumps(payload, indent=2))


def _tool_get_node_properties(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    node_id = args.get("id", "")
    node = slicer.mrmlScene.GetNodeByID(node_id)
    if not node:
        return _text(f"Node '{node_id}' not found")
    return _text(str(node))


def _tool_screenshot(_args: Dict[str, Any]) -> List[Dict[str, Any]]:
    slicer.app.processEvents()
    slicer.util.forceRenderAllViews()
    pixmap = slicer.util.mainWindow().grab()
    byte_array = qt.QByteArray()
    buffer = qt.QBuffer(byte_array)
    buffer.open(qt.QIODevice.WriteOnly)
    pixmap.save(buffer, "PNG")
    encoded = base64.b64encode(bytes(byte_array.data())).decode("ascii")
    return [{"type": "image", "data": encoded, "mimeType": "image/png"}]


def _tool_execute_python_raw(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Disarmed ``execute_python``: plain exec in Slicer's ``__main__``."""
    import sys

    code = args.get("code", "")
    exec_globals = sys.modules["__main__"].__dict__
    exec_globals.setdefault("__result", None)
    exec_globals["__result"] = None
    try:
        exec(code, exec_globals)
    except Exception:
        return _text(f"Error:\n{traceback.format_exc()}")
    result = exec_globals.get("__result")
    return _text(str(result) if result is not None else "OK (no __result set)")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

class BaselineMCPServer:
    """Singleton MCP endpoint owned by the agent widget.

    Lifecycle: ``start()`` on demand (the first time the Claude Code baseline is
    selected), ``arm(callback)`` for one step, ``disarm()`` afterwards, and
    ``stop()`` on widget cleanup. Starting is idempotent.
    """

    _instance: Optional["BaselineMCPServer"] = None

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = int(port)
        self._logic = None
        self._lock = threading.Lock()
        self._armed_callback: Optional[Callable[[str], Dict[str, Any]]] = None
        self._armed_label = ""
        self._access_allowed: Optional[bool] = None
        self.last_error = ""

    # -- singleton ---------------------------------------------------------
    @classmethod
    def instance(cls, port: int = DEFAULT_PORT) -> "BaselineMCPServer":
        if cls._instance is None:
            cls._instance = cls(port)
        return cls._instance

    # -- state -------------------------------------------------------------
    @property
    def running(self) -> bool:
        return self._logic is not None

    @property
    def armed(self) -> bool:
        return self._armed_callback is not None

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}/mcp"

    def client_config_snippet(self) -> str:
        """The one-line MCP client config that points at this endpoint."""
        return json.dumps(
            {"mcpServers": {"slicer-agent": {"url": self.url}}},
            ensure_ascii=False,
        )

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> bool:
        """Start the endpoint. Returns True when it is running afterwards."""
        if self._logic is not None:
            return True
        try:
            import WebServer
            import WebServerLib
        except Exception as exc:
            self.last_error = (
                "Slicer's WebServer module is not available, so the MCP endpoint "
                f"cannot start ({exc}). Install/enable the WebServer module."
            )
            logger.warning(self.last_error)
            return False

        handler = _BaselineMCPRequestHandler(self, WebServerLib.BaseRequestHandler)
        try:
            self._logic = WebServer.WebServerLogic(
                port=self.port,
                logMessage=lambda *a: logger.debug("BaselineMCP: %s", " ".join(str(x) for x in a)),
                enableSlicer=False,
                enableExec=False,
                enableStaticPages=False,
                enableDICOM=False,
                enableCORS=True,
                requestHandlers=[handler],
            )
            self._logic.start()
            # WebServerLogic may fall back to a different free port.
            self.port = int(getattr(self._logic, "port", self.port))
            self.last_error = ""
            logger.info("Baseline MCP endpoint listening on %s", self.url)
            return True
        except Exception as exc:
            self._logic = None
            self.last_error = f"Failed to start the MCP endpoint on port {self.port}: {exc}"
            logger.warning(self.last_error, exc_info=True)
            return False

    def stop(self) -> None:
        self.disarm()
        logic, self._logic = self._logic, None
        if logic is None:
            return
        try:
            logic.stop()
        except Exception:
            logger.debug("Baseline MCP stop failed", exc_info=True)

    # -- arming ------------------------------------------------------------
    def arm(self, callback: Callable[[str], Dict[str, Any]], label: str = "") -> None:
        """Route the next ``execute_python`` call to ``callback``.

        ``callback(code)`` runs on the Qt main thread and must return a dict
        with ``success`` / ``output`` / ``error`` keys. It stays armed until
        :meth:`disarm` -- the caller disarms once the step has advanced, so a
        Claude Code retry after a failed attempt is still captured.
        """
        with self._lock:
            self._armed_callback = callback
            self._armed_label = label or ""

    def disarm(self) -> None:
        with self._lock:
            self._armed_callback = None
            self._armed_label = ""

    def _current_callback(self):
        with self._lock:
            return self._armed_callback

    # -- access gate -------------------------------------------------------
    def check_access(self) -> bool:
        """Confirm once per session that an MCP client may drive this Slicer."""
        if self._access_allowed is not None:
            return self._access_allowed
        try:
            box = qt.QMessageBox(slicer.util.mainWindow())
            box.setWindowTitle("MCP Client Requesting Connection")
            box.setIcon(qt.QMessageBox.Warning)
            box.setText("Allow an MCP client to connect to the SlicerAIAgent baseline endpoint?")
            box.setInformativeText(
                "If you allow this, the client will be able to execute arbitrary "
                "Python code in this Slicer session, with full access to the "
                "filesystem, network and any loaded data (including patient "
                "data).\n\nOnly allow this if you trust the connecting application."
            )
            box.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
            box.setDefaultButton(qt.QMessageBox.No)
            self._access_allowed = box.exec() == qt.QMessageBox.Yes
        except Exception:
            logger.debug("MCP access dialog failed; denying", exc_info=True)
            self._access_allowed = False
        return self._access_allowed

    def reset_access(self) -> None:
        self._access_allowed = None

    # -- dispatch ----------------------------------------------------------
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Run one MCP tool call and return the ``tools/call`` result body."""
        try:
            if name == "list_nodes":
                return {"content": _tool_list_nodes(arguments), "isError": False}
            if name == "get_node_properties":
                return {"content": _tool_get_node_properties(arguments), "isError": False}
            if name == "screenshot":
                return {"content": _tool_screenshot(arguments), "isError": False}
            if name == "execute_python":
                return self._call_execute_python(arguments)
        except Exception:
            return {"content": _text(traceback.format_exc()), "isError": True}
        return {"content": _text(f"Unknown tool: {name}"), "isError": True}

    def _call_execute_python(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        callback = self._current_callback()
        if callback is None:
            return {"content": _tool_execute_python_raw(arguments), "isError": False}

        code = str(arguments.get("code", "") or "")
        try:
            outcome = callback(code) or {}
        except Exception:
            logger.warning("Armed baseline callback raised", exc_info=True)
            return {"content": _text(f"Error:\n{traceback.format_exc()}"), "isError": True}

        lines = []
        header = self._armed_label or "baseline step"
        if outcome.get("success"):
            lines.append(f"OK - executed for {header}.")
        else:
            lines.append(f"FAILED - executed for {header}.")
        if outcome.get("output"):
            lines.append(f"\nOutput:\n{outcome['output']}")
        if outcome.get("error"):
            lines.append(f"\nError:\n{outcome['error']}")
        if outcome.get("note"):
            lines.append(f"\n{outcome['note']}")
        return {"content": _text("\n".join(lines)), "isError": not outcome.get("success")}

    # -- JSON-RPC ----------------------------------------------------------
    def dispatch(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route one JSON-RPC message; returns None for notifications."""
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params") or {}

        if method == "initialize":
            return _ok(msg_id, {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": SERVER_CAPABILITIES,
                "serverInfo": SERVER_INFO,
            })
        if method in ("notifications/initialized", "notifications/cancelled"):
            return None
        if method == "ping":
            return _ok(msg_id, {})
        if method == "tools/list":
            return _ok(msg_id, {"tools": TOOL_SCHEMAS})
        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            return _ok(msg_id, self.call_tool(name, arguments))
        if msg_id is not None:
            return _err(msg_id, -32601, f"Method not found: {method}")
        return None


def _ok(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _err(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _BaselineMCPRequestHandler(server: BaselineMCPServer, base_class):
    """Build a WebServer request handler bound to ``server``.

    Written as a factory because ``WebServerLib.BaseRequestHandler`` can only be
    imported once Slicer's WebServer module is available, which is not
    guaranteed at import time of this module.
    """

    class _Handler(base_class):
        def __init__(self):
            self.logMessage = lambda *a: None

        def canHandleRequest(self, uri: bytes, **_kwargs) -> float:
            try:
                return 0.6 if urllib.parse.urlparse(uri).path == MCP_PATH else 0.0
            except Exception:
                return 0.0

        def handleRequest(self, method: str, uri: bytes, requestBody: bytes, **_kwargs):
            if not server.check_access():
                return b"application/json", json.dumps(
                    _err(None, -32600, "Access denied by user")
                ).encode()

            if method == "DELETE":
                return b"application/json", b'{"ok":true}'
            if method == "GET":
                return b"application/json", json.dumps(
                    _err(None, -32600, "SSE streaming not implemented; use POST")
                ).encode()
            if method != "POST":
                return b"application/json", json.dumps(
                    _err(None, -32600, f"Unsupported HTTP method: {method}")
                ).encode()

            try:
                message = json.loads(requestBody)
            except (ValueError, json.JSONDecodeError) as exc:
                return b"application/json", json.dumps(
                    _err(None, -32700, f"Parse error: {exc}")
                ).encode()

            if isinstance(message, list):
                responses = [r for r in (server.dispatch(m) for m in message) if r is not None]
                if not responses:
                    return b"application/json", b"{}"
                body = responses if len(responses) > 1 else responses[0]
                return b"application/json", json.dumps(body).encode()

            response = server.dispatch(message)
            if response is None:
                return b"application/json", b"{}"
            return b"application/json", json.dumps(response).encode()

    return _Handler()


# ---------------------------------------------------------------------------
# Launching the skill's own server (so the user does not have to paste it)
# ---------------------------------------------------------------------------

#: The skill's shipped console script, relative to the project root.
SKILL_MCP_SCRIPT = os.path.join(
    "Resources", "Skills", "slicer-skill-full", "slicer-mcp-server.py"
)


def skill_mcp_script_path() -> str:
    """Absolute path of the shipped ``slicer-mcp-server.py`` ("" when absent)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, SKILL_MCP_SCRIPT)
    return path if os.path.isfile(path) else ""


def run_skill_mcp_script(path: str = "") -> Tuple[bool, str]:
    """Execute the skill's server script exactly as pasting it would.

    Returns ``(ok, detail)``. Automating the *invocation* is not a modification
    of the skill: the same file is executed, byte for byte, in the same
    namespace (``__main__``), so it defines the same ``TOOL_HANDLERS`` and
    ``mcpLogic`` and exposes the same five tools. Only the user's copy-paste is
    removed.

    Deliberately NOT routed through CodeValidator/SafeExecutor. Those exist to
    contain model-generated code; this is a first-party file on disk that the
    user was otherwise going to paste by hand, and it legitimately needs the
    imports the validator blocks (``json``, ``urllib``, ``base64``, ``open``).

    Safe to call more than once: the script's own tail stops any previous
    instance before starting a new one ("so the script can be re-pasted
    safely"). Callers must still avoid re-running it while a step is ARMED,
    because a fresh ``TOOL_HANDLERS`` would drop the armed wrapper.
    """
    path = path or skill_mcp_script_path()
    if not path or not os.path.isfile(path):
        return False, (
            f"{os.path.basename(path) or 'slicer-mcp-server.py'} was not found "
            f"(expected under {SKILL_MCP_SCRIPT}) — is the slicer-skill "
            "submodule checked out?"
        )
    try:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except Exception as exc:
        return False, f"Could not read {os.path.basename(path)}: {exc}"

    try:
        import sys
        main_globals = sys.modules["__main__"].__dict__
        # compile() with the real filename so any traceback points at the script.
        exec(compile(source, path, "exec"), main_globals)  # noqa: S102
    except Exception as exc:
        logger.warning("Auto-start of the skill MCP server failed", exc_info=True)
        return False, f"{type(exc).__name__}: {exc}"
    return True, path


# ---------------------------------------------------------------------------
# Bridge to the skill's own stand-alone server (the default transport)
# ---------------------------------------------------------------------------

class BaselineMCPBridge:
    """Attach to the ``slicer-mcp-server.py`` the user pasted into Slicer.

    The skill's documented setup is unchanged: register its MCP section in the
    Claude Code config, ``--add-dir`` the skill directory, and paste
    ``slicer-mcp-server.py`` into Slicer's Python console. That script defines
    ``TOOL_HANDLERS`` and ``mcpLogic`` in ``__main__``; this class finds them
    there.

    While ARMED, ``TOOL_HANDLERS["execute_python"]`` is replaced by a wrapper
    that hands the code to the baseline callback instead of ``exec``-ing it
    raw, and returns the callback's real stdout/stderr in the same content shape
    the original handler uses -- so Claude Code sees exactly what it would
    normally see and can iterate. Disarming restores the original handler.

    Every other tool (``list_nodes``, ``get_node_properties``, ``screenshot``,
    ``load_sample_data``) is left completely untouched, armed or not.
    """

    #: Port the shipped script uses; only a fallback for display when the live
    #: ``mcpLogic`` object cannot be read.
    DEFAULT_PORT = 2026

    _instance: Optional["BaselineMCPBridge"] = None

    def __init__(self):
        self._original: Optional[Callable] = None
        self._armed_callback: Optional[Callable[[str], Dict[str, Any]]] = None
        self._armed_label = ""
        self._lock = threading.Lock()
        self.last_error = ""

    @classmethod
    def instance(cls) -> "BaselineMCPBridge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # -- discovery ---------------------------------------------------------
    @staticmethod
    def _main_namespace() -> Dict[str, Any]:
        import sys
        try:
            return sys.modules["__main__"].__dict__
        except Exception:
            return {}

    def _handlers(self) -> Optional[Dict[str, Any]]:
        """The pasted server's tool-handler registry, or None if absent."""
        handlers = self._main_namespace().get("TOOL_HANDLERS")
        if isinstance(handlers, dict) and callable(handlers.get("execute_python")):
            return handlers
        return None

    @property
    def available(self) -> bool:
        return self._handlers() is not None

    @property
    def running(self) -> bool:
        """True when the pasted server is present. Nothing for us to start."""
        return self.available

    @property
    def armed(self) -> bool:
        return self._armed_callback is not None

    @property
    def port(self) -> int:
        logic = self._main_namespace().get("mcpLogic")
        try:
            return int(getattr(logic, "port", self.DEFAULT_PORT) or self.DEFAULT_PORT)
        except Exception:
            return self.DEFAULT_PORT

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}/mcp"

    @property
    def transport(self) -> str:
        """Identifier recorded with every run, so the transport is never implicit."""
        return "slicer-mcp-server.py (attached)"

    # No client_config_snippet here on purpose: the skill's own
    # slicer-mcp-server.py prints its MCP client config to the Python console
    # the moment it is pasted, so re-emitting it from this panel would be
    # duplicate, second-source-of-truth output.

    NOT_FOUND_MESSAGE = (
        "The Slicer skill's MCP server is not running in this Slicer session. "
        "Paste slicer-mcp-server.py (from the slicer-skill directory) into "
        "Slicer's Python console, then arm the baseline again."
    )

    def start(self) -> bool:
        """No-op: the user starts the skill's server themselves, by design."""
        if self.available:
            self.last_error = ""
            return True
        self.last_error = self.NOT_FOUND_MESSAGE
        return False

    # -- arming ------------------------------------------------------------
    def arm(self, callback: Callable[[str], Dict[str, Any]], label: str = "") -> bool:
        """Route the pasted server's ``execute_python`` to ``callback``."""
        handlers = self._handlers()
        if handlers is None:
            self.last_error = self.NOT_FOUND_MESSAGE
            return False

        current = handlers["execute_python"]
        if not getattr(current, "_slicer_ai_agent_bridge", False):
            # Only capture a genuine original, never our own wrapper -- otherwise
            # a re-arm would nest wrappers and disarm could never restore.
            self._original = current

        def _wrapped(args):
            handler = self._current_callback()
            if handler is None:
                original = self._original
                return original(args) if original else _tool_execute_python_raw(args)
            code = str((args or {}).get("code", "") or "")
            try:
                outcome = handler(code) or {}
            except Exception:
                logger.warning("Armed baseline callback raised", exc_info=True)
                return _text(f"Error:\n{traceback.format_exc()}")
            header = self._armed_label or "baseline step"
            lines = [("OK - executed for " if outcome.get("success") else "FAILED - executed for ")
                     + header + "."]
            if outcome.get("output"):
                lines.append(f"\nOutput:\n{outcome['output']}")
            if outcome.get("error"):
                lines.append(f"\nError:\n{outcome['error']}")
            if outcome.get("note"):
                lines.append(f"\n{outcome['note']}")
            return _text("\n".join(lines))

        _wrapped._slicer_ai_agent_bridge = True
        handlers["execute_python"] = _wrapped
        with self._lock:
            self._armed_callback = callback
            self._armed_label = label or ""
        self.last_error = ""
        logger.info("Baseline attached to the skill's MCP server at %s", self.url)
        return True

    def disarm(self) -> None:
        """Put the skill's own ``execute_python`` handler back."""
        with self._lock:
            self._armed_callback = None
            self._armed_label = ""
        handlers = self._handlers()
        original = self._original
        self._original = None
        if handlers is None or original is None:
            return
        # Only restore over OUR wrapper: if the user re-pasted the script the
        # registry is already fresh and putting a stale handler back would
        # silently undo their re-paste.
        if getattr(handlers.get("execute_python"), "_slicer_ai_agent_bridge", False):
            handlers["execute_python"] = original

    def stop(self) -> None:
        """Detach. The skill's server keeps running -- it is not ours to stop."""
        self.disarm()

    def _current_callback(self):
        with self._lock:
            return self._armed_callback

    def check_access(self) -> bool:
        """The pasted server owns its own consent dialog; nothing to add."""
        return True

    def reset_access(self) -> None:
        pass
