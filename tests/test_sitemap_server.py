"""
Unit tests for sitemap_server.py
"""
from unittest.mock import Mock, patch

import pytest

from sitemap_server import (
    _detect_sitemap_type,
    _extract_urls,
    _parse_sitemap_internal,
)


class TestExtractUrls:
    """Test the _extract_urls helper function"""

    def test_extract_urls_standard_sitemap(self):
        """Test URL extraction from standard sitemap"""
        sitemap_data = {
            "urlset": {
                "url": [
                    {"loc": "https://example.com/page1"},
                    {"loc": "https://example.com/page2"}
                ]
            }
        }

        urls = _extract_urls(sitemap_data)
        assert len(urls) == 2
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls

    def test_extract_urls_single_url(self):
        """Test URL extraction from sitemap with single URL"""
        sitemap_data = {
            "urlset": {
                "url": {"loc": "https://example.com/page1"}
            }
        }

        urls = _extract_urls(sitemap_data)
        assert len(urls) == 1
        assert urls[0] == "https://example.com/page1"

    def test_extract_urls_sitemap_index(self):
        """Test URL extraction from sitemap index"""
        sitemap_data = {
            "sitemapindex": {
                "sitemap": [
                    {"loc": "https://example.com/sitemap1.xml"},
                    {"loc": "https://example.com/sitemap2.xml"}
                ]
            }
        }

        urls = _extract_urls(sitemap_data)
        assert len(urls) == 2
        assert "https://example.com/sitemap1.xml" in urls
        assert "https://example.com/sitemap2.xml" in urls

    def test_extract_urls_empty_sitemap(self):
        """Test URL extraction from empty sitemap"""
        sitemap_data = {}
        urls = _extract_urls(sitemap_data)
        assert urls == []


class TestDetectSitemapType:
    """Test the _detect_sitemap_type helper function"""

    def test_detect_standard_sitemap(self):
        """Test detection of standard sitemap"""
        sitemap_data = {"urlset": {}}
        assert _detect_sitemap_type(sitemap_data) == "standard_sitemap"

    def test_detect_sitemap_index(self):
        """Test detection of sitemap index"""
        sitemap_data = {"sitemapindex": {}}
        assert _detect_sitemap_type(sitemap_data) == "sitemap_index"

    def test_detect_unknown_type(self):
        """Test detection of unknown sitemap type"""
        sitemap_data = {"unknown": {}}
        assert _detect_sitemap_type(sitemap_data) == "unknown"


class TestParseSitemapInternal:
    """Test the _parse_sitemap_internal function"""

    @pytest.mark.asyncio
    @patch('sitemap_server.requests.get')
    @patch('sitemap_server.xmltodict.parse')
    async def test_parse_sitemap_success(self, mock_xmlparse, mock_get, mock_context, sample_sitemap_xml):
        """Test successful sitemap parsing"""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = sample_sitemap_xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_xmlparse.return_value = {
            "urlset": {
                "url": [
                    {"loc": "https://example.com/page1"},
                    {"loc": "https://example.com/page2"}
                ]
            }
        }

        result = await _parse_sitemap_internal("https://example.com/sitemap.xml", mock_context)

        assert result["success"] is True
        assert result["total_urls"] == 2
        assert result["sitemap_type"] == "standard_sitemap"
        assert "https://example.com/page1" in result["urls"]

    @pytest.mark.asyncio
    @patch('sitemap_server.requests.get')
    async def test_parse_sitemap_network_error(self, mock_get, mock_context):
        """Test sitemap parsing with network error"""
        mock_get.side_effect = Exception("Network error")

        result = await _parse_sitemap_internal("https://example.com/sitemap.xml", mock_context)

        assert result["success"] is False
        assert "解析错误" in result["error"]

    @pytest.mark.asyncio
    @patch('sitemap_server.requests.get')
    async def test_parse_sitemap_http_error(self, mock_get, mock_context):
        """Test sitemap parsing with HTTP error"""
        from requests import RequestException
        mock_get.side_effect = RequestException("HTTP 404")

        result = await _parse_sitemap_internal("https://example.com/sitemap.xml", mock_context)

        assert result["success"] is False
        assert "网络请求错误" in result["error"]


# Note: MCP tool tests are skipped due to FastMCP decorator complexity
# The core functionality is tested through the internal functions above
