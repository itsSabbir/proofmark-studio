from fastapi.testclient import TestClient

from web_app import APP_NAME, app


client = TestClient(app)


def test_home_page_renders_core_links():
    response = client.get("/")
    assert response.status_code == 200
    assert APP_NAME in response.text
    assert "Proofmark PDF" in response.text
    assert "Proofmark Text Inspection Studio" in response.text
    assert "Proofmark site" in response.text
    assert "target='_blank'" not in response.text


def test_health_endpoint_reports_service():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "proofmark-studio"


def test_hub_redirects_route_directly():
    response = client.get("/go/proofmark-pdf", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert response.headers["location"].endswith(":8010")


def test_studio_map_api_exposes_spokes():
    response = client.get("/api/studio-map")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "proofmark-studio"
    assert len(payload["spokes"]) >= 4


def test_stub_tool_page_renders():
    response = client.get("/tools/html-to-pdf")
    assert response.status_code == 200
    assert "HTML to PDF" in response.text
    assert "reserved inside Proofmark Studio" in response.text


def test_unknown_tool_page_returns_404():
    response = client.get("/tools/not-a-real-tool")
    assert response.status_code == 404


def test_policy_pages_render():
    privacy = client.get("/privacy")
    terms = client.get("/terms")
    assert privacy.status_code == 200
    assert terms.status_code == 200
    assert "Privacy Policy" in privacy.text
    assert "Terms of Use" in terms.text


def test_search_support_files_render():
    robots = client.get("/robots.txt")
    sitemap = client.get("/sitemap.xml")
    assert robots.status_code == 200
    assert "Sitemap:" in robots.text
    assert sitemap.status_code == 200
    assert "<urlset" in sitemap.text
