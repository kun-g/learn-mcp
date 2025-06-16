"""
Pytest configuration and fixtures
"""
from unittest.mock import AsyncMock, Mock

import pytest
from fastmcp import Context


@pytest.fixture
def mock_context():
    """Mock FastMCP Context for testing"""
    ctx = Mock(spec=Context)
    ctx.info = AsyncMock()
    ctx.error = AsyncMock()
    ctx.report_progress = AsyncMock()
    ctx.read_resource = AsyncMock()
    return ctx


@pytest.fixture
def sample_sitemap_xml():
    """Sample sitemap XML for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
        <lastmod>2024-01-02</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""


@pytest.fixture
def sample_sitemap_index_xml():
    """Sample sitemap index XML for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://example.com/sitemap1.xml</loc>
        <lastmod>2024-01-01T00:00:00Z</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://example.com/sitemap2.xml</loc>
        <lastmod>2024-01-02T00:00:00Z</lastmod>
    </sitemap>
</sitemapindex>"""
