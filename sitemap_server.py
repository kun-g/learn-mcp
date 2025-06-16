#!/usr/bin/env python3
"""
Sitemap MCP Server - Parse and analyze XML sitemaps using FastMCP
"""

import json
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse

import requests
import xmltodict
from fastmcp import Context, FastMCP

mcp = FastMCP(
    name="SitemapServer",
    instructions="""Sitemap parser server for analyzing XML sitemaps with update tracking capabilities.

    Available tools:
    - parse_sitemap: Parse sitemap XML and extract URLs
    - analyze_sitemap: Get detailed statistics about a sitemap
    - validate_sitemap: Check if sitemap follows XML sitemap protocol
    - extract_domain_info: Get domain information from sitemap URLs
    - analyze_update_patterns: Analyze website update patterns, frequencies, and recent changes

    Available resources:
    - data://sitemap/{url}: Get cached sitemap data for a URL
    - data://sitemap/updates/{url}: Get detailed update records and patterns from a sitemap

    Supports both standard sitemaps and sitemap index files with comprehensive update tracking.
    """,
)

async def _parse_sitemap_internal(url: str, ctx: Context) -> Dict[str, Any]:
    """
    Internal function to parse sitemap and extract URLs
    """
    try:
        # Fetch the sitemap XML
        await ctx.report_progress(0, 3, "正在下载 sitemap...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        await ctx.report_progress(1, 3, "正在解析 XML...")
        # Parse XML using xmltodict
        parsed_data = xmltodict.parse(response.text)

        await ctx.report_progress(2, 3, "正在提取 URLs...")
        # Extract URLs from parsed data
        urls = _extract_urls(parsed_data)

        await ctx.report_progress(3, 3, f"解析完成，找到 {len(urls)} 个 URLs")

        result = {
            "source_url": url,
            "total_urls": len(urls),
            "urls": urls,
            "sitemap_type": _detect_sitemap_type(parsed_data),
            "success": True
        }

        return result

    except requests.RequestException as e:
        error_msg = f"网络请求错误: {str(e)}"
        ctx.error(error_msg)
        return {"success": False, "error": error_msg, "source_url": url}
    except Exception as e:
        error_msg = f"解析错误: {str(e)}"
        ctx.error(error_msg)
        return {"success": False, "error": error_msg, "source_url": url}

@mcp.tool()
async def parse_sitemap(url: str, ctx: Context) -> Dict[str, Any]:
    """
    Parse a sitemap XML from URL and extract all URLs

    Args:
        url: Sitemap URL to parse

    Returns:
        Dictionary containing parsed URLs and metadata
    """
    ctx.info(f"开始解析 sitemap: {url}")
    result = await _parse_sitemap_internal(url, ctx)

    if result.get("success"):
        ctx.info(f"成功解析 sitemap，共 {result['total_urls']} 个 URLs")

    return result

@mcp.tool()
async def analyze_sitemap(url: str, ctx: Context) -> Dict[str, Any]:
    """
    Analyze sitemap and provide detailed statistics

    Args:
        url: Sitemap URL to analyze

    Returns:
        Detailed analysis including URL patterns, domains, etc.
    """
    ctx.info(f"开始分析 sitemap: {url}")

    # First parse the sitemap
    parse_result = await _parse_sitemap_internal(url, ctx)

    if not parse_result.get("success"):
        return parse_result

    urls = parse_result["urls"]

    # Analyze URL patterns
    domains = {}
    paths = {}
    extensions = {}

    for url_item in urls:
        parsed_url = urlparse(url_item)

        # Count domains
        domain = parsed_url.netloc
        domains[domain] = domains.get(domain, 0) + 1

        # Count path patterns
        path_parts = parsed_url.path.split('/')
        if len(path_parts) > 1:
            first_path = f"/{path_parts[1]}" if path_parts[1] else "/"
            paths[first_path] = paths.get(first_path, 0) + 1

        # Count file extensions
        if '.' in parsed_url.path:
            ext = parsed_url.path.split('.')[-1].lower()
            extensions[ext] = extensions.get(ext, 0) + 1

    analysis = {
        "source_url": url,
        "total_urls": len(urls),
        "unique_domains": len(domains),
        "domain_distribution": dict(sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]),
        "path_patterns": dict(sorted(paths.items(), key=lambda x: x[1], reverse=True)[:10]),
        "file_extensions": dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)),
        "sitemap_type": parse_result["sitemap_type"],
        "success": True
    }

    ctx.info(f"分析完成: {len(urls)} URLs, {len(domains)} 个域名")
    return analysis

@mcp.tool()
async def validate_sitemap(url: str, ctx: Context) -> Dict[str, Any]:
    """
    Validate sitemap against XML sitemap protocol standards

    Args:
        url: Sitemap URL to validate

    Returns:
        Validation results with issues and recommendations
    """
    ctx.info(f"开始验证 sitemap: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        parsed_data = xmltodict.parse(response.text)
        urls = _extract_urls(parsed_data)

        validation_issues = []
        warnings = []

        # Check URL count limit (50,000 URLs per sitemap)
        if len(urls) > 50000:
            validation_issues.append(f"URL数量超限: {len(urls)} > 50,000")

        # Check file size (max 50MB uncompressed)
        content_size = len(response.content)
        if content_size > 50 * 1024 * 1024:
            validation_issues.append(f"文件大小超限: {content_size / (1024*1024):.1f}MB > 50MB")
        elif content_size > 10 * 1024 * 1024:
            warnings.append(f"文件较大: {content_size / (1024*1024):.1f}MB")

        # Check URL format
        invalid_urls = []
        for i, url_item in enumerate(urls[:100]):  # Check first 100 URLs
            if len(url_item) > 2048:
                invalid_urls.append(f"URL #{i+1} 长度超限")
            if not url_item.startswith(('http://', 'https://')):
                invalid_urls.append(f"URL #{i+1} 协议无效")

        if invalid_urls:
            validation_issues.extend(invalid_urls[:5])  # Show first 5 issues

        # Check XML structure
        sitemap_type = _detect_sitemap_type(parsed_data)
        if sitemap_type == "unknown":
            validation_issues.append("无法识别的 sitemap 格式")

        is_valid = len(validation_issues) == 0

        result = {
            "source_url": url,
            "is_valid": is_valid,
            "total_urls": len(urls),
            "file_size_mb": content_size / (1024*1024),
            "sitemap_type": sitemap_type,
            "validation_issues": validation_issues,
            "warnings": warnings,
            "success": True
        }

        status = "有效" if is_valid else "无效"
        ctx.info(f"验证完成: sitemap {status}, {len(validation_issues)} 个问题")
        return result

    except Exception as e:
        error_msg = f"验证失败: {str(e)}"
        ctx.error(error_msg)
        return {"success": False, "error": error_msg, "source_url": url}

@mcp.tool()
async def extract_domain_info(url: str, ctx: Context, limit: int = 10) -> Dict[str, Any]:
    """
    Extract and analyze domain information from sitemap URLs

    Args:
        url: Sitemap URL to analyze
        limit: Maximum number of sample URLs to return per domain

    Returns:
        Domain analysis with sample URLs
    """
    ctx.info(f"开始提取域名信息: {url}")

    parse_result = await _parse_sitemap_internal(url, ctx)

    if not parse_result.get("success"):
        return parse_result

    urls = parse_result["urls"]
    domain_info = {}

    for url_item in urls:
        parsed_url = urlparse(url_item)
        domain = parsed_url.netloc

        if domain not in domain_info:
            domain_info[domain] = {
                "count": 0,
                "sample_urls": [],
                "paths": set(),
                "schemes": set()
            }

        domain_data = domain_info[domain]
        domain_data["count"] += 1
        domain_data["schemes"].add(parsed_url.scheme)
        domain_data["paths"].add(parsed_url.path.split('/')[1] if len(parsed_url.path.split('/')) > 1 else '/')

        if len(domain_data["sample_urls"]) < limit:
            domain_data["sample_urls"].append(url_item)

    # Convert sets to lists for JSON serialization
    for domain, data in domain_info.items():
        data["schemes"] = list(data["schemes"])
        data["paths"] = list(data["paths"])[:20]  # Limit paths to avoid huge responses

    result = {
        "source_url": url,
        "total_urls": len(urls),
        "total_domains": len(domain_info),
        "domains": dict(sorted(domain_info.items(), key=lambda x: x[1]["count"], reverse=True)),
        "success": True
    }

    ctx.info(f"域名分析完成: {len(domain_info)} 个域名")
    return result

@mcp.tool()
async def analyze_update_patterns(url: str, ctx: Context) -> Dict[str, Any]:
    """
    Analyze website update patterns from sitemap

    Args:
        url: Sitemap URL to analyze

    Returns:
        Detailed analysis of update patterns, frequencies, and recent changes
    """
    ctx.info(f"开始分析网站更新模式: {url}")

    try:
        await ctx.report_progress(0, 3, "正在下载并解析 sitemap...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        parsed_data = xmltodict.parse(response.text)
        url_details = _extract_url_details(parsed_data)

        await ctx.report_progress(1, 3, "正在分析更新模式...")
        update_analysis = _analyze_update_patterns(url_details)

        await ctx.report_progress(2, 3, "正在提取最近更新...")
        recent_updates = _get_recent_updates(url_details, limit=50)

        # 分析域名级别的更新模式
        domain_updates = {}
        for item in url_details:
            if item.get('lastmod'):
                parsed_url = urlparse(item['loc'])
                domain = parsed_url.netloc
                if domain not in domain_updates:
                    domain_updates[domain] = {
                        'count': 0,
                        'latest_update': None,
                        'changefreqs': set(),
                        'avg_priority': []
                    }

                domain_updates[domain]['count'] += 1
                if item.get('changefreq'):
                    domain_updates[domain]['changefreqs'].add(item['changefreq'])
                if item.get('priority'):
                    try:
                        domain_updates[domain]['avg_priority'].append(float(item['priority']))
                    except (ValueError, TypeError):
                        pass

                # 更新最新更新时间
                try:
                    lastmod = item['lastmod']
                    if 'T' in lastmod:
                        lastmod_date = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                    else:
                        lastmod_date = datetime.strptime(lastmod, '%Y-%m-%d')

                    if not domain_updates[domain]['latest_update'] or lastmod_date > domain_updates[domain]['latest_update']:
                        domain_updates[domain]['latest_update'] = lastmod_date
                except (ValueError, TypeError):
                    pass

        # 计算平均优先级
        for domain, data in domain_updates.items():
            data['changefreqs'] = list(data['changefreqs'])
            if data['avg_priority']:
                data['avg_priority'] = sum(data['avg_priority']) / len(data['avg_priority'])
            else:
                data['avg_priority'] = None

        await ctx.report_progress(3, 3, "分析完成")

        result = {
            "source_url": url,
            "analyzed_at": datetime.now().isoformat(),
            "sitemap_type": _detect_sitemap_type(parsed_data),
            "total_urls": len(url_details),
            "metadata_coverage": {
                "urls_with_lastmod": sum(1 for item in url_details if item.get('lastmod')),
                "urls_with_changefreq": sum(1 for item in url_details if item.get('changefreq')),
                "urls_with_priority": sum(1 for item in url_details if item.get('priority'))
            },
            "update_patterns": update_analysis,
            "recent_updates": recent_updates[:20],  # 限制返回数量
            "domain_update_summary": dict(sorted(domain_updates.items(), key=lambda x: x[1]['count'], reverse=True)[:10]),
            "success": True
        }

        ctx.info(f"更新模式分析完成: {len(recent_updates)} 个最近更新")
        return result

    except Exception as e:
        error_msg = f"分析失败: {str(e)}"
        ctx.error(error_msg)
        return {"success": False, "error": error_msg, "source_url": url}

def _extract_urls(sitemap_data: Dict[str, Any]) -> List[str]:
    """Extract URLs from parsed sitemap data (legacy function for compatibility)"""
    url_details = _extract_url_details(sitemap_data)
    return [item['loc'] for item in url_details]

def _extract_url_details(sitemap_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract detailed URL information from parsed sitemap data"""
    url_details = []

    # Handle standard sitemap format
    if 'urlset' in sitemap_data:
        urlset = sitemap_data['urlset']
        if 'url' in urlset:
            url_entries = urlset['url']

            if isinstance(url_entries, list):
                for entry in url_entries:
                    if 'loc' in entry:
                        url_info = {
                            'loc': entry['loc'],
                            'lastmod': entry.get('lastmod'),
                            'changefreq': entry.get('changefreq'),
                            'priority': entry.get('priority')
                        }
                        url_details.append(url_info)
            else:
                if 'loc' in url_entries:
                    url_info = {
                        'loc': url_entries['loc'],
                        'lastmod': url_entries.get('lastmod'),
                        'changefreq': url_entries.get('changefreq'),
                        'priority': url_entries.get('priority')
                    }
                    url_details.append(url_info)

    # Handle sitemap index format
    elif 'sitemapindex' in sitemap_data:
        sitemapindex = sitemap_data['sitemapindex']
        if 'sitemap' in sitemapindex:
            sitemap_entries = sitemapindex['sitemap']

            if isinstance(sitemap_entries, list):
                for entry in sitemap_entries:
                    if 'loc' in entry:
                        url_info = {
                            'loc': entry['loc'],
                            'lastmod': entry.get('lastmod'),
                            'changefreq': None,  # Index doesn't typically have changefreq
                            'priority': None     # Index doesn't typically have priority
                        }
                        url_details.append(url_info)
            else:
                if 'loc' in sitemap_entries:
                    url_info = {
                        'loc': sitemap_entries['loc'],
                        'lastmod': sitemap_entries.get('lastmod'),
                        'changefreq': None,
                        'priority': None
                    }
                    url_details.append(url_info)

    return url_details

def _detect_sitemap_type(sitemap_data: Dict[str, Any]) -> str:
    """Detect the type of sitemap"""
    if 'urlset' in sitemap_data:
        return "standard_sitemap"
    elif 'sitemapindex' in sitemap_data:
        return "sitemap_index"
    else:
        return "unknown"

def _analyze_update_patterns(url_details: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze update patterns from URL details"""
    changefreq_stats = {}
    priority_stats = {}
    lastmod_stats = {
        "total_with_lastmod": 0,
        "date_range": {"earliest": None, "latest": None},
        "recent_updates_7d": 0,
        "recent_updates_30d": 0
    }

    now = datetime.now()

    for item in url_details:
        # 分析 changefreq
        changefreq = item.get('changefreq')
        if changefreq:
            changefreq_stats[changefreq] = changefreq_stats.get(changefreq, 0) + 1

        # 分析 priority
        priority = item.get('priority')
        if priority:
            try:
                priority_float = float(priority)
                priority_range = f"{int(priority_float * 10) / 10:.1f}"
                priority_stats[priority_range] = priority_stats.get(priority_range, 0) + 1
            except (ValueError, TypeError):
                pass

        # 分析 lastmod
        lastmod = item.get('lastmod')
        if lastmod:
            lastmod_stats["total_with_lastmod"] += 1
            try:
                # 尝试解析日期格式
                if 'T' in lastmod:
                    lastmod_date = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                else:
                    lastmod_date = datetime.strptime(lastmod, '%Y-%m-%d')

                # 更新日期范围
                if not lastmod_stats["date_range"]["earliest"] or lastmod_date < lastmod_stats["date_range"]["earliest"]:
                    lastmod_stats["date_range"]["earliest"] = lastmod_date
                if not lastmod_stats["date_range"]["latest"] or lastmod_date > lastmod_stats["date_range"]["latest"]:
                    lastmod_stats["date_range"]["latest"] = lastmod_date

                # 计算最近更新
                days_diff = (now - lastmod_date).days
                if days_diff <= 7:
                    lastmod_stats["recent_updates_7d"] += 1
                if days_diff <= 30:
                    lastmod_stats["recent_updates_30d"] += 1

            except (ValueError, TypeError):
                pass

    return {
        "changefreq_distribution": changefreq_stats,
        "priority_distribution": priority_stats,
        "lastmod_analysis": lastmod_stats
    }

def _get_recent_updates(url_details: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent updates sorted by lastmod date"""
    updates_with_dates = []

    for item in url_details:
        lastmod = item.get('lastmod')
        if lastmod:
            try:
                if 'T' in lastmod:
                    lastmod_date = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                else:
                    lastmod_date = datetime.strptime(lastmod, '%Y-%m-%d')

                updates_with_dates.append({
                    'url': item['loc'],
                    'lastmod': lastmod,
                    'lastmod_parsed': lastmod_date,
                    'changefreq': item.get('changefreq'),
                    'priority': item.get('priority')
                })
            except (ValueError, TypeError):
                pass

    # 按日期排序，最新的在前
    updates_with_dates.sort(key=lambda x: x['lastmod_parsed'], reverse=True)

    # 移除 lastmod_parsed 字段并返回前 N 个
    result = []
    for item in updates_with_dates[:limit]:
        result_item = {k: v for k, v in item.items() if k != 'lastmod_parsed'}
        result.append(result_item)

    return result

@mcp.resource("data://sitemap/{url}")
def get_sitemap_data(url: str) -> str:
    """
    Get cached sitemap data for a URL
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        parsed_data = xmltodict.parse(response.text)
        urls = _extract_urls(parsed_data)

        cache_data = {
            "url": url,
            "cached_at": "2024-01-01T00:00:00Z",  # This would be current timestamp in real implementation
            "total_urls": len(urls),
            "sitemap_type": _detect_sitemap_type(parsed_data),
            "first_10_urls": urls[:10]
        }

        return json.dumps(cache_data, indent=2, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

@mcp.resource("data://sitemap/updates/{url}")
def get_sitemap_updates(url: str) -> str:
    """
    Get detailed update records and patterns from a sitemap
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        parsed_data = xmltodict.parse(response.text)
        url_details = _extract_url_details(parsed_data)

        # 分析更新模式
        update_analysis = _analyze_update_patterns(url_details)

        update_data = {
            "url": url,
            "analyzed_at": datetime.now().isoformat(),
            "sitemap_type": _detect_sitemap_type(parsed_data),
            "total_urls": len(url_details),
            "urls_with_lastmod": sum(1 for item in url_details if item.get('lastmod')),
            "urls_with_changefreq": sum(1 for item in url_details if item.get('changefreq')),
            "urls_with_priority": sum(1 for item in url_details if item.get('priority')),
            "update_patterns": update_analysis,
            "recent_updates": _get_recent_updates(url_details, limit=20),
            "sample_urls_with_metadata": url_details[:10]
        }

        return json.dumps(update_data, indent=2, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
