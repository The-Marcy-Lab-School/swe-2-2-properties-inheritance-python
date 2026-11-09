"""Turn pytest's JUnit XML into a readable summary of which tests passed.

Writes two things from one source:

  1. A table appended to the Actions job summary, which is what the student
     reads after a push.
  2. A commit status under the context "marcy/score", which is what the
     gradebook collector reads back through the API.

Neither one says whether the assignment is complete. Assignments are graded
against a rubric by an instructor, and a second message about completion here
would be a second source of truth that could disagree with the first. So this
reports which tests passed and stops there.
"""

import os
import subprocess
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def source_path(case):
    """The test file this case came from."""
    f = case.get("file")
    if f:
        return Path(f)
    # classname looks like "tests.test_debug"; turn it back into a path.
    return Path(case.get("classname", "").replace(".", "/") + ".py")


def suite_meta(path: Path):
    """The suite's display name and whether it counts, read from the file.

    Test files declare `TEST_SUITE_NAME = "Debug Tests"` and bonus files add
    `SCORED = False`. JUnit XML carries neither, so read them from the source
    rather than inventing a name from the filename.
    """
    name, scored = None, True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    m = re.search(r"""^TEST_SUITE_NAME\s*=\s*["'](.+?)["']""", text, re.M)
    if m:
        name = m.group(1)
    if re.search(r"^SCORED\s*=\s*False\b", text, re.M):
        scored = False
    if not name:
        stem = path.stem.removeprefix("test_").replace("_", " ").title()
        name = f"{stem} Tests" if stem else "Tests"
    return name, scored


def main(xml_path):
    # No XML means pytest could not start: a syntax error, or a missing import.
    # That is a real result and must not be reported as a crash of the grader.
    if not os.path.exists(xml_path):
        write_summary("Tests could not run. Check the log above for the error.")
        set_status("error", "tests could not run")
        return

    root = ET.parse(xml_path).getroot()

    suites = defaultdict(lambda: [0, 0])
    unscored = set()
    for case in root.iter("testcase"):
        # A skipped test is not a failed test. Bonus questions ship skipped on
        # purpose, so counting them would understate a complete submission.
        if case.find("skipped") is not None:
            continue
        name, scored = suite_meta(source_path(case))
        if not scored:
            unscored.add(name)
        passed = not any(case.find(t) is not None for t in ("failure", "error"))
        s = suites[name]
        s[1] += 1
        s[0] += int(passed)

    lines = ["| Suite | Passed |", "| --- | --- |"]
    for name in sorted(suites):
        p, t = suites[name]
        tag = " _(not scored)_" if name in unscored else ""
        lines.append(f"| {name}{tag} | {p}/{t} |")
    lines.append("")
    lines.append(
        "Your instructor grades this assignment against the rubric. "
        "This table only shows which tests passed on your last push."
    )
    write_summary("\n".join(lines))

    # The check stays neutral. A student pushing unfinished work is doing the
    # right thing, so this never renders as a pass or a failure. The counts are
    # here because the gradebook reads this description.
    passed = sum(p for n, (p, _) in suites.items() if n not in unscored)
    total = sum(t for n, (_, t) in suites.items() if n not in unscored)
    set_status("success", f"{passed}/{total} tests passing")


def write_summary(markdown):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        print(markdown)
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write("## Test results\n\n" + markdown + "\n")


def set_status(state, description):
    """Post the commit status the gradebook reads. Never fail the job over it."""
    repo, sha = os.environ.get("REPO"), os.environ.get("SHA")
    if not (repo and sha):
        return
    try:
        subprocess.run(
            ["gh", "api", "-X", "POST", f"repos/{repo}/statuses/{sha}",
             "-f", f"state={state}",
             "-f", "context=marcy/score",
             "-f", f"description={description[:140]}"],
            check=False, capture_output=True,
        )
    except OSError:
        pass


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results.xml")
