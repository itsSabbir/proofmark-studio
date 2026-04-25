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


def test_sitemap_enumerates_beta_tools_in_roadmap_mode(monkeypatch):
    """Roadmap mode (PROOFMARK_SHOW_ALL_TILES=true) reveals beta tools."""
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
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


def test_stub_page_has_meta_description(monkeypatch):
    """Phase 18.6: every tool stub page carries a <meta name='description'>."""
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/project-intake")
    assert r.status_code == 200
    assert '<meta name="description"' in r.text
    # Description should echo the tool's registry desc.
    assert "project setup" in r.text.lower() or "source files" in r.text.lower()


def test_stub_page_has_og_tags(monkeypatch):
    """OpenGraph tags so social shares don't look naked."""
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/edit-pdf")
    assert 'property="og:title"' in r.text
    assert 'property="og:description"' in r.text
    assert 'property="og:type"' in r.text


# ─── Phase 18.7: /about + /changelog ───────────────────────────────────

def test_about_page_renders_from_markdown():
    r = client.get("/about")
    assert r.status_code == 200
    # Content from docs/about.md should flow through the markdown renderer.
    assert "<h1>" in r.text
    assert "ProofMark Studio" in r.text
    assert '<meta name="description"' in r.text


def test_changelog_page_renders_from_markdown():
    r = client.get("/changelog")
    assert r.status_code == 200
    assert "<h1>" in r.text
    # The changelog tracks promotion history — assert a concrete anchor.
    assert "Phase" in r.text or "release" in r.text.lower()
    assert '<meta name="description"' in r.text


def test_markdown_lite_renders_headings_paragraphs_lists():
    from proofmark_studio.markdown_lite import render
    md = "# Title\n\nFirst paragraph.\n\n- one\n- two\n\nSecond paragraph."
    html_out = render(md)
    assert "<h1>Title</h1>" in html_out
    assert "<p>First paragraph.</p>" in html_out
    assert "<ul>" in html_out and "<li>one</li>" in html_out and "<li>two</li>" in html_out
    assert "<p>Second paragraph.</p>" in html_out


def test_markdown_lite_escapes_html_in_source():
    """Authored content only, but still escape to guard against accidental raw HTML."""
    from proofmark_studio.markdown_lite import render
    html_out = render("# <script>alert(1)</script>")
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_markdown_lite_renders_inline_formatting():
    from proofmark_studio.markdown_lite import render
    html_out = render("Hello **world** and _italics_ and `code`.")
    assert "<strong>world</strong>" in html_out
    assert "<em>italics</em>" in html_out
    assert "<code>code</code>" in html_out


def test_markdown_lite_renders_links():
    from proofmark_studio.markdown_lite import render
    html_out = render("See [hub](/).")
    assert '<a href="/">hub</a>' in html_out


# ─── Phase 18.8: keyboard shortcuts cheat-sheet ────────────────────────

def test_shortcuts_modal_component_present_in_app():
    """? key opens a shortcuts cheat-sheet with documented bindings."""
    r = client.get("/static/hub/src/app.jsx")
    assert r.status_code == 200
    src = r.text
    assert "ShortcutsModal" in src
    # The ? keypress toggles the modal.
    assert "'?'" in src or '"?"' in src


def test_shortcuts_modal_lists_known_bindings():
    r = client.get("/static/hub/src/app.jsx")
    src = r.text
    # Each documented shortcut should live in the cheat-sheet payload.
    for key in ("Cmd+K", "Ctrl+K", "Home", "All tools", "Recent", "Pinned"):
        assert key in src, f"shortcuts cheat-sheet missing entry for {key!r}"


# ─── Phase 18.4: pretty error pages ────────────────────────────────────

def test_unknown_tool_returns_pretty_404_with_hub_chrome():
    r = client.get("/tool/this-is-not-a-real-tool")
    assert r.status_code == 404
    assert "text/html" in r.headers["content-type"]
    # Hub chrome markers.
    assert "ProofMark" in r.text
    assert "Return to the hub" in r.text
    # A humane 404 headline, not FastAPI's default JSON.
    assert "404" in r.text
    assert "Not found" in r.text or "not found" in r.text


def test_unknown_top_level_path_returns_pretty_404():
    r = client.get("/this-path-does-not-exist")
    assert r.status_code == 404
    assert "text/html" in r.headers["content-type"]
    assert "ProofMark" in r.text


def test_api_404_stays_json():
    """API routes keep the JSON error contract; only HTML views get chrome."""
    r = client.get("/api/not-a-real-endpoint")
    assert r.status_code == 404
    assert "application/json" in r.headers["content-type"]


def test_error_page_has_meta_description():
    r = client.get("/this-path-does-not-exist")
    assert '<meta name="description"' in r.text


# ─── Display filter: only-live-tiles policy ────────────────────────────

def test_api_tools_defaults_to_live_only_display():
    """By default (PROOFMARK_SHOW_ALL_TILES unset) every entry carries a
    display flag, live=True and beta/planned=False."""
    r = client.get("/api/tools")
    tools = r.json()["tools"]
    assert tools["merge-pdf"]["display"] is True
    # Beta tile (Office-to-PDF requires self-host) stays hidden by default.
    assert tools["word-to-pdf"]["display"] is False
    # Planned workflow tile stays hidden.
    assert tools["project-intake"]["display"] is False


def test_api_tools_display_counts_match_displayed(monkeypatch):
    """counts stays raw-registry; display_counts reflects what users see."""
    monkeypatch.delenv("PROOFMARK_SHOW_ALL_TILES", raising=False)
    payload = client.get("/api/tools").json()
    display_counts = payload["display_counts"]
    # Live-only default: displayed universe = live tools.
    assert display_counts["total"] == display_counts["live"]
    assert display_counts["beta"] == 0
    assert display_counts["planned"] == 0
    # Raw counts preserved (backwards compat with Phase 10.5 contract).
    assert payload["counts"]["beta"] >= 1
    assert payload["counts"]["planned"] >= 1


def test_api_tools_respects_show_all_tiles_env(monkeypatch):
    """Dev/roadmap mode: PROOFMARK_SHOW_ALL_TILES=true reveals beta+planned."""
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/api/tools")
    tools = r.json()["tools"]
    counts = r.json()["counts"]
    assert tools["word-to-pdf"]["display"] is True
    assert tools["project-intake"]["display"] is True
    assert counts["beta"] >= 1
    assert counts["planned"] >= 1


def test_tool_router_404s_beta_by_default():
    """Live-only default — beta tool URLs don't resolve for end users."""
    r = client.get("/tool/word-to-pdf")
    assert r.status_code == 404


def test_tool_router_serves_beta_when_show_all_tiles(monkeypatch):
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/word-to-pdf")
    assert r.status_code == 200
    assert "Word to PDF" in r.text
    assert "Beta" in r.text


def test_sitemap_lists_only_displayed_tools_by_default(monkeypatch):
    monkeypatch.delenv("PROOFMARK_SHOW_ALL_TILES", raising=False)
    r = client.get("/sitemap.xml")
    # Live tool present.
    assert "/tool/merge-pdf" in r.text
    # Beta + planned drop out.
    assert "/tool/word-to-pdf" not in r.text
    assert "/tool/project-intake" not in r.text


def test_sitemap_includes_beta_when_show_all_tiles(monkeypatch):
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/sitemap.xml")
    assert "/tool/word-to-pdf" in r.text


def test_spa_filters_hidden_tiles_in_every_render_surface():
    """After /api/tools sync marks a slug as non-displayed, the SPA must
    drop it from every render path (catalog, palette, sidebar, drawer)."""
    r = client.get("/static/hub/src/app.jsx")
    src = r.text
    # The sync function should flip t.hidden based on server display flag.
    assert "t.hidden" in src
    # Each surface filters hidden tiles before rendering.
    assert "t => !t.hidden" in src or "!t.hidden" in src
    # A render surface that exists today should have been wrapped.
    assert "filter" in src  # sanity — we actually apply filters


def test_feature_flags_is_displayed_defaults_live_only(monkeypatch):
    from proofmark_studio import feature_flags as ff
    monkeypatch.delenv("PROOFMARK_SHOW_ALL_TILES", raising=False)
    assert ff.is_displayed("merge-pdf", {"status": "live"}) is True
    assert ff.is_displayed("word-to-pdf", {"status": "beta"}) is False
    assert ff.is_displayed("project-intake", {"status": "planned"}) is False


def test_feature_flags_is_displayed_honors_per_tool_flag(monkeypatch):
    from proofmark_studio import feature_flags as ff
    monkeypatch.setenv("TOOL_MERGE_PDF_ENABLED", "false")
    assert ff.is_displayed("merge-pdf", {"status": "live"}) is False


def test_feature_flags_show_all_tiles_reveals_wip(monkeypatch):
    from proofmark_studio import feature_flags as ff
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    assert ff.is_displayed("word-to-pdf", {"status": "beta"}) is True
    assert ff.is_displayed("project-intake", {"status": "planned"}) is True


# ─── Phase 18.5: dynamic OG cards ──────────────────────────────────────

def test_og_card_returns_png_for_live_tool():
    r = client.get("/og/merge-pdf.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    # PNG magic header.
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"
    # 1200x630 cards weigh ~20-50KB. Sanity floor — guards against blank renders.
    assert len(r.content) > 4_000


def test_og_card_renders_correct_dimensions():
    """Pillow round-trip — verify the rendered PNG is exactly 1200x630."""
    from io import BytesIO
    from PIL import Image
    r = client.get("/og/merge-pdf.png")
    img = Image.open(BytesIO(r.content))
    assert img.size == (1200, 630)


def test_og_card_carries_cache_headers():
    r = client.get("/og/merge-pdf.png")
    cc = r.headers.get("cache-control", "")
    assert "max-age" in cc
    assert "public" in cc


def test_og_card_falls_back_for_unknown_slug():
    """Unknown slug → brand card so /og/proofmark-studio.png works for content pages."""
    r = client.get("/og/proofmark-studio.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_og_card_renders_for_beta_tool_too(monkeypatch):
    """OG cards are content, not a display surface — even hidden tiles get one."""
    monkeypatch.delenv("PROOFMARK_SHOW_ALL_TILES", raising=False)
    r = client.get("/og/word-to-pdf.png")
    assert r.status_code == 200
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_stub_page_links_og_image(monkeypatch):
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/word-to-pdf")
    assert 'property="og:image" content="/og/word-to-pdf.png"' in r.text
    assert 'name="twitter:card" content="summary_large_image"' in r.text
    assert 'property="og:image:width" content="1200"' in r.text


def test_about_page_links_og_image():
    r = client.get("/about")
    assert 'property="og:image" content="/og/about.png"' in r.text


def test_changelog_page_links_og_image():
    r = client.get("/changelog")
    assert 'property="og:image" content="/og/changelog.png"' in r.text


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


def test_tool_router_stub_for_planned(monkeypatch):
    # Workflow tiles stay `planned` until Phase 17 infra (DB+auth) lands.
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/project-intake")
    assert r.status_code == 200
    assert "Project Intake" in r.text
    assert "Return to the hub" in r.text
    assert "Planned" in r.text


def test_tool_router_stub_for_beta(monkeypatch):
    # Office → PDF stays `beta` until a self-hosted LibreOffice runtime lands.
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
    r = client.get("/tool/word-to-pdf")
    assert r.status_code == 200
    assert "Word to PDF" in r.text
    assert "Beta" in r.text
    assert "Return to the hub" in r.text


def test_tool_router_stub_for_beta_parent_link(monkeypatch):
    """Stub page renders the 'Open parent app' button with hub chrome."""
    monkeypatch.setenv("PROOFMARK_SHOW_ALL_TILES", "true")
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
