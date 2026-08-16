"""Runtime revision of ONE generated-CLI step template, from the surgeon's words.

A generated step can be *correct by every static check and still wrong*: it runs,
raises nothing, and puts the curve in the wrong view, reconstructs the wrong
side, or leaves a node the next step cannot find. Nothing in the pipeline can
detect that -- the only signal is a person looking at the scene. This module is
the machinery behind the ``✎`` button beside Send: while a guided workflow is
open, the user steps to the offending step, describes what should have happened,
and one step's ``.tpl`` is rewritten.

Three properties separate this from the "Function-level errors" box it replaces:

* **The step is pointed at, not guessed.** The old path took a sentence, asked an
  LLM which of 27 steps it meant, and repaired blind. Here the step is whatever
  the replay stepper is showing, so there is no classification to get wrong --
  and the revision can therefore be given that step's *filled* code, its last
  execution output and the live scene, which a whole-package repair cannot.
* **The TEMPLATE is rewritten, placeholders intact.** The runtime's own
  self-correction write-back (``_persistGeneratedTemplateRepair``) persists the
  *filled* code and so must refuse any template carrying a ``{placeholder}`` --
  freezing this run's ``{side}`` into the package would make every later run
  reconstruct whichever side this one happened to pick. A revision works on the
  template source, so it has no such limit; instead it is checked against the
  original's placeholder set (:func:`validate_revision`).
* **The pre-state is kept.** ``versions/revision_<ts>/`` is a snapshot taken
  BEFORE the write -- the same direction as ``versions/runtime_fix_<ts>/`` and
  deliberately NOT the ``repair_NNN`` convention, which archives the result. The
  round's request, reply, before/after text and unified diff land in
  ``debug/revision_<ts>/``, and every revision is indexed in
  ``debug/revisions.json`` so "what has this package been asked to do" is one
  file rather than a directory listing.

Everything here is Qt-free and Slicer-free: it resolves paths, reads and writes
text, builds message lists and checks the result. The LLM call, the scene read
and the re-run stay in ``app/widget_revise.py``, so a revision reuses the same
``chatWithToolsIsolated`` -> CodeValidator -> SafeExecutor path self-correction
uses. ``scripts/check_template_revision.py`` exercises this module outside
Slicer against every shipped package.
"""

from __future__ import annotations

import ast
import difflib
import json
import logging
import os
import re
import shutil
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

#: Version/debug round prefix. Distinct from ``repair_NNN`` on purpose: a
#: ``repair_NNN`` snapshot is the package AFTER that round, while this one — like
#: ``runtime_fix_<ts>`` — is the package BEFORE the write, i.e. the thing to
#: restore from. Mixing the two conventions under one prefix would make
#: ``versions/`` mean two opposite things.
REVISION_ROUND_PREFIX = "revision"

#: Cumulative index of every revision ever applied to a package. Lives under
#: ``debug/`` rather than at the package root because the root is the ACTIVE
#: package by exclusion (``cli_artifacts._PRESERVED_ENTRIES``) and is wiped by a
#: regeneration, while ``debug/`` is history and survives one.
REVISION_INDEX_NAME = "revisions.json"

#: The four fields of ``code_generators.json`` that can name a template, mapped
#: to the role the runtime dispatches them as. ``branch_action_template`` is read
#: from the workflow.json STEP as well, because that is where the loader looks
#: for it (``workflow_handlers._handle_branch_step``).
_GENERATOR_TEMPLATE_FIELDS = (
    ("template_file", "main"),
    ("pre_template_file", "pre"),
    ("post_template_file", "post"),
    ("branch_action_template", "branch_action"),
)

#: workflow.json mirrors the same paths under different names. Read as well as
#: the generators, and unioned, so a step whose generator entry is missing a
#: field still resolves — a template the runtime would dispatch and this module
#: could not see is exactly how a broken branch action once shipped as "all
#: probes passed".
_STEP_TEMPLATE_FIELDS = (
    ("code_template", "main"),
    ("pre_template", "pre"),
    ("post_template", "post"),
    ("branch_action_template", "branch_action"),
)

#: Ordering for display, so a pre/post pair always reads in dispatch order.
_ROLE_ORDER = {"main": 0, "pre": 1, "post": 2, "branch_action": 3}

_ROLE_LABELS = {
    "main": "the step's only template (runs when the step is dispatched)",
    "pre": "PRE template (runs when the step opens, before the user acts)",
    "post": "POST template (runs after the user clicks Done)",
    "branch_action": "branch action (runs only when the user answers yes)",
}


# --------------------------------------------------------------------------
# Placeholders
# --------------------------------------------------------------------------

#: A single-brace placeholder, ``{{...}}`` excluded. Same expression as
#: ``WidgetExecutionFlowMixin._templatePlaceholderNames``, deliberately: the two
#: answer the same question about the same files, and a template that one of them
#: reads as placeholder-free while the other does not would let a filled fix be
#: persisted over a parameterised template.
_PLACEHOLDER_RE = re.compile(
    r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)(?::[^{}]*)?\}(?!\})"
)

#: The same, restricted to the ``{name: default}`` form. A placeholder WITH a
#: default can never fail at dispatch, so it is the one kind a revision may
#: introduce.
_DEFAULTED_RE = re.compile(
    r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*):[^{}]*\}(?!\})"
)

#: Structural, not run-specific: it expands to the same scene lookup on every
#: run, so it is always available regardless of what the step recorded.
STRUCTURAL_PLACEHOLDERS = frozenset({"vol_lookup"})


def placeholder_names(text: str) -> set:
    """Every single-brace placeholder name in a template."""
    return set(_PLACEHOLDER_RE.findall(text or ""))


def defaulted_placeholder_names(text: str) -> set:
    """Placeholder names written as ``{name: default}`` (never fatal at dispatch)."""
    return set(_DEFAULTED_RE.findall(text or ""))


def fillable_placeholder_names(text: str) -> set:
    """The placeholders the loader will actually try to look up.

    ``placeholder_names`` is a raw brace scan, so it also matches every f-string
    interpolation in the file -- ``print(f"failed: {_module_enter_error}")`` is
    two braces and an identifier like any other. The loader never looks those up
    (they sit inside a string literal it masks), so they can never raise
    ``KeyError`` at dispatch and impose no closure requirement on a revision.

    Not a detail: without this, adding an ordinary f-string to a template would
    read as "introduces a placeholder the runtime cannot fill" and a correct
    revision would be refused. Closure must be measured over what the filler
    LOOKS UP, not over what looks like a brace.
    """
    return placeholder_names(text) - surviving_placeholder_names(text)


def sample_fill(text: str) -> str:
    """Fill every placeholder with a syntactically valid stand-in.

    Used ONLY to make a template parseable so it can be syntax- and
    security-checked; it is never executed and never written. The values are
    deliberately not the run's real ones — what is being checked is the code the
    model wrote, not the data it will see.

    ``{vol_lookup}`` is substituted with an assignment rather than with the
    loader's real snippet: it is emitted at column 0 as a statement, an
    assignment is a statement, and reproducing the loader's snippet here would
    be a second copy of it to keep in step.
    """
    def _replace(match):
        name = match.group(1)
        if name in STRUCTURAL_PLACEHOLDERS:
            return "inputVolume = None"
        # The runtime repr()-wraps every substituted value, so a quoted literal
        # is the shape a template is written against.
        return "'__sample__'"

    return _PLACEHOLDER_RE.sub(_replace, text or "")


# --------------------------------------------------------------------------
# Targets
# --------------------------------------------------------------------------

class TemplateTarget(object):
    """One template file belonging to a step."""

    __slots__ = ("role", "rel_path", "abs_path", "text")

    def __init__(self, role, rel_path, abs_path, text):
        self.role = role
        self.rel_path = rel_path
        self.abs_path = abs_path
        self.text = text

    @property
    def role_label(self):
        return _ROLE_LABELS.get(self.role, self.role)

    def to_dict(self):
        return {
            "role": self.role,
            "rel_path": self.rel_path,
            "chars": len(self.text or ""),
            "placeholders": sorted(placeholder_names(self.text)),
        }

    def __repr__(self):  # pragma: no cover - debugging aid
        return "<TemplateTarget %s %s>" % (self.role, self.rel_path)


class ReviseTarget(object):
    """A step and every template file the runtime would dispatch for it."""

    __slots__ = (
        "extension", "cli_dir", "step_id", "operation_type", "description",
        "templates",
    )

    def __init__(self, extension, cli_dir, step_id, operation_type,
                 description, templates):
        self.extension = extension
        self.cli_dir = cli_dir
        self.step_id = step_id
        self.operation_type = operation_type
        self.description = description
        self.templates = templates

    @property
    def rel_paths(self):
        return [tpl.rel_path for tpl in self.templates]

    def template_for(self, rel_path):
        for tpl in self.templates:
            if tpl.rel_path == rel_path:
                return tpl
        return None

    def to_dict(self):
        return {
            "extension": self.extension,
            "step_id": self.step_id,
            "operation_type": self.operation_type,
            "templates": [tpl.to_dict() for tpl in self.templates],
        }


def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def step_template_paths(cli_dir: str, step_id: str) -> List[Tuple[str, str]]:
    """Every ``(role, relative path)`` the runtime could dispatch for a step.

    Unions ``code_generators.json`` (what the automated/interactive handlers
    read) with the step's own entry in ``workflow.json`` (where the branch action
    lives). Order is dispatch order, and duplicates are dropped keeping the first
    role seen, so a field present in both files is listed once.
    """
    found = []
    seen = set()

    generators = _read_json(os.path.join(cli_dir, "code_generators.json"), [])
    for gen in generators if isinstance(generators, list) else []:
        if not isinstance(gen, dict):
            continue
        if (gen.get("param_signature") or {}).get("workflow_step") != step_id:
            continue
        for field, role in _GENERATOR_TEMPLATE_FIELDS:
            rel = (gen.get(field) or "").strip()
            if rel and rel not in seen:
                seen.add(rel)
                found.append((role, rel))

    graph = _read_json(os.path.join(cli_dir, "workflow.json"), {})
    for step in (graph.get("steps") or []) if isinstance(graph, dict) else []:
        if not isinstance(step, dict) or step.get("step_id") != step_id:
            continue
        for field, role in _STEP_TEMPLATE_FIELDS:
            rel = (step.get(field) or "").strip()
            if rel and rel not in seen:
                seen.add(rel)
                found.append((role, rel))

    found.sort(key=lambda entry: _ROLE_ORDER.get(entry[0], 9))
    return found


def step_meta(cli_dir: str, step_id: str) -> Dict[str, Any]:
    """The step's entry from ``workflow.json``, or ``{}``."""
    graph = _read_json(os.path.join(cli_dir, "workflow.json"), {})
    for step in (graph.get("steps") or []) if isinstance(graph, dict) else []:
        if isinstance(step, dict) and step.get("step_id") == step_id:
            return step
    return {}


def resolve_target(cli_dir: str, extension: str, step_id: str) -> Optional[ReviseTarget]:
    """Build a :class:`ReviseTarget`, or ``None`` when the step has no template.

    A step with no template on disk cannot be revised — ``user_choice``,
    ``review_op`` and most ``branch_op`` steps have none by construction, and for
    those the thing the user wants changed is the *panel*, not code.
    """
    if not cli_dir or not os.path.isdir(cli_dir) or not step_id:
        return None

    meta = step_meta(cli_dir, step_id)
    templates = []
    for role, rel in step_template_paths(cli_dir, step_id):
        abs_path = os.path.join(cli_dir, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            # Named but absent: the package and its generators disagree. Skip it
            # rather than inventing the file — writing a template the runtime
            # never reads would look like a fix and change nothing.
            logger.debug("Revise target names a missing template: %s", abs_path)
            continue
        try:
            with open(abs_path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except Exception:
            logger.debug("Revise target unreadable: %s", abs_path, exc_info=True)
            continue
        templates.append(TemplateTarget(role, rel, abs_path, text))

    if not templates:
        return None

    return ReviseTarget(
        extension=extension,
        cli_dir=cli_dir,
        step_id=step_id,
        operation_type=str(meta.get("operation_type", "") or ""),
        description=str(meta.get("description", "") or ""),
        templates=templates,
    )


def revise_eligibility(cli_dir: str, step_id: str) -> Tuple[bool, str]:
    """``(ok, reason)`` — whether this step has code a revision could rewrite."""
    if not step_id:
        return False, "No step is selected."
    if not cli_dir or not os.path.isdir(cli_dir):
        return False, "This procedure has no generated CLI package on disk."
    paths = step_template_paths(cli_dir, step_id)
    if not paths:
        meta = step_meta(cli_dir, step_id)
        op_type = str(meta.get("operation_type", "") or "this step")
        return False, (
            "%s runs no generated code — there is no template to revise. "
            "Step back to a step that does." % op_type
        )
    missing = [rel for _role, rel in paths
               if not os.path.isfile(os.path.join(cli_dir, rel.replace("/", os.sep)))]
    if len(missing) == len(paths):
        return False, "This step's template file is missing from the package."
    return True, ""


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

class RevisionCheck(object):
    """Outcome of checking one rewritten template."""

    __slots__ = ("rel_path", "errors", "warnings")

    def __init__(self, rel_path, errors=None, warnings=None):
        self.rel_path = rel_path
        self.errors = list(errors or [])
        self.warnings = list(warnings or [])

    @property
    def ok(self):
        return not self.errors

    def to_dict(self):
        return {"rel_path": self.rel_path, "errors": self.errors,
                "warnings": self.warnings}


#: The string-literal mask ``extension_cli_loader.templates._fill_template``
#: applies before it scans for placeholders. Reproduced here EXACTLY -- same
#: pattern, same flags -- because the check below asks a question only the real
#: algorithm can answer: does this template still fill?
#:
#: It is a raw regex over the whole file rather than a tokenizer, so a quote
#: character that Python would read as ordinary text (an apostrophe in a prose
#: comment) still opens a span, and the span runs to the next quote character
#: anywhere in the file. Any ``{placeholder}`` caught inside is emitted RAW, the
#: step then executes ``{side}`` -- valid Python, a set literal -- and the result
#: is a NameError or, worse, a silently wrong value. Nothing raises at fill time,
#: which is what makes it worth checking rather than merely documenting.
_FILLER_STRING_MASK_RE = re.compile(
    r'(?:[fFrRbBuU]{0,2})("""|\'\'\'|"|\')(.*?)\1', re.DOTALL
)


def unfillable_placeholders(text: str) -> list:
    """Placeholders that would still be ``{name}`` after the loader filled them.

    Empty for a healthy template. Non-empty means the template carries a
    ``{name}`` that reaches the executor as literal text -- valid Python (a set
    literal), so it raises a NameError at best and silently uses the wrong value
    at worst.

    Answered by RUNNING the loader's own ``_fill_template`` against sample values
    and looking for survivors, not by re-deriving its rules. A copy would have to
    reproduce both the mask regex and its containment test (the filler checks
    only where a placeholder BEGINS, and it walks a buffer in which every ``{{``
    has already been swapped for a longer sentinel, shifting its own offsets),
    and a copy that drifted would answer confidently about a slightly different
    string than the one the loader processes.

    The regex path below is the fallback for a stand-alone import, where the
    loader package is not importable. It is deliberately the conservative half
    of the question.

    An f-string interpolation is NOT reported. Both it and a trapped placeholder
    are ``{name}`` spans the filler leaves alone, but the filler is RIGHT about
    the f-string: ``print(f"failed: {_module_enter_error}")`` in
    BoneReconstructionPlanner/cb_step_1 is Python, and every generated template
    reports its errors that way. The two are separated by asking PYTHON, not a
    regex: a survivor sitting inside a real STRING token is an interpolation, a
    survivor outside one is trapped by the mask. Without that split, "the model
    added an f-string" and "the model broke placeholder filling" would be the
    same verdict, and the common case is the innocent one.
    """
    return _survivors(text)[1]


def surviving_placeholder_names(text: str) -> set:
    """Every ``{name}`` the loader leaves untouched — interpolations included.

    The complement of :func:`fillable_placeholder_names`. Both kinds of survivor
    belong here, because closure is about what the filler LOOKS UP and it looks
    up neither.
    """
    return _survivors(text)[0]


def _survivors(text):
    """``(all survivors, trapped survivors)`` for one template.

    A *survivor* is a ``{name}`` still present after the loader filled the
    template. It is *trapped* when it is a survivor that Python does not consider
    part of a string literal — i.e. the mask swallowed it by accident rather than
    because it is an f-string interpolation.
    """
    text = text or ""
    names = placeholder_names(text)
    if not names:
        return set(), []

    scan_text, mask_spans = text, None
    try:
        from .extension_cli_loader.templates import _fill_template
        scan_text = _fill_template(
            text, {name: "'__sample__'" for name in names})
    except Exception:
        # No loader package (a stand-alone import), or the filler refused. Fall
        # back to its mask, which is the conservative half of the question. The
        # filler tests only where a placeholder BEGINS (`_in_string(pos)` is
        # `s <= pos < e`), so this must too.
        logger.debug("Revision fill probe unavailable", exc_info=True)
        mask_spans = [(match.start(), match.end())
                      for match in _FILLER_STRING_MASK_RE.finditer(text)]

    strings = _real_string_spans(scan_text)
    all_survivors, trapped = set(), set()
    for match in _PLACEHOLDER_RE.finditer(scan_text):
        name = match.group(1)
        if name not in names:
            continue
        start = match.start()
        if mask_spans is not None and not any(
                s <= start < e for s, e in mask_spans):
            continue
        all_survivors.add(name)
        if strings is not None and any(s <= start < e for s, e in strings):
            continue  # an f-string interpolation: Python's, not the filler's
        trapped.add(name)
    return all_survivors, sorted(trapped)


def _real_string_spans(text):
    """Absolute offsets of every Python STRING token, or ``None`` if untokenizable.

    ``None`` means "cannot tell", and every caller then falls back to treating
    survivors as trapped -- the safe direction, because the verdict is always a
    delta against the original and a template that does not tokenize would fail
    the syntax gate anyway.
    """
    import io
    import tokenize

    line_starts = [0]
    for line in text.splitlines(keepends=True):
        line_starts.append(line_starts[-1] + len(line))

    def offset(position):
        row, col = position
        if row - 1 >= len(line_starts):
            return line_starts[-1]
        return line_starts[row - 1] + col

    spans = []
    # Python 3.12 splits an f-string into FSTRING_START/MIDDLE/END around real
    # tokens, so the interpolation is no longer inside a STRING token. Track the
    # whole f-string as one span there. Slicer 5.x ships 3.9, where it is a
    # single STRING token; both are handled so this does not depend on which
    # interpreter the check script runs under.
    fstring_start = getattr(tokenize, "FSTRING_START", None)
    fstring_end = getattr(tokenize, "FSTRING_END", None)
    open_fstring = None
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.STRING:
                spans.append((offset(token.start), offset(token.end)))
            elif fstring_start is not None and token.type == fstring_start:
                open_fstring = offset(token.start)
            elif (fstring_end is not None and token.type == fstring_end
                  and open_fstring is not None):
                spans.append((open_fstring, offset(token.end)))
                open_fstring = None
    except Exception:
        return None
    return spans


def validate_revision(original_text: str, new_text: str,
                      code_validator=None,
                      rel_path: str = "") -> RevisionCheck:
    """Check a rewritten template before it is allowed near the package.

    Five gates, in the order a failure would bite:

    1. **Non-empty and changed.** An empty answer would delete the step's code;
       an identical one is reported so the user is not told a fix was applied
       when nothing moved.
    2. **Placeholder closure.** A revision may DROP a placeholder (inlining a
       value the user asked to pin is a legitimate fix) and may add one that
       carries a default, but it may never introduce a bare ``{name}`` the
       original did not have. The original demonstrably fills at dispatch, so its
       placeholder set *is* the set the runtime can supply for this step; a new
       one raises ``KeyError`` inside the loader, which surfaces as a step that
       silently never executes rather than as an error anyone reads.
    3. **Syntax.** Parsed after :func:`sample_fill`, because a template is not
       valid Python until its placeholders are substituted.
    4. **Security.** The same ``CodeValidator`` the runtime runs before
       execution, so a revision cannot ship code the executor would refuse.
    5. **The apostrophe mask.** Two quote characters make the filler treat
       everything between them as a string literal, so a placeholder caught in
       the span is emitted raw. A warning when the original was already like
       that, an error when the revision made it so.
    """
    check = RevisionCheck(rel_path)
    new_text = new_text or ""
    original_text = original_text or ""

    if not new_text.strip():
        check.errors.append("The rewritten template is empty.")
        return check
    if new_text.strip() == original_text.strip():
        check.warnings.append("The rewritten template is identical to the original.")

    original_names = fillable_placeholder_names(original_text)
    new_names = fillable_placeholder_names(new_text)
    safe_names = original_names | STRUCTURAL_PLACEHOLDERS
    introduced = sorted(new_names - safe_names)
    if introduced:
        # The defaulted form is NOT an escape hatch here, and the reason is that
        # `{name: default}` and a dict literal `{name: value}` are the same six
        # characters. The filler cannot tell them apart -- it replaces the whole
        # brace span with the default -- so `d = {key: 1}` silently becomes
        # `d = 1`. Refusing both readings with one message is the only rule that
        # is not a coin flip: a genuinely new value has no business being written
        # as a placeholder anyway (nothing can ever fill it, so it is a constant
        # in disguise), and a dict needs `dict(...)` or a quoted key.
        check.errors.append(
            "Introduces {%s}, which the runtime cannot fill for this step — only "
            "%s are available here. If you meant a constant, write the value "
            "directly. If you meant a dict, write dict(key=value) or quote the "
            "key: the template filler reads {name: value} as a placeholder with "
            "a default and replaces the whole thing with `value`."
            % ("}, {".join(introduced),
               ", ".join("{%s}" % name for name in sorted(safe_names)) or "none")
        )
    dropped = sorted(original_names - new_names - STRUCTURAL_PLACEHOLDERS)
    if dropped:
        check.warnings.append(
            "No longer uses %s — the value the user chose for it will not reach "
            "this step." % ", ".join("{%s}" % name for name in dropped)
        )

    filled = sample_fill(new_text)
    try:
        ast.parse(filled)
    except SyntaxError as exc:
        check.errors.append(
            "The template is not valid Python once its placeholders are filled: "
            "%s (line %s)." % (exc.msg, exc.lineno)
        )
        # No point running the validator on something that does not parse.
        return check

    if code_validator is not None:
        try:
            verdict = code_validator.validate(filled)
        except Exception as exc:  # pragma: no cover - validator is pure
            logger.debug("Revision CodeValidator call failed", exc_info=True)
            verdict = {"valid": True, "reason": str(exc)}
        if not verdict.get("valid", True):
            check.errors.append(
                "Rejected by the code validator: %s" % verdict.get("reason", "?")
            )

    _check_filler_hazards(original_text, new_text, check)
    return check


def _check_filler_hazards(original_text: str, new_text: str, check: RevisionCheck):
    """Run the filler's own string mask and see whether a placeholder survives.

    Deliberately not a proxy such as "counts more than one apostrophe": a
    correctly closed ``'Foo'`` is masked and SHOULD be, and refusing every
    revision that adds a single-quoted string would reject most correct answers.
    What matters is only whether a ``{placeholder}`` ends up inside a masked
    span -- which is exactly what :func:`unfillable_placeholders` measures.
    """
    swallowed_now = set(unfillable_placeholders(new_text))
    if not swallowed_now:
        return
    swallowed_before = set(unfillable_placeholders(original_text))
    introduced = swallowed_now - swallowed_before
    if not introduced:
        # Present in the original too, so it is almost certainly an f-string
        # interpolation the filler is right to leave alone -- and if it is a
        # genuine pre-existing trap, it is not this revision's doing and saying
        # so on every revision of every template would be pure noise.
        return
    check.errors.append(
        "%s would never be filled: the template filler masks everything between "
        "two quote characters as a string literal, and %s falls inside such a "
        "span. An apostrophe in a comment is the usual cause — it opens a span "
        "that runs to the next quote anywhere in the file. The step would "
        "execute a raw {name}."
        % (", ".join("{%s}" % name for name in sorted(introduced)),
           "it" if len(introduced) == 1 else "one of them")
    )


# --------------------------------------------------------------------------
# Prompt
# --------------------------------------------------------------------------

#: The revision agent's instructions. Like every other prompt in this project it
#: is a file, not a Python literal, so it can be edited, diffed and cited without
#: touching code (Resources/Prompts/README.md). The name is duplicated from
#: PromptLibrary only so this module keeps working when it is imported
#: stand-alone by scripts/check_template_revision.py.
TEMPLATE_REVISION_PROMPT = "template_revision_prompt.md"

#: Last-resort text for a missing prompt file. Not a second copy of the prompt —
#: it exists so a missing file degrades to something safe rather than to an empty
#: system message, and it keeps the two rules that make a wrong answer
#: unrecoverable: the placeholders and the output contract.
_REVISION_FALLBACK = (
    "You revise ONE step's code template for a 3D Slicer guided workflow. "
    "Rewrite the template so it does what the user describes, changing as "
    "little as possible. Keep every {placeholder} exactly as it is — they are "
    "filled at dispatch with the values the user chose, and the substituted "
    "value is already a Python literal, so write f({side}) and never "
    "f('{side}'). Do not introduce a placeholder the original did not have. "
    "Verify every API you call against the extension source before using it. "
    "Reply with ONE JSON object: {\"analysis\": \"...\", \"summary\": \"...\", "
    "\"templates\": {\"<relative path>\": \"<complete new template>\"}}."
)


def revision_system_prompt(blocked_modules="", blocked_functions="",
                           allowed_modules="", source_roots="") -> str:
    """Render the revision agent's system prompt.

    The validator's three lists are rendered in rather than restated by hand:
    a prompt that describes a blocked list which has since changed teaches the
    model a rule the executor does not enforce, and the failure shows up as a
    rejected revision the user cannot explain.
    """
    try:
        from . import PromptLibrary
        return PromptLibrary.render(
            TEMPLATE_REVISION_PROMPT,
            fallback=_REVISION_FALLBACK,
            blocked_modules=blocked_modules,
            blocked_functions=blocked_functions,
            allowed_modules=allowed_modules,
            extension_source_roots=source_roots,
        )
    except Exception:
        logger.debug("Revision prompt load failed", exc_info=True)
        return _REVISION_FALLBACK


def _section(title, body):
    body = (body or "").strip()
    if not body:
        return ""
    return "## %s\n%s\n" % (title, body)


def _fence(text, language="python"):
    return "```%s\n%s\n```" % (language, (text or "").rstrip("\n"))


def build_case_message(target: ReviseTarget, request: str,
                       context: Optional[Dict[str, Any]] = None) -> str:
    """The user half: everything about THIS step, and nothing about any other.

    Deliberately generous, because the whole advantage of revising at runtime is
    that the evidence exists: the template as it stands, the code that was
    actually dispatched (template + prelude, placeholders filled with this run's
    real values), what that code printed or raised, the live scene, the answers
    the user already gave, and what previous revisions of this step did. A
    whole-package repair has none of that.
    """
    context = context or {}
    parts = [
        "# Revision request",
        (request or "").strip() or "(no request text)",
        "",
        "# The step this is about",
        "- extension: %s" % target.extension,
        "- step_id: %s" % target.step_id,
        "- operation_type: %s" % (target.operation_type or "unknown"),
    ]
    position = context.get("position")
    if position:
        parts.append("- position: %s" % position)
    parts.append("")

    blocks = [
        _section("What the procedure says this step does", target.description),
        _section("What the panel tells the surgeon", context.get("step_brief")),
        _section("Answers the user already gave in this run", context.get("choices")),
        _section("Steps already completed", context.get("completed")),
        _section("Previous revisions of this step (do not undo them)",
                 context.get("history")),
    ]

    tpl_lines = []
    for tpl in target.templates:
        tpl_lines.append("### %s — %s" % (tpl.rel_path, tpl.role_label))
        names = sorted(placeholder_names(tpl.text))
        if names:
            fills = context.get("fill_values") or {}
            described = []
            for name in names:
                value = fills.get(name)
                described.append(
                    "  - {%s} -> %s" % (name, value if value else "(filled at dispatch)")
                )
            tpl_lines.append("Placeholders in this template, and what this run "
                             "fills them with:\n" + "\n".join(described))
        else:
            tpl_lines.append("This template has no placeholders.")
        tpl_lines.append(_fence(tpl.text))
        tpl_lines.append("")
    blocks.append(_section("The template(s) to revise", "\n".join(tpl_lines)))

    dispatched = context.get("dispatched_code")
    if dispatched:
        blocks.append(_section(
            "The code that actually ran last time (template filled, plus the "
            "runtime prelude the loader prepends — the prelude is NOT part of "
            "the template and must not be reproduced in your answer)",
            _fence(dispatched)))
    blocks.append(_section("What that run produced", context.get("execution")))
    blocks.append(_section("The live scene right now", context.get("scene")))

    parts.append("\n".join(block for block in blocks if block))
    parts.append(
        "# Your answer\n"
        "Rewrite ONLY the template(s) listed above, in full, and return the "
        "JSON object described in your instructions. Change as little as the "
        "request allows."
    )
    return "\n".join(parts)


def build_messages(target: ReviseTarget, request: str,
                   context: Optional[Dict[str, Any]] = None,
                   system_prompt: str = "") -> List[Dict[str, str]]:
    """``[system, user]`` for the revision agent's first round."""
    return [
        {"role": "system", "content": system_prompt or revision_system_prompt()},
        {"role": "user", "content": build_case_message(target, request, context)},
    ]


def build_retry_message(checks: Sequence[RevisionCheck],
                        parsed: Optional[ParsedRevision] = None) -> str:
    """The follow-up round: hand the model its own rejection, verbatim.

    This is the loop that makes the feature agentic rather than one-shot. The
    checks are deterministic (placeholder closure, syntax, the validator), so the
    message is evidence rather than an opinion, and a model that cannot satisfy
    them in :data:`MAX_ROUNDS` rounds is telling us the request needs a human.
    """
    lines = ["Your rewritten template was rejected. Fix these and return the "
             "complete template again, in the same JSON shape."]
    if parsed is not None and parsed.error:
        lines.append("- %s" % parsed.error)
    for check in checks or []:
        for error in check.errors:
            lines.append("- %s: %s" % (check.rel_path or "template", error))
    lines.append(
        "Do not narrow the fix to satisfy the check — if a rule blocks the only "
        "correct fix, say so in \"blocked\" instead of shipping something that "
        "passes and does the wrong thing."
    )
    return "\n".join(lines)


#: How many validate -> retry cycles a revision gets. Three, matching the shape
#: of the generation repair ladder: one to answer, one to fix a mechanical
#: rejection, one to fix a consequence of that fix. Beyond that the model is
#: guessing, and a guess that reaches a surgical template is worse than a
#: refusal the user can read.
MAX_ROUNDS = 3

#: Search rounds inside ONE revision call. Higher than self-correction's 5,
#: because a revision that must derive an API from the extension source is doing
#: the same job the online-only baseline is given 16 rounds for, and cutting it
#: off mid-search measures the budget instead of the approach.
TOOL_ROUNDS = 12


# --------------------------------------------------------------------------
# Reply parsing
# --------------------------------------------------------------------------

class ParsedRevision(object):
    """What the model returned, normalised."""

    __slots__ = ("templates", "summary", "analysis", "blocked", "error")

    def __init__(self, templates=None, summary="", analysis="", blocked="",
                 error=""):
        self.templates = dict(templates or {})
        self.summary = summary
        self.analysis = analysis
        self.blocked = blocked
        self.error = error

    @property
    def ok(self):
        return bool(self.templates) and not self.error and not self.blocked


_FENCE_RE = re.compile(
    r"```(?:[A-Za-z0-9_+-]*)\s*\n(.*?)```", re.DOTALL
)
_FILE_MARKER_RE = re.compile(
    r"^[#\s>*]*FILE\s*:\s*(?P<path>[^\s`]+)\s*$", re.MULTILINE | re.IGNORECASE
)


def parse_reply(reply: str, known_rel_paths: Sequence[str]) -> ParsedRevision:
    """Recover ``{rel_path: new template text}`` from the model's answer.

    Three accepted shapes, tried in order, because a model asked to return
    several hundred lines of Python inside JSON will sometimes decline to:

    1. A JSON object (bare or fenced) with a ``templates`` map — the contract the
       prompt asks for.
    2. ``FILE: <path>`` followed by a fenced block, one pair per template.
    3. A single fenced block, accepted ONLY when the step has exactly one
       template, so there is nothing to mis-assign.

    A path the step does not own is dropped rather than written: the revision is
    scoped to one step, and a model that decides to also fix step 14 must not be
    able to.
    """
    reply = reply or ""
    known = list(known_rel_paths or [])
    if not reply.strip():
        return ParsedRevision(error="The revision agent returned nothing.")

    parsed = _parse_json_shape(reply, known)
    if parsed is not None:
        return parsed

    templates = _parse_file_marker_shape(reply, known)
    if templates:
        return ParsedRevision(templates=templates,
                              summary=_leading_prose(reply))

    # A JSON object that parsed but carried no usable templates map is a
    # CORRECTABLE mistake -- a renamed key, a path for another step -- and must
    # be reported as one. Falling through to the single-block shape below would
    # install the JSON document ITSELF as the template, and nothing downstream
    # would catch it: a JSON object is a valid Python dict-literal expression, so
    # it parses, contains no import or call for the validator to refuse, and has
    # no placeholders to be closed against. The step would then execute a dict
    # literal -- raising nothing, printing nothing, doing nothing. The one
    # feature whose job is to fix silently-wrong steps would have manufactured
    # one.
    stray = _json_object_keys(reply)
    if stray is not None:
        return ParsedRevision(error=(
            "The reply is a JSON object with no usable \"templates\" map (it has: "
            "%s). Return {\"templates\": {\"<one of %s>\": \"<complete file>\"}}."
            % (", ".join(stray) or "no keys", ", ".join(known) or "the step's templates")
        ))

    blocks = _FENCE_RE.findall(reply)
    if len(known) == 1 and len(blocks) == 1:
        return ParsedRevision(templates={known[0]: _dedent_block(blocks[0])},
                              summary=_leading_prose(reply))

    if len(blocks) > 1 and len(known) == 1:
        return ParsedRevision(error=(
            "The reply contains %d code blocks but the step has one template; "
            "it is ambiguous which one to install." % len(blocks)
        ))
    return ParsedRevision(error=(
        "Could not find a rewritten template in the reply. Expected a JSON "
        "object with a \"templates\" map."
    ))


def _parse_json_shape(reply, known):
    for candidate in _json_candidates(reply):
        try:
            payload = json.loads(candidate)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        blocked = str(payload.get("blocked") or "").strip()
        raw = payload.get("templates")
        templates = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                rel = _match_known_path(str(key), known)
                if rel and isinstance(value, str):
                    templates[rel] = value
        if templates or blocked:
            return ParsedRevision(
                templates=templates,
                summary=str(payload.get("summary") or "").strip(),
                analysis=str(payload.get("analysis") or "").strip(),
                blocked=blocked,
            )
    return None


def _json_object_keys(reply):
    """Top-level keys of the reply's JSON object, or ``None`` if it is not one.

    Used only to tell "the model answered in JSON and got a key wrong" apart from
    "the model answered in prose or code", because those two need opposite
    handling and only the first is worth another round.
    """
    for candidate in _json_candidates(reply):
        try:
            payload = json.loads(candidate)
        except Exception:
            continue
        if isinstance(payload, dict):
            return sorted(str(key) for key in payload)
    return None


def _json_candidates(reply):
    """The whole reply, then each fenced block, then the outermost {...} span."""
    yield reply.strip()
    for block in _FENCE_RE.findall(reply):
        yield block.strip()
    start = reply.find("{")
    end = reply.rfind("}")
    if start >= 0 and end > start:
        yield reply[start:end + 1]


def _parse_file_marker_shape(reply, known):
    templates = {}
    for match in _FILE_MARKER_RE.finditer(reply):
        rel = _match_known_path(match.group("path"), known)
        if not rel:
            continue
        fence = _FENCE_RE.search(reply, match.end())
        if fence is None:
            continue
        templates[rel] = _dedent_block(fence.group(1))
    return templates


def _match_known_path(candidate, known):
    """Resolve a model-written path to one this step owns, or ``None``."""
    candidate = (candidate or "").strip().strip("`\"'").replace("\\", "/")
    if not candidate:
        return None
    for rel in known:
        if candidate == rel:
            return rel
    tail = candidate.rsplit("/", 1)[-1]
    for rel in known:
        if tail == rel.rsplit("/", 1)[-1]:
            return rel
    return None


def _dedent_block(text):
    text = (text or "").replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def _leading_prose(reply, limit=400):
    head = (reply or "").split("```", 1)[0].strip()
    return head[:limit]


# --------------------------------------------------------------------------
# Applying
# --------------------------------------------------------------------------

def round_label(stamp: Optional[str] = None) -> str:
    """``revision_<YYYYmmdd_HHMMSS>`` — the label for one applied revision."""
    return "%s_%s" % (REVISION_ROUND_PREFIX, stamp or time.strftime("%Y%m%d_%H%M%S"))


def _header_safe(text, limit=300):
    """Collapse to one line and REMOVE every quote character.

    The surgeon's own sentence and the model's summary are written into a
    comment at the top of an executable template, and the template filler's
    string mask is a regex, not a tokenizer: a single apostrophe in "shouldn't"
    opens a span that runs to the next quote anywhere in the file and swallows
    whatever ``{placeholder}`` lies between. That is the same defect the
    validator refuses in the model's own output -- it must not enter through the
    header instead. Stripped rather than escaped, because the header is prose for
    a human and a backslash in it would read as noise.
    """
    collapsed = " ".join(str(text or "").split())
    return collapsed.replace("'", "").replace('"', "")[:limit]


def _revision_header(label, request, summary):
    """The comment block prepended to every rewritten template.

    Names the backup, because a template that says where its predecessor went is
    recoverable by whoever opens it; the alternative is knowing to look in
    ``debug/revisions.json``.
    """
    lines = [
        "# [revised] Rewritten by the runtime revision agent (%s)." % label,
        "# Pre-revision package backed up under versions/%s/." % label,
    ]
    request_line = _header_safe(request)
    if request_line:
        lines.append("# Requested: %s" % request_line)
    summary_line = _header_safe(summary)
    if summary_line:
        lines.append("# Change: %s" % summary_line)
    return "\n".join(lines) + "\n"


#: A previous header, and ONLY a previous header. The continuation lines are
#: enumerated rather than matched as "any comment line", because a template's
#: first real content is often itself a comment: the
#: ``# precondition:begin … # precondition:end`` block sits at the top of every
#: step that enters a module, and eating it would silently remove the runtime's
#: only marker for firing the extension's ``enter()``. The model is shown the
#: template WITH its header, so it does reproduce one, and a greedy strip would
#: have taken the precondition block with it on the second revision of a step.
_HEADER_START_RE = re.compile(r"^# \[(?:revised|runtime-fixed)\][^\n]*\n")
_HEADER_CONT_PREFIXES = (
    "# Pre-revision",
    "# Requested:",
    "# Change:",
    "# Fixed runtime error:",
)


def _strip_previous_header(text):
    """Drop a previous revision header so they do not stack up one per round."""
    text = text or ""
    match = _HEADER_START_RE.match(text)
    if not match:
        return text
    rest = text[match.end():]
    while True:
        line, sep, remainder = rest.partition("\n")
        if sep and line.startswith(_HEADER_CONT_PREFIXES):
            rest = remainder
            continue
        return rest


def apply_revision(target: ReviseTarget,
                   revisions: Dict[str, str],
                   request: str,
                   summary: str = "",
                   analysis: str = "",
                   checks: Optional[Sequence[RevisionCheck]] = None,
                   messages: Optional[Sequence[Dict[str, Any]]] = None,
                   reply: str = "",
                   rounds: int = 1,
                   stamp: Optional[str] = None) -> Dict[str, Any]:
    """Back up the package, write the rewritten templates, record what happened.

    Returns a record dict (also written to ``debug/<label>/revision.json`` and
    appended to ``debug/revisions.json``). ``applied`` is the list of relative
    paths actually written; it is empty and ``error`` is set when the pre-write
    backup could not be taken — a revision that cannot be undone is not applied,
    because the whole promise of this path is that the original is kept.

    The loader cache is deliberately NOT invalidated. Template CONTENT is read
    fresh from disk on every dispatch (``workflow_handlers`` opens the file each
    time), so the next "Run from here" already picks the new text up; and
    ``invalidate_cache()`` mid-run re-reads every manifest, which drops any
    package that fails the status gate — including, potentially, the one the
    surgeon is standing in.
    """
    label = round_label(stamp)
    record = {
        "label": label,
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "extension": target.extension,
        "step_id": target.step_id,
        "operation_type": target.operation_type,
        "request": request,
        "summary": summary,
        "analysis": analysis,
        "rounds": rounds,
        "applied": [],
        "backup": "",
        "error": "",
        "templates": [],
    }

    # Only templates whose BODY actually changed. The agent is asked for the
    # complete file for every template of the step, so it routinely returns the
    # one it did not touch verbatim -- rewriting that file would stamp a header
    # on it, put it in the diff, and tell the user step 13's post template was
    # "revised" when nothing about it moved. Compared after stripping both
    # headers, so a re-revision does not read as a change either.
    writable, unchanged = {}, []
    for rel, text in (revisions or {}).items():
        tpl = target.template_for(rel)
        if tpl is None or not (text or "").strip():
            continue
        if _strip_previous_header(text).strip() == _strip_previous_header(tpl.text).strip():
            unchanged.append(rel)
            continue
        writable[rel] = text
    record["unchanged"] = unchanged
    if not writable:
        record["error"] = (
            "The revision agent returned %s unchanged — nothing was written."
            % (", ".join(unchanged) if unchanged else "no template")
        )
        return record

    backup = _snapshot_package(target.cli_dir, label)
    if not backup:
        # cli_artifacts fails SILENTLY (it has no logger and returns None), so
        # the return value is the only evidence the backup happened. Refusing
        # here is the point: "the original is saved" must not be a claim made on
        # a call whose result was never checked.
        record["error"] = (
            "Could not back the package up under versions/%s/ — nothing was "
            "written." % label
        )
        return record
    record["backup"] = "versions/%s" % label

    debug_dir = os.path.join(target.cli_dir, "debug", label)
    try:
        os.makedirs(debug_dir, exist_ok=True)
    except Exception:
        logger.debug("Revision debug dir failed: %s", debug_dir, exc_info=True)
        debug_dir = ""

    header = _revision_header(label, request, summary)
    for rel, new_text in sorted(writable.items()):
        tpl = target.template_for(rel)
        body = _strip_previous_header(new_text)
        if not body.endswith("\n"):
            body += "\n"
        final = header + body
        # Re-check the FILE, not the body. validate_revision ran on what the
        # model wrote; what reaches disk is that plus a header this module
        # builds, so the header is the one part of the shipped template nothing
        # has checked. _header_safe already strips the quote characters that
        # could cause this, and this is the assertion that it worked.
        trapped = set(unfillable_placeholders(final)) - set(
            unfillable_placeholders(body))
        if trapped:
            record["error"] = (
                "The revision header would trap %s inside the template filler's "
                "string mask; %s was not written."
                % (", ".join("{%s}" % name for name in sorted(trapped)), rel)
            )
            logger.warning("Revision header hazard on %s; skipped", rel)
            continue
        try:
            with open(tpl.abs_path, "w", encoding="utf-8") as handle:
                handle.write(final)
        except Exception as exc:
            record["error"] = "Could not write %s: %s" % (rel, exc)
            logger.debug("Revision write failed: %s", tpl.abs_path, exc_info=True)
            continue
        record["applied"].append(rel)
        entry = {
            "rel_path": rel,
            "role": tpl.role,
            "before_chars": len(tpl.text or ""),
            "after_chars": len(final),
            "placeholders_before": sorted(placeholder_names(tpl.text)),
            "placeholders_after": sorted(placeholder_names(final)),
        }
        check = _check_for(checks, rel)
        if check is not None:
            entry["warnings"] = list(check.warnings)
        record["templates"].append(entry)
        _write_round_files(debug_dir, rel, tpl.text, final)

    _write_round_context(debug_dir, record, messages, reply)
    _append_index(target.cli_dir, record)
    return record


def _snapshot_package(cli_dir, label):
    """Copy the active package into ``versions/<label>/`` BEFORE any write."""
    try:
        from .cli_artifacts import snapshot_package_version
        return snapshot_package_version(cli_dir, label)
    except Exception:
        logger.debug("Revision snapshot import/call failed", exc_info=True)
        return _fallback_snapshot(cli_dir, label)


def _fallback_snapshot(cli_dir, label):
    """Copy ``templates/`` alone when cli_artifacts is unavailable.

    Only reached outside the packaged import (a check script running the module
    stand-alone). Partial by design and reported as such — the templates are the
    only thing a revision writes, so they are the only thing it must be able to
    put back.
    """
    try:
        dest = os.path.join(cli_dir, "versions", label, "templates")
        src = os.path.join(cli_dir, "templates")
        if not os.path.isdir(src):
            return ""
        if os.path.isdir(dest):
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        return os.path.dirname(dest)
    except Exception:
        logger.debug("Revision fallback snapshot failed", exc_info=True)
        return ""


def _check_for(checks, rel):
    for check in checks or []:
        if getattr(check, "rel_path", "") == rel:
            return check
    return None


def _safe_name(rel):
    return rel.replace("\\", "/").replace("/", "__")


def _write_round_files(debug_dir, rel, before, after):
    if not debug_dir:
        return
    base = _safe_name(rel)
    _write_text(os.path.join(debug_dir, base + ".before"), before)
    _write_text(os.path.join(debug_dir, base + ".after"), after)
    diff = "\n".join(difflib.unified_diff(
        (before or "").splitlines(), (after or "").splitlines(),
        fromfile=rel + " (before)", tofile=rel + " (after)", lineterm="",
    ))
    _write_text(os.path.join(debug_dir, base + ".diff"), diff + "\n")


def _write_round_context(debug_dir, record, messages, reply):
    if not debug_dir:
        return
    _write_text(os.path.join(debug_dir, "request.txt"), record.get("request", ""))
    _write_text(os.path.join(debug_dir, "reply.txt"), reply or "")
    if messages:
        rendered = []
        for index, message in enumerate(messages):
            rendered.append("===== MESSAGE %d | %s =====" % (
                index, message.get("role", "?")))
            rendered.append(str(message.get("content", "")))
            rendered.append("")
        _write_text(os.path.join(debug_dir, "messages_sent.txt"),
                    "\n".join(rendered))
    _write_json(os.path.join(debug_dir, "revision.json"), record)


def _write_text(path, text):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text or "")
        return path
    except Exception:
        logger.debug("Could not write %s", path, exc_info=True)
        return ""


def _write_json(path, payload):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
        return path
    except Exception:
        logger.debug("Could not write %s", path, exc_info=True)
        return ""


def _append_index(cli_dir, record):
    """Append one line to ``debug/revisions.json``, the package's whole history."""
    path = os.path.join(cli_dir, "debug", REVISION_INDEX_NAME)
    entries = _read_json(path, [])
    if not isinstance(entries, list):
        entries = []
    entries.append({
        "label": record.get("label", ""),
        "time": record.get("time", ""),
        "step_id": record.get("step_id", ""),
        "request": record.get("request", ""),
        "summary": record.get("summary", ""),
        "applied": list(record.get("applied", [])),
        "backup": record.get("backup", ""),
        "rounds": record.get("rounds", 1),
    })
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        logger.debug("Revision index dir failed", exc_info=True)
        return ""
    return _write_json(path, entries)


def revision_history(cli_dir: str, step_id: str = "") -> List[Dict[str, Any]]:
    """Past revisions of this package, oldest first, optionally one step's.

    Fed back into the prompt: a second request against a step the user already
    revised must be able to see what the first one did, or it will happily undo
    it.
    """
    entries = _read_json(
        os.path.join(cli_dir, "debug", REVISION_INDEX_NAME), [])
    if not isinstance(entries, list):
        return []
    if step_id:
        entries = [e for e in entries
                   if isinstance(e, dict) and e.get("step_id") == step_id]
    return [e for e in entries if isinstance(e, dict)]


def restore_revision(cli_dir: str, label: str) -> Dict[str, Any]:
    """Put the templates from ``versions/<label>/`` back at the package root.

    The undo for :func:`apply_revision`. Restores ONLY ``templates/`` — a
    revision writes nothing else, so restoring the JSON as well could roll back
    a step-instruction edit or a regeneration that happened since.
    """
    result = {"label": label, "restored": [], "error": ""}
    src = os.path.join(cli_dir, "versions", label, "templates")
    dest = os.path.join(cli_dir, "templates")
    if not os.path.isdir(src):
        result["error"] = "No snapshot at versions/%s/templates." % label
        return result
    for name in sorted(os.listdir(src)):
        source = os.path.join(src, name)
        if not os.path.isfile(source):
            continue
        try:
            shutil.copy2(source, os.path.join(dest, name))
            result["restored"].append(name)
        except Exception as exc:
            result["error"] = "Could not restore %s: %s" % (name, exc)
            logger.debug("Revision restore failed: %s", name, exc_info=True)
    return result
