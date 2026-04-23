"""Hub-side parity check: the copy matches proofmark_pdf's behavior."""
from __future__ import annotations

import pytest


def test_hub_flag_defaults_on(monkeypatch: pytest.MonkeyPatch) -> None:
    from proofmark_studio.feature_flags import is_enabled

    monkeypatch.delenv("TOOL_MERGE_PDF_ENABLED", raising=False)
    assert is_enabled("merge-pdf") is True


def test_hub_flag_turns_off(monkeypatch: pytest.MonkeyPatch) -> None:
    from proofmark_studio.feature_flags import is_enabled

    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "false")
    assert is_enabled("merge-pdf") is False


def test_hub_flag_env_name_shape() -> None:
    from proofmark_studio.feature_flags import flag_env_name

    assert flag_env_name("merge-pdf") == "TOOL_MERGE_PDF_ENABLED"
