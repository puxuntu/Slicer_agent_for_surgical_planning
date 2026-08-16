#!/usr/bin/env python3
"""Check the runtime template-revision core against every shipped CLI package.

    python scripts/check_template_revision.py            # everything
    python scripts/check_template_revision.py --verbose  # print each case

Runs OUTSIDE Slicer, deliberately, and that is the whole reason
``SlicerAIAgentLib/TemplateReviser.py`` is Qt-free and Slicer-free: the part of
the ✎ Revise feature that decides *what may be written into a surgical
package* -- which file a step owns, whether a rewritten template is safe to
install, and whether the original can be recovered -- must be checkable on every
change rather than when someone remembers to open Slicer.

Five groups:

* **Package sweep.** For every step of every ``Resources/extension_CLI/*/``:
  the resolved template paths exist, the eligibility verdict and the resolved
  target agree, and no step that the runtime dispatches with code resolves to
  nothing. That is what catches a regenerated package whose generator entry and
  workflow.json disagree about a step's file.
* **Self-validation.** Every shipped template must pass ``validate_revision``
  against itself. If a real, working template is rejected, the validator would
  reject the model's faithful rewrite of it too, and the feature would be able to
  fail on correct answers -- the one failure mode worth more than all the others.
* **Rejections.** The gates actually bite: a new bare placeholder, a syntax
  error, a blocked import and an empty answer are all refused; a placeholder with
  a default is allowed.
* **Reply parsing.** Every shape the agent may answer in, plus the two that must
  be refused (a foreign path, an ambiguous multi-block reply).
* **Round trip.** ``apply_revision`` on a COPY of a real package: the pre-state
  snapshot holds the original, the installed file holds the new text, the index
  records it, ``restore_revision`` puts it back, and a second revision does not
  stack a second header.

Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_DIR = os.path.join(ROOT, "SlicerAIAgentLib")
CLI_DIR = os.path.join(ROOT, "Resources", "extension_CLI")

FAILURES = []
CHECKS = [0]


def fail(message):
    FAILURES.append(message)


def check(condition, message):
    CHECKS[0] += 1
    if not condition:
        fail(message)
    return bool(condition)


def _load_lib():
    """Import TemplateReviser + CodeValidator without SlicerAIAgentLib/__init__.

    The package's ``__init__`` imports Slicer, so a synthetic package with the
    same ``__path__`` is registered instead -- the same trick
    ``check_voice_commands.py`` uses. TemplateReviser's own imports of
    ``.cli_artifacts`` and ``.PromptLibrary`` are function-local and resolve
    through that path when they run.
    """
    package = types.ModuleType("_revlib")
    package.__path__ = [LIB_DIR]
    sys.modules["_revlib"] = package

    def load(name, parent=package, parent_name="_revlib", directory=LIB_DIR):
        path = os.path.join(directory, name + ".py")
        full = parent_name + "." + name
        spec = importlib.util.spec_from_file_location(full, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[full] = module
        spec.loader.exec_module(module)
        setattr(parent, name, module)
        return module

    # The loader package, faked the same way, so TemplateReviser's
    # `from .extension_cli_loader.templates import _fill_template` resolves to
    # the REAL filler. Without this the module would silently fall back to its
    # own reimplementation of the mask and this script would then be checking
    # the fallback -- i.e. exactly the copy the fill probe exists to avoid.
    loader_dir = os.path.join(LIB_DIR, "extension_cli_loader")
    loader_pkg = types.ModuleType("_revlib.extension_cli_loader")
    loader_pkg.__path__ = [loader_dir]
    sys.modules["_revlib.extension_cli_loader"] = loader_pkg
    package.extension_cli_loader = loader_pkg
    load("cache", loader_pkg, "_revlib.extension_cli_loader", loader_dir)
    load("templates", loader_pkg, "_revlib.extension_cli_loader", loader_dir)

    return load("TemplateReviser"), load("CodeValidator").CodeValidator()


# ---------------------------------------------------------------------------
# 1. Package sweep
# ---------------------------------------------------------------------------

def check_packages(reviser, verbose):
    packages = sorted(
        name for name in os.listdir(CLI_DIR)
        if os.path.isfile(os.path.join(CLI_DIR, name, "workflow.json"))
    ) if os.path.isdir(CLI_DIR) else []
    check(packages, "No generated CLI packages found under Resources/extension_CLI")

    total_steps = 0
    total_templates = 0
    for name in packages:
        cli_dir = os.path.join(CLI_DIR, name)
        with open(os.path.join(cli_dir, "workflow.json"), encoding="utf-8") as fh:
            graph = json.load(fh)
        for step in graph.get("steps", []):
            step_id = step.get("step_id")
            if not step_id:
                continue
            total_steps += 1
            paths = reviser.step_template_paths(cli_dir, step_id)
            target = reviser.resolve_target(cli_dir, name, step_id)
            ok, reason = reviser.revise_eligibility(cli_dir, step_id)
            where = "%s/%s" % (name, step_id)

            for role, rel in paths:
                total_templates += 1
                check(
                    os.path.isfile(os.path.join(cli_dir, rel.replace("/", os.sep))),
                    "%s: %s template %r is named but missing from the package"
                    % (where, role, rel),
                )

            # Eligibility and resolution must agree, or the button offers a
            # revision that then cannot find anything to revise.
            if ok:
                check(target is not None,
                      "%s: reported revisable but resolve_target returned None" % where)
            else:
                check(target is None,
                      "%s: reported NOT revisable (%s) but a target resolved"
                      % (where, reason))

            # A step the runtime answers with code must have a template.
            if step.get("operation_type") in ("extension_op", "slicer_op"):
                check(paths, "%s: %s step has no template file at all"
                      % (where, step.get("operation_type")))

            if verbose and target is not None:
                print("  ok %s -> %s" % (where, ", ".join(target.rel_paths)))

    print("package sweep: %d packages, %d steps, %d templates"
          % (len(packages), total_steps, total_templates))


# ---------------------------------------------------------------------------
# 2. Every shipped template validates against itself
# ---------------------------------------------------------------------------

def check_self_validation(reviser, validator, verbose):
    checked = 0
    for name in sorted(os.listdir(CLI_DIR)) if os.path.isdir(CLI_DIR) else []:
        templates_dir = os.path.join(CLI_DIR, name, "templates")
        if not os.path.isdir(templates_dir):
            continue
        for filename in sorted(os.listdir(templates_dir)):
            if not filename.endswith(".tpl"):
                continue
            path = os.path.join(templates_dir, filename)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            result = reviser.validate_revision(
                text, text, code_validator=validator, rel_path=filename)
            checked += 1
            check(result.ok,
                  "%s/%s: a SHIPPED template is rejected by validate_revision: %s"
                  % (name, filename, "; ".join(result.errors)))
            if verbose and result.warnings:
                print("  warn %s/%s: %s" % (name, filename, "; ".join(result.warnings)))
    print("self-validation: %d shipped templates" % checked)


# ---------------------------------------------------------------------------
# 3. The gates bite
# ---------------------------------------------------------------------------

BASE = (
    "import slicer\n"
    "logic = SomeLogic()\n"
    "logic.run({side})\n"
)


def check_rejections(reviser, validator, verbose):
    def verdict(new_text, original=BASE):
        return reviser.validate_revision(
            original, new_text, code_validator=validator, rel_path="t.py.tpl")

    check(verdict("import slicer\nlogic.run({side})\nprint(1)\n").ok,
          "a legitimate edit that keeps the placeholder was rejected")

    result = verdict("import slicer\nlogic.run({side}, {angle})\n")
    check(not result.ok and any("angle" in e for e in result.errors),
          "a NEW bare placeholder must be refused (it KeyErrors at dispatch)")

    # `{angle: 30}` and `d = {key: 1}` are the SAME six characters to the filler,
    # so they must get the same verdict. Both are refused: nothing can ever fill
    # a name the step does not have, so the first is a constant written as a
    # placeholder, and the second is a dict the filler would eat.
    result = verdict("import slicer\nlogic.run({side}, {angle: 30})\n")
    check(not result.ok and any("angle" in e for e in result.errors),
          "a NEW defaulted placeholder must be refused — write the literal")

    result = verdict("import slicer\nd = {key: 1}\nlogic.run({side})\n")
    check(not result.ok and any("dict(key=value)" in e for e in result.errors),
          "a dict literal with a bare identifier key must be refused, with the "
          "dict(...) remedy in the message")

    # The defaulted form of a placeholder the template ALREADY has is the one
    # legitimate use: same placeholder, made safe against a missing value.
    check(verdict("import slicer\nlogic.run({side: None})\n").ok,
          "defaulting an EXISTING placeholder must be allowed")

    # A correctly closed single-quoted string is masked by the filler and SHOULD
    # be; refusing it would reject most correct answers.
    check(verdict("import slicer\nnode.SetName('Result')\nlogic.run({side})\n").ok,
          "an ordinary single-quoted string must not be mistaken for the "
          "unbalanced-quote hazard")

    check(verdict("import slicer\nlogic.run({vol_lookup})\n").ok,
          "{vol_lookup} is structural and available in every template")

    result = verdict("import slicer\nlogic.run({side}\n")
    check(not result.ok and any("valid Python" in e for e in result.errors),
          "a syntax error must be refused")

    result = verdict("import os\nos.remove('/x')\nlogic.run({side})\n")
    check(not result.ok and any("validator" in e for e in result.errors),
          "code the executor would refuse must not reach the package")

    result = verdict("   \n")
    check(not result.ok, "an empty template must be refused")

    result = verdict(BASE)
    check(result.ok and any("identical" in w for w in result.warnings),
          "an unchanged answer must be reported as unchanged")

    # Dropping a placeholder is allowed but must be said out loud.
    result = verdict("import slicer\nlogic.run('left')\n")
    check(result.ok and any("side" in w for w in result.warnings),
          "dropping a placeholder must warn that the user's choice stops arriving")

    # The two filler hazards, introduced by the revision.
    # The real hazard: an UNBALANCED apostrophe in a comment opens a mask span
    # that runs to the next quote character and swallows the placeholder.
    result = verdict("import slicer\n# don't do this\nlogic.run({side})\n# won't work\n")
    check(not result.ok and any("never be filled" in e for e in result.errors),
          "a placeholder trapped inside the filler's string mask must be refused")
    check(reviser.unfillable_placeholders(
        "# don't\nlogic.run({side})\n# won't\n") == ["side"],
        "unfillable_placeholders must name the trapped placeholder")
    check(reviser.unfillable_placeholders("logic.run({side})  # fine\n") == [],
          "a healthy template must report no trapped placeholders")

    # An f-string interpolation is NOT a placeholder. The loader is right to
    # leave it alone, so adding one must not read as "introduces a placeholder
    # the runtime cannot fill" -- that would refuse a correct revision, and
    # f-strings are how every shipped template reports an error
    # (BoneReconstructionPlanner/cb_step_1 has one).
    fstring = ("import slicer\n"
               "try:\n"
               "    logic.run({side})\n"
               "except Exception as exc:\n"
               '    print(f"failed: {exc}")\n')
    result = verdict(fstring)
    check(result.ok,
          "adding an f-string interpolation must be allowed, got: %s"
          % "; ".join(result.errors))
    check("exc" not in reviser.fillable_placeholder_names(fstring),
          "an f-string interpolation must not count as a fillable placeholder")
    check("side" in reviser.fillable_placeholder_names(fstring),
          "a real placeholder must still count as fillable")

    # And the same template with the placeholder trapped IS refused, so the
    # f-string allowance did not disable the gate. TWO apostrophes: one alone
    # opens no span, because the regex needs a closing quote of the same kind.
    trapped = "import slicer\n# don't\nlogic.run({side})\n# won't\n"
    result = verdict(trapped)
    check(not result.ok,
          "the mask gate must still fire when a real placeholder is trapped")
    check(reviser.unfillable_placeholders(trapped) == ["side"],
          "the trapped placeholder must be named, got %r"
          % reviser.unfillable_placeholders(trapped))

    # The fill probe must be answering with the REAL loader, not the fallback.
    # A silent fallback would make every check above test a copy of the filler
    # rather than the filler.
    try:
        from _revlib.extension_cli_loader.templates import _fill_template
        probe_ok = _fill_template("x = {side}\n", {"side": "'left'"}) == "x = 'left'\n"
    except Exception as exc:
        probe_ok = False
        fail("the real _fill_template is not importable here: %s" % exc)
    check(probe_ok, "the real _fill_template did not fill a trivial template")

    if verbose:
        print("  rejection cases exercised")
    print("rejection gates: exercised")


# ---------------------------------------------------------------------------
# 4. Reply parsing
# ---------------------------------------------------------------------------

def check_parsing(reviser, verbose):
    known = ["templates/cb_step_12.py.tpl"]
    two = ["templates/cb_step_3_pre.py.tpl", "templates/cb_step_3_post.py.tpl"]

    payload = json.dumps({
        "analysis": "wrong view",
        "summary": "show in Red only",
        "templates": {known[0]: "import slicer\n"},
    })
    parsed = reviser.parse_reply(payload, known)
    check(parsed.ok and parsed.templates[known[0]] == "import slicer\n",
          "a bare JSON reply must parse")
    check(parsed.summary == "show in Red only", "the summary must survive parsing")

    parsed = reviser.parse_reply("Here you go:\n```json\n%s\n```\n" % payload, known)
    check(parsed.ok, "a fenced JSON reply must parse")

    marker = ("FILE: templates/cb_step_3_pre.py.tpl\n```python\nimport slicer\n```\n"
              "FILE: templates/cb_step_3_post.py.tpl\n```python\nimport vtk\n```\n")
    parsed = reviser.parse_reply(marker, two)
    check(parsed.ok and len(parsed.templates) == 2,
          "the FILE: marker shape must parse both templates")

    parsed = reviser.parse_reply("```python\nimport slicer\n```", known)
    check(parsed.ok and parsed.templates[known[0]] == "import slicer\n",
          "a lone code block is unambiguous when the step has ONE template")

    parsed = reviser.parse_reply("```python\na\n```\n```python\nb\n```", known)
    check(not parsed.ok and parsed.error,
          "two blocks for one template is ambiguous and must be refused")

    foreign = json.dumps({"templates": {"templates/cb_step_99.py.tpl": "x\n"}})
    parsed = reviser.parse_reply(foreign, known)
    check(not parsed.ok,
          "a path the step does not own must never be installed")

    # THE trap: a JSON reply with the key misspelled must produce a correctable
    # error, never fall through to the single-block shape -- which would install
    # the JSON document itself as the template. A JSON object is a valid Python
    # dict-literal expression, so every downstream gate would pass it and the
    # step would silently do nothing.
    misnamed = ('```json\n' + json.dumps({
        "analysis": "a", "summary": "b",
        "template": {known[0]: "import slicer\n"},   # singular: wrong
    }) + '\n```')
    parsed = reviser.parse_reply(misnamed, known)
    check(not parsed.ok and parsed.error and not parsed.templates,
          "a JSON reply with a misspelled templates key must NOT be installed "
          "as a template")
    check("templates" in (parsed.error or ""),
          "the error must tell the model which key it needed")

    # ... and the same reply with the correct key must still work through a
    # ```json fence, which is what the prompt now mandates so the tool loop ends.
    fenced = ('```json\n' + json.dumps({
        "summary": "s", "templates": {known[0]: "import slicer\n"}}) + '\n```')
    parsed = reviser.parse_reply(fenced, known)
    check(parsed.ok and parsed.templates[known[0]] == "import slicer\n",
          "the fenced-json contract the prompt mandates must parse")

    parsed = reviser.parse_reply(json.dumps({"blocked": "no such API"}), known)
    check(not parsed.ok and parsed.blocked == "no such API",
          "a refusal must be carried through as `blocked`, not as a failure")

    parsed = reviser.parse_reply("", known)
    check(not parsed.ok and parsed.error, "an empty reply must be refused")

    # A basename-only path is accepted (models drop the folder), a different
    # basename is not.
    parsed = reviser.parse_reply(
        json.dumps({"templates": {"cb_step_12.py.tpl": "import slicer\n"}}), known)
    check(parsed.ok, "a basename-only path must resolve to the step's template")

    if verbose:
        print("  parsing cases exercised")
    print("reply parsing: exercised")


# ---------------------------------------------------------------------------
# 5. Apply / restore round trip on a COPY of a real package
# ---------------------------------------------------------------------------

def _first_revisable_package(reviser):
    for name in sorted(os.listdir(CLI_DIR)) if os.path.isdir(CLI_DIR) else []:
        cli_dir = os.path.join(CLI_DIR, name)
        graph_path = os.path.join(cli_dir, "workflow.json")
        if not os.path.isfile(graph_path):
            continue
        with open(graph_path, encoding="utf-8") as fh:
            graph = json.load(fh)
        for step in graph.get("steps", []):
            step_id = step.get("step_id")
            if step_id and reviser.resolve_target(cli_dir, name, step_id):
                return name, step_id
    return "", ""


def check_round_trip(reviser, verbose):
    name, step_id = _first_revisable_package(reviser)
    if not check(name, "no package offered a revisable step for the round trip"):
        return

    workspace = tempfile.mkdtemp(prefix="revcheck_")
    try:
        cli_dir = os.path.join(workspace, name)
        shutil.copytree(os.path.join(CLI_DIR, name), cli_dir,
                        ignore=shutil.ignore_patterns("versions", "debug", "logs"))
        target = reviser.resolve_target(cli_dir, name, step_id)
        if not check(target is not None, "the copied package did not resolve"):
            return
        rel = target.rel_paths[0]
        original = target.template_for(rel).text

        # FIRST, and it writes nothing: a template the agent returned VERBATIM
        # must not be rewritten. The agent is asked for the complete file for
        # every template of the step, so it routinely echoes the one it did not
        # touch, and stamping a header on that would report an untouched file as
        # revised — which is exactly what a real run produced ("Revised
        # cb_step_13_post … Warnings: identical to the original").
        echoed = reviser.apply_revision(
            target, {rel: original}, request="no-op", summary="", rounds=1,
            stamp="20260101_000009")
        check(echoed["applied"] == [] and echoed.get("unchanged") == [rel],
              "an unchanged template must be skipped, got applied=%r unchanged=%r"
              % (echoed["applied"], echoed.get("unchanged")))
        check("unchanged" in (echoed.get("error") or ""),
              "the caller must be told the agent changed nothing")
        with open(os.path.join(cli_dir, rel.replace("/", os.sep)), encoding="utf-8") as fh:
            check(fh.read() == original,
                  "a no-op revision must leave the file byte-identical")

        new_text = original + "\nprint('revised')\n"
        record = reviser.apply_revision(
            target, {rel: new_text}, request="make it print",
            summary="added a print", rounds=1, stamp="20260101_000000")

        check(record["applied"] == [rel],
              "apply_revision reported %r, expected [%r]" % (record["applied"], rel))
        check(record["backup"] == "versions/revision_20260101_000000",
              "the backup path must be reported: %r" % record["backup"])

        # The PRE-state must be what the snapshot holds. This is the property the
        # whole feature promises the user.
        snapshot = os.path.join(cli_dir, "versions", "revision_20260101_000000",
                                rel.replace("/", os.sep))
        if check(os.path.isfile(snapshot), "no pre-revision snapshot at %s" % snapshot):
            with open(snapshot, encoding="utf-8") as fh:
                check(fh.read() == original,
                      "the snapshot does not hold the ORIGINAL template")

        installed_path = os.path.join(cli_dir, rel.replace("/", os.sep))
        with open(installed_path, encoding="utf-8") as fh:
            installed = fh.read()
        check("print('revised')" in installed, "the new text was not installed")
        check(installed.startswith("# [revised]"),
              "the installed template must carry a revision header")
        check("versions/revision_20260101_000000" in installed,
              "the header must name the backup it can be restored from")

        index = os.path.join(cli_dir, "debug", "revisions.json")
        if check(os.path.isfile(index), "no debug/revisions.json index written"):
            with open(index, encoding="utf-8") as fh:
                entries = json.load(fh)
            check(len(entries) == 1 and entries[0]["step_id"] == step_id,
                  "the index does not record this revision")

        history = reviser.revision_history(cli_dir, step_id)
        check(len(history) == 1, "revision_history did not return the entry")

        for suffix in (".before", ".after", ".diff"):
            path = os.path.join(cli_dir, "debug", "revision_20260101_000000",
                                rel.replace("/", "__") + suffix)
            check(os.path.isfile(path), "missing round artifact %s" % suffix)

        # A SECOND revision must replace the header, not stack one.
        target2 = reviser.resolve_target(cli_dir, name, step_id)
        record2 = reviser.apply_revision(
            target2, {rel: installed + "\nprint('again')\n"},
            request="and again", summary="second", rounds=1,
            stamp="20260101_000001")
        check(record2["applied"] == [rel], "the second revision did not apply")
        with open(installed_path, encoding="utf-8") as fh:
            twice = fh.read()
        check(twice.count("# [revised]") == 1,
              "revision headers must not stack (found %d)"
              % twice.count("# [revised]"))
        check(len(reviser.revision_history(cli_dir, step_id)) == 2,
              "the index must accumulate")

        # Restore takes the package back to the pre-FIRST-revision state.
        restored = reviser.restore_revision(cli_dir, "revision_20260101_000000")
        check(not restored["error"], "restore reported %r" % restored["error"])
        with open(installed_path, encoding="utf-8") as fh:
            check(fh.read() == original,
                  "restore_revision did not recover the original template")

        # The header carries the SURGEON'S OWN SENTENCE into a comment at the
        # top of an executable template. An apostrophe in it ("shouldn't") would
        # open the filler's string mask and swallow the placeholder below —
        # introducing, through the header, the exact defect the validator
        # refuses in the model's output.
        reviser.restore_revision(cli_dir, "revision_20260101_000000")
        target3 = reviser.resolve_target(cli_dir, name, step_id)
        placeholder_body = original + "\nlogic.check({vol_lookup})\n"
        record3 = reviser.apply_revision(
            target3, {rel: placeholder_body},
            request="the model shouldn't be placed on the left orbit",
            summary="don't use the wrong side", rounds=1,
            stamp="20260101_000002")
        with open(installed_path, encoding="utf-8") as fh:
            headered = fh.read()
        check(record3["applied"] == [rel],
              "a request containing apostrophes must still apply: %r"
              % record3.get("error"))
        check("shouldnt" in headered and "shouldn't" not in headered,
              "the header must strip the request's apostrophes")
        check(set(reviser.unfillable_placeholders(headered))
              <= set(reviser.unfillable_placeholders(placeholder_body)),
              "the header must not trap a placeholder the body did not")

        if verbose:
            print("  round trip on %s/%s (%s)" % (name, step_id, rel))
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    print("round trip: %s/%s" % (name, step_id))


# ---------------------------------------------------------------------------
# 5b. Header stripping must not eat the precondition block
# ---------------------------------------------------------------------------

def check_header_strip(reviser, verbose):
    """The second revision of a step must not lose its module-entry marker.

    The model is shown the template WITH the header a previous revision added,
    so it reproduces one. A strip that swallowed "every comment line after the
    header" would take the ``# precondition:begin ... # precondition:end`` block
    with it -- the runtime's only marker for firing the extension's ``enter()``,
    whose absence breaks every later interactive step and raises nothing.
    """
    strip = reviser._strip_previous_header

    revised = (
        "# [revised] Rewritten by the runtime revision agent (revision_x).\n"
        "# Pre-revision package backed up under versions/revision_x/.\n"
        "# Requested: fix the view\n"
        "# Change: red only\n"
        "# precondition:begin\n"
        "selectModule('Foo')\n"
        "# precondition:end\n"
        "import slicer\n"
    )
    stripped = strip(revised)
    check(stripped.startswith("# precondition:begin"),
          "the precondition block must survive a header strip, got %r"
          % stripped[:60])
    check("# [revised]" not in stripped, "the header itself must be removed")

    # A template that merely OPENS with an ordinary comment must be untouched.
    plain = "# Step 12: draw the curve\nimport slicer\n"
    check(strip(plain) == plain, "a template with no header must be untouched")

    # The runtime self-correction's header is stripped by the same rule.
    runtime_fixed = (
        "# [runtime-fixed] Auto-revised by runtime self-correction at 20260101.\n"
        "# Pre-revision templates backed up under versions/runtime_fix_x/.\n"
        "# Fixed runtime error: boom\n"
        "import slicer\n"
    )
    check(strip(runtime_fixed) == "import slicer\n",
          "a runtime-fix header must be stripped too")

    if verbose:
        print("  header strip cases exercised")
    print("header strip: exercised")


# ---------------------------------------------------------------------------
# 6. The prompt file exists and carries its placeholders
# ---------------------------------------------------------------------------

def check_prompt(reviser, verbose):
    path = os.path.join(ROOT, "Resources", "Prompts",
                        reviser.TEMPLATE_REVISION_PROMPT)
    if not check(os.path.isfile(path), "missing prompt file %s" % path):
        return
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for token in ("{{BLOCKED_MODULES}}", "{{BLOCKED_FUNCTIONS}}",
                  "{{ALLOWED_MODULES}}", "{{EXTENSION_SOURCE_ROOTS}}"):
        check(token in text, "the revision prompt never fills %s" % token)

    # The reply must be FENCED. llm_client._runToolLoop ends a round only when
    # _extractCode finds a fenced block, so a prompt that asks for bare JSON
    # produces a loop that never accepts a correct answer -- it burns every
    # round, then every retry, and reports a failure that did not happen.
    check("```json" in text,
          "the revision prompt must mandate a ```json fence, or the tool loop "
          "can never terminate on a compliant reply")
    check("fence is not cosmetic" in text,
          "the prompt must say WHY the fence is required, or it reads as style")
    # The rendered prompt must actually substitute them, or the model is told
    # about a blocked list it never sees.
    rendered = reviser.revision_system_prompt(
        blocked_modules="os, sys", blocked_functions="eval",
        allowed_modules="slicer", source_roots="- `ext:Foo/`")
    # Match PromptLibrary's own token shape, not a bare "{{": the prompt
    # deliberately CONTAINS `{{` and `}}` where it explains that literal braces
    # in a template must be doubled.
    import re as _re
    leftover = _re.findall(r"\{\{([A-Z0-9_]+)\}\}", rendered)
    check(not leftover,
          "the rendered revision prompt still has unfilled placeholders: %s"
          % ", ".join(leftover))
    check("os, sys" in rendered, "the blocked-module list did not reach the prompt")
    if verbose:
        print("  prompt renders to %d chars" % len(rendered))
    print("prompt: %s" % os.path.basename(path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    reviser, validator = _load_lib()

    check_packages(reviser, args.verbose)
    check_self_validation(reviser, validator, args.verbose)
    check_rejections(reviser, validator, args.verbose)
    check_parsing(reviser, args.verbose)
    check_round_trip(reviser, args.verbose)
    check_header_strip(reviser, args.verbose)
    check_prompt(reviser, args.verbose)

    print("checks run: %d" % CHECKS[0])
    if FAILURES:
        print("\nFAILURES (%d):" % len(FAILURES))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("all template-revision checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
