"""Phase 10.5 — /api/tools downgrades a live tool to 'planned' when the flag is off.

This is the contract between the registry (truth at deploy time) and the
runtime (truth right now). Flipping TOOL_<SLUG>_ENABLED=false demotes the tile.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from web_app import app

client = TestClient(app)


def test_merge_pdf_live_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOOL_MERGE_PDF_ENABLED", raising=False)
    payload = client.get("/api/tools").json()
    assert payload["tools"]["merge-pdf"]["status"] == "live"
    # `paused` flag absent when not downgraded.
    assert payload["tools"]["merge-pdf"].get("paused") is not True


def test_merge_pdf_demoted_when_flag_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "false")
    payload = client.get("/api/tools").json()
    entry = payload["tools"]["merge-pdf"]
    assert entry["status"] == "planned"
    assert entry["paused"] is True


def test_beta_tool_also_demotes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Beta tiles should also be flag-demotable."""
    monkeypatch.setenv("TOOL_ORGANIZE_PDF_ENABLED", "0")
    payload = client.get("/api/tools").json()
    entry = payload["tools"]["organize-pdf"]
    assert entry["status"] == "planned"
    assert entry["paused"] is True


def test_counts_reflect_demotions(monkeypatch: pytest.MonkeyPatch) -> None:
    """When a live tool is demoted, the live count drops and planned rises."""
    monkeypatch.delenv("TOOL_MERGE_PDF_ENABLED", raising=False)
    baseline = client.get("/api/tools").json()["counts"]

    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "off")
    after = client.get("/api/tools").json()["counts"]

    assert after["live"] == baseline["live"] - 1
    assert after["planned"] == baseline["planned"] + 1
    assert after["total"] == baseline["total"]


def test_tool_router_respects_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """/tool/<slug> renders the stub instead of redirecting when flag is off."""
    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "false")
    response = client.get("/tool/merge-pdf", follow_redirects=False)
    assert response.status_code == 200
    assert "Return to the hub" in response.text
