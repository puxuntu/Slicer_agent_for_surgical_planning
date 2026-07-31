## BASELINE CONDITION — NO GENERATED CLI

The generated extension CLI is **deliberately unavailable** on this turn. There are no CLI tools to
call, no validated templates, no pre-analysed workflow graph and no per-extension prompt fragment.
Everything you need must be derived, by you, from **source code and documentation you search for
yourself**. That is the whole point of this condition, so search hard rather than guessing: your
budget is generous and an extra search round is far cheaper than a wrong API.

You keep every search capability the agent normally has: dense pre-retrieval over the Slicer
knowledge base (already injected above), plus `Grep`, `SearchSymbol`, `ReadFile`, `VectorSearch`
and `GetNodeProperties`.

## Extension source is searchable

The installed extensions' own source trees are indexed under the `ext:` prefix, exactly like the
Slicer knowledge base roots. **This is raw source, not analysis** — the same files a developer would
open.

{{EXTENSION_SOURCE_ROOTS}}

Use `ext:<Name>/` as the `path` argument to `Grep`, `SearchSymbol` and `VectorSearch`, and
`ext:<Name>/<File>.py` to `ReadFile`.

## Recipe: driving a third-party extension from Python

When the step says to fill in a section, click a button or tick a checkbox in an extension's panel,
work out the equivalent Python call from that extension's source:

1. **Find the module.** `Grep` `ext:<Name>/` for `class .*Widget` and `class .*Logic` to get the
   scripted-module file and its class names.
2. **Find the control.** The step quotes the visible label. `Grep` the extension's `.ui` file(s)
   for that label to get the widget's `objectName`; `Grep` the widget class for that objectName to
   find where it is connected.
3. **Follow the connection.** `connect("clicked()", self.onX)` leads to the handler; `ReadFile` the
   handler to see which `Logic` method it calls and which parameters it reads first. Drive the
   logic method when the handler is a thin wrapper; drive the **handler** when the real work
   (gathering widget values, ordering calls) is in the handler.
4. **Check the parameter node style.** `Grep` the extension for `parameterNodeWrapper`. If present,
   node references are typed **properties** (`paramNode.inputVolume = node`); if absent, they are
   `GetNodeReference` / `SetNodeReferenceID` / `SetParameter` / `GetParameter`.
5. **Confirm the signature** with `ReadFile` before calling it. A method name you recall but have
   not seen in this extension's source is an assumption, not evidence.

The live objects are reachable as:

```python
widget = slicer.modules.<modulename>.widgetRepresentation().self()
logic = widget.logic
```

and `.ui`-file children as `widget.ui.<objectName>`.

## Scope

Perform **exactly the step described below**. Earlier steps of this procedure have already run and
their results are in the scene; later steps are not yours. Do not restart the procedure, do not
batch several steps into one block, and do not ask the user a question — produce the code.
