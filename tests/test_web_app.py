"""Hub tests. Studio serves a React SPA shell; most UI assertions moved to
Phase 3 (tool-stub routing) and Phase 7 (E2E click-through)."""
from fastapi.testclient import TestClient

from web_app import APP_NAME, app


client = TestClient(app)


def test_spa_shell_renders():
    """The React SPA shell loads — page title + mount points + JSX script tags present."""
    response = client.get("/")
    assert response.status_code == 200
    assert APP_NAME in response.text or "ProofMark Studio" in response.text
    assert 'id="root"' in response.text
    assert 'id="studio-canvas-root"' in response.text  # art layer mount
    assert "src/app.jsx" in response.text
    assert "src/studio-canvas.jsx" in response.text
    # No grid-bg element — removed in Phase 2
    assert "app-grid-bg" not in response.text


def test_health_endpoint_reports_service():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "proofmark-studio"


def test_hub_redirects_to_pdf_on_8010():
    response = client.get("/go/proofmark-pdf", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert ":8010" in response.headers["location"]


def test_hub_redirects_to_text_cleaner_on_8000():
    response = client.get("/go/text-inspection", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert ":8000" in response.headers["location"]


def test_studio_map_api_exposes_spokes():
    response = client.get("/api/studio-map")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "proofmark-studio"
    assert len(payload["spokes"]) >= 4
    assert any(s["id"] == "pdf" for s in payload["spokes"])
    assert any(s["id"] == "text" for s in payload["spokes"])


def test_local_projects_api_exposes_inventory():
    response = client.get("/api/local-projects")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "proofmark-studio"
    assert any(p["slug"] == "proofmark-studio" for p in payload["projects"])


def test_unknown_tool_page_returns_404():
    response = client.get("/tools/not-a-real-tool")
    assert response.status_code == 404


def test_legacy_policy_pages_render():
    local_projects = client.get("/local-projects")
    privacy = client.get("/privacy")
    terms = client.get("/terms")
    assert local_projects.status_code == 200
    assert privacy.status_code == 200
    assert terms.status_code == 200
    assert "Local project inventory" in local_projects.text
    assert "Privacy Policy" in privacy.text
    assert "Terms of Use" in terms.text


def test_search_support_files_render():
    robots = client.get("/robots.txt")
    sitemap = client.get("/sitemap.xml")
    assert robots.status_code == 200
    assert "Sitemap:" in robots.text
    assert sitemap.status_code == 200
    assert "<urlset" in sitemap.text


def test_sitemap_enumerates_live_tools():
    """Phase 18.6: every live tool has a /tool/{slug} entry in sitemap.xml."""
    from proofmark_studio import tool_registry as reg
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    live_slugs = [s for s, t in reg.TOOLS.items() if t["status"] == "live"]
    assert len(live_slugs) >= 30  # guardrail: sweep keeps this honest
    for slug in live_slugs:
        assert f"/tool/{slug}" in r.text, f"sitemap missing /tool/{slug}"


def test_sitemap_enumerates_beta_tools():
    """Beta tools live in the catalog and deserve indexing too."""
    from proofmark_studio import tool_registry as reg
    r = client.get("/sitemap.xml")
    beta_slugs = [s for s, t in reg.TOOLS.items() if t["status"] == "beta"]
    for slug in beta_slugs:
        assert f"/tool/{slug}" in r.text, f"sitemap missing beta /tool/{slug}"


def test_sitemap_omits_flag_disabled_tools(monkeypatch):
    """TOOL_<SLUG>_ENABLED=false demotes a tile and must drop it from the sitemap."""
    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "false")
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert "/tool/merge-pdf" not in r.text


def test_sitemap_includes_content_pages():
    r = client.get("/sitemap.xml")
    assert "<loc>" in r.text
    for path in ("/", "/about", "/changelog", "/privacy", "/terms"):
        assert path in r.text, f"sitemap missing content page {path}"


def test_stub_page_has_meta_description():
    """Phase 18.6: every tool stub page carries a <meta name='description'>."""
    r = client.get("/tool/project-intake")
    assert r.status_code == 200
    assert '<meta name="description"' in r.text
    # Description should echo the tool's registry desc.
    assert "project setup" in r.text.lower() or "source files" in r.text.lower()


def test_stub_page_has_og_tags():
    """OpenGraph tags so social shares don't look naked."""
    r = client.get("/tool/edit-pdf")
    assert 'property="og:title"' in r.text
    assert 'property="og:description"' in r.text
    assert 'property="og:type"' in r.text


def test_static_jsx_served():
    """JSX source files reachable at /static/hub/src/*."""
    r = client.get("/static/hub/src/app.jsx")
    assert r.status_code == 200
    assert "React" in r.text or "const App" in r.text
    r = client.get("/static/hub/src/studio-canvas.jsx")
    assert r.status_code == 200
    assert "StudioCanvas" in r.text


# ─── Phase 3: Tool router + stub page ──────────────────────────────────

def test_tool_router_redirects_live_pdf_tool():
    r = client.get("/tool/merge-pdf", follow_redirects=False)
    assert r.status_code in {302, 307}
    assert "/merge-pdf" in r.headers["location"]
    assert ":8010" in r.headers["location"] or r.headers["location"].startswith("/pdf/")


def test_tool_router_redirects_live_text_tool():
    r = client.get("/tool/text-inspection", follow_redirects=False)
    assert r.status_code in {302, 307}
    assert ":8000" in r.headers["location"] or r.headers["location"].startswith("/text/")


def test_tool_router_stub_for_planned():
    # Workflow tiles stay `planned` until Phase 17 infra (DB+auth) lands.
    r = client.get("/tool/project-intake")
    assert r.status_code == 200
    assert "Project Intake" in r.text
    assert "Return to the hub" in r.text
    assert "Planned" in r.text


def test_tool_router_stub_for_beta():
    # Office → PDF stays `beta` until a self-hosted LibreOffice runtime lands.
    r = client.get("/tool/word-to-pdf")
    assert r.status_code == 200
    assert "Word to PDF" in r.text
    assert "Beta" in r.text
    assert "Return to the hub" in r.text


def test_tool_router_stub_for_beta_parent_link():
    """Stub page renders the 'Open parent app' button with hub chrome."""
    r = client.get("/tool/edit-pdf")
    assert r.status_code == 200
    assert "Edit PDF" in r.text
    assert "Return to the hub" in r.text
    assert "Open ProofMark PDF" in r.text


def test_tool_router_404_for_unknown():
    r = client.get("/tool/this-is-not-a-real-tool")
    assert r.status_code == 404


def test_api_tools_returns_full_registry():
    r = client.get("/api/tools")
    assert r.status_code == 200
    payload = r.json()
    assert payload["service"] == "proofmark-studio"
    tools = payload["tools"]
    assert "merge-pdf" in tools
    assert tools["merge-pdf"]["status"] == "live"
    # Workflow tiles stay planned until Phase 17 infra (DB+auth) lands.
    assert "project-intake" in tools
    assert tools["project-intake"]["status"] == "planned"
    # Counts sanity — post phase-15/16 promotion sweep baseline
    counts = payload["counts"]
    assert counts["total"] >= 40
    assert counts["live"] >= 30
