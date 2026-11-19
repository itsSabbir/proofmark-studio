"""Static contracts for the Windows all-app launcher."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = REPO_ROOT / "scripts" / "launch-all.ps1"


def test_text_sibling_launcher_uses_current_repository_name() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert "Join-Path $ToolsRoot 'text-remover'" in source
    assert "Join-Path $ToolsRoot 'text-remover\\.venv\\Scripts\\python.exe'" in source
    assert "text :8000   (text-remover)" in source
    assert "text-cleaner" not in source
