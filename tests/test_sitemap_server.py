"""
Unit tests for sitemap_server.py
"""
from unittest.mock import Mock, patch

import pytest

from sitemap_server import (
    _analyze_update_patterns,
    _detect_sitemap_type,
    _extract_url_details,
    _extract_urls,
    _get_recent_updates,
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


class TestExtractUrlDetails:
    """Test the _extract_url_details helper function"""

    def test_extract_url_details_with_metadata(self):
        """Test URL details extraction with full metadata"""
        sitemap_data = {
            "urlset": {
                "url": [
                    {
                        "loc": "https://example.com/page1",
                        "lastmod": "2024-01-01",
                        "changefreq": "daily",
                        "priority": "0.8"
                    },
                    {
                        "loc": "https://example.com/page2",
                        "lastmod": "2024-01-02",
                        "changefreq": "weekly",
                        "priority": "0.6"
                    }
                ]
            }
        }

        url_details = _extract_url_details(sitemap_data)
        assert len(url_details) == 2
        
        first_url = url_details[0]
        assert first_url['loc'] == "https://example.com/page1"
        assert first_url['lastmod'] == "2024-01-01"
        assert first_url['changefreq'] == "daily"
        assert first_url['priority'] == "0.8"

    def test_extract_url_details_partial_metadata(self):
        """Test URL details extraction with partial metadata"""
        sitemap_data = {
            "urlset": {
                "url": {
                    "loc": "https://example.com/page1",
                    "lastmod": "2024-01-01"
                    # Missing changefreq and priority
                }
            }
        }

        url_details = _extract_url_details(sitemap_data)
        assert len(url_details) == 1
        
        url_info = url_details[0]
        assert url_info['loc'] == "https://example.com/page1"
        assert url_info['lastmod'] == "2024-01-01"
        assert url_info['changefreq'] is None
        assert url_info['priority'] is None


class TestAnalyzeUpdatePatterns:
    """Test the _analyze_update_patterns helper function"""

    def test_analyze_update_patterns_with_data(self):
        """Test update pattern analysis with sample data"""
        url_details = [
            {
                'loc': 'https://example.com/page1',
                'lastmod': '2024-01-01',
                'changefreq': 'daily',
                'priority': '0.8'
            },
            {
                'loc': 'https://example.com/page2',
                'lastmod': '2024-01-02',
                'changefreq': 'weekly',
                'priority': '0.6'
            },
            {
                'loc': 'https://example.com/page3',
                'lastmod': '2024-01-03',
                'changefreq': 'daily',
                'priority': '0.7'
            }
        ]

        with patch('sitemap_server.datetime') as mock_datetime:
            from datetime import datetime
            mock_datetime.now.return_value = datetime(2024, 1, 10)
            mock_datetime.strptime = datetime.strptime
            
            result = _analyze_update_patterns(url_details)

        assert 'changefreq_distribution' in result
        assert 'priority_distribution' in result
        assert 'lastmod_analysis' in result
        
        # Check changefreq distribution
        assert result['changefreq_distribution']['daily'] == 2
        assert result['changefreq_distribution']['weekly'] == 1
        
        # Check lastmod analysis
        assert result['lastmod_analysis']['total_with_lastmod'] == 3

    def test_analyze_update_patterns_empty_data(self):
        """Test update pattern analysis with empty data"""
        url_details = []
        
        result = _analyze_update_patterns(url_details)
        
        assert result['changefreq_distribution'] == {}
        assert result['priority_distribution'] == {}
        assert result['lastmod_analysis']['total_with_lastmod'] == 0


class TestGetRecentUpdates:
    """Test the _get_recent_updates helper function"""

    def test_get_recent_updates_sorted(self):
        """Test recent updates are sorted correctly"""
        url_details = [
            {
                'loc': 'https://example.com/page1',
                'lastmod': '2024-01-01',
                'changefreq': 'daily',
                'priority': '0.8'
            },
            {
                'loc': 'https://example.com/page2',
                'lastmod': '2024-01-03',  # Most recent
                'changefreq': 'weekly',
                'priority': '0.6'
            },
            {
                'loc': 'https://example.com/page3',
                'lastmod': '2024-01-02',  # Middle
                'changefreq': 'daily',
                'priority': '0.7'
            }
        ]
        
        recent_updates = _get_recent_updates(url_details, limit=10)
        
        assert len(recent_updates) == 3
        # Should be sorted by lastmod date, most recent first
        assert recent_updates[0]['url'] == 'https://example.com/page2'
        assert recent_updates[1]['url'] == 'https://example.com/page3'
        assert recent_updates[2]['url'] == 'https://example.com/page1'

    def test_get_recent_updates_limit(self):
        """Test recent updates respects limit"""
        url_details = [
            {'loc': f'https://example.com/page{i}', 'lastmod': f'2024-01-{i:02d}'}
            for i in range(1, 6)  # 5 URLs
        ]
        
        recent_updates = _get_recent_updates(url_details, limit=3)
        
        assert len(recent_updates) == 3
        # Should get the 3 most recent
        assert recent_updates[0]['url'] == 'https://example.com/page5'
        assert recent_updates[1]['url'] == 'https://example.com/page4'
        assert recent_updates[2]['url'] == 'https://example.com/page3'

    def test_get_recent_updates_no_lastmod(self):
        """Test recent updates with URLs missing lastmod"""
        url_details = [
            {'loc': 'https://example.com/page1'},  # No lastmod
            {'loc': 'https://example.com/page2', 'lastmod': '2024-01-01'},
            {'loc': 'https://example.com/page3'}   # No lastmod
        ]
        
        recent_updates = _get_recent_updates(url_details, limit=10)
        
        # Should only include URLs with lastmod
        assert len(recent_updates) == 1
        assert recent_updates[0]['url'] == 'https://example.com/page2'


# Note: MCP tool tests are skipped due to FastMCP decorator complexity
# The core functionality is tested through the internal functions above
