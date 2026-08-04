"""Contracts for files that must trigger the retained CI workflow."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _trigger_path_lines(source: str, trigger: str) -> set[str]:
    lines = source.splitlines()
    trigger_start = lines.index(f"  {trigger}:") + 1
    trigger_end = next(
        (
            index
            for index in range(trigger_start, len(lines))
            if lines[index].strip() and _indent(lines[index]) <= 2
        ),
        len(lines),
    )
    trigger_lines = lines[trigger_start:trigger_end]

    try:
        paths_start = trigger_lines.index("    paths:") + 1
    except ValueError:
        return set()

    path_lines: set[str] = set()
    for line in trigger_lines[paths_start:]:
        if line.strip() and _indent(line) <= 4:
            break
        path_lines.add(line)
    return path_lines


def test_runtime_and_deploy_inputs_trigger_push_and_pull_request_ci() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    push_lines = _trigger_path_lines(source, "push")
    pull_request_lines = _trigger_path_lines(source, "pull_request")

    for path in ("docs/about.md", "docs/changelog.md", ".vercelignore"):
        entry = f"      - '{path}'"
        assert entry in push_lines, f"{path} must trigger push CI"
        assert entry in pull_request_lines, f"{path} must trigger pull-request CI"


def test_commented_paths_do_not_satisfy_the_trigger_contract() -> None:
    source = """on:
  push:
    paths:
      # - 'docs/about.md'
  pull_request:
    paths:
      # - 'docs/about.md'
permissions:
  contents: read
"""
    entry = "      - 'docs/about.md'"

    assert entry not in _trigger_path_lines(source, "push")
    assert entry not in _trigger_path_lines(source, "pull_request")


def test_paths_ignore_entries_do_not_satisfy_the_trigger_contract() -> None:
    source = """on:
  push:
    paths-ignore:
      - 'docs/about.md'
  pull_request:
    paths-ignore:
      - 'docs/about.md'
permissions:
  contents: read
"""
    entry = "      - 'docs/about.md'"

    assert entry not in _trigger_path_lines(source, "push")
    assert entry not in _trigger_path_lines(source, "pull_request")
