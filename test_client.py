#!/usr/bin/env python3
"""
测试客户端 - 验证 Sitemap MCP Server 的认证功能
"""

import asyncio
import os
import sys
from typing import Dict, Any

# 注意: 这是一个简化的测试客户端
# 在实际应用中，你可能需要使用 FastMCP 的官方客户端库

async def test_http_connection():
    """测试 HTTP 连接和认证"""
    print("=" * 50)
    print("Sitemap MCP Server 认证测试")
    print("=" * 50)
    
    # 测试配置
    server_host = "127.0.0.1"
    server_port = 9000
    test_url = "https://example.com/sitemap.xml"
    
    print(f"服务器地址: {server_host}:{server_port}")
    print(f"测试 URL: {test_url}")
    print()
    
    # 模拟不同的认证场景
    scenarios = [
        {
            "name": "无认证测试",
            "description": "测试在没有API Key的情况下调用工具",
            "api_key": None,
            "should_succeed": True,  # 我们的简化实现允许无认证访问
        },
        {
            "name": "有效认证测试", 
            "description": "测试使用有效API Key调用工具",
            "api_key": "test-api-key-12345",
            "should_succeed": True,
        },
    ]
    
    for scenario in scenarios:
        print(f"场景: {scenario['name']}")
        print(f"描述: {scenario['description']}")
        
        if scenario['api_key']:
            print(f"API Key: {scenario['api_key']}")
        else:
            print("API Key: 未设置")
        
        try:
            result = await simulate_mcp_call(
                host=server_host,
                port=server_port,
                tool_name="analyze_update_patterns",
                params={"url": test_url},
                api_key=scenario['api_key']
            )
            
            if scenario['should_succeed']:
                print("✅ 调用成功（符合预期）")
            else:
                print("❌ 调用成功但不应该成功")
                
        except Exception as e:
            if not scenario['should_succeed']:
                print("✅ 调用失败（符合预期）")
                print(f"   错误: {e}")
            else:
                print("❌ 调用失败但应该成功")
                print(f"   错误: {e}")
        
        print("-" * 30)
        print()

async def simulate_mcp_call(host: str, port: int, tool_name: str, params: Dict[str, Any], api_key: str = None):
    """
    模拟 MCP 工具调用
    注意: 这是一个简化的实现，实际应该使用 FastMCP Client
    """
    import aiohttp
    
    # 构建请求
    url = f"http://{host}:{port}/mcp"  # 这是假设的 endpoint
    headers = {
        "Content-Type": "application/json",
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # MCP 请求格式（简化）
    payload = {
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params
        }
    }
    
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result
            elif response.status == 401:
                raise Exception("认证失败: 未授权访问")
            elif response.status == 403:
                raise Exception("认证失败: 权限不足")
            else:
                raise Exception(f"HTTP 错误: {response.status}")

def print_usage():
    """打印使用说明"""
    print("使用说明:")
    print("1. 启动服务器（HTTP 模式）:")
    print("   MCP_TRANSPORT=http MCP_PORT=9000 python sitemap_server.py")
    print()
    print("2. 启动服务器（带认证）:")
    print("   MCP_TRANSPORT=http MCP_PORT=9000 MCP_API_KEY=test-api-key-12345 python sitemap_server.py")
    print()
    print("3. 运行此测试客户端:")
    print("   python test_client.py")
    print()

async def check_server_running(host: str, port: int) -> bool:
    """检查服务器是否运行"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # 尝试连接服务器
            async with session.get(f"http://{host}:{port}/health", timeout=2) as response:
                return True
    except:
        return False

async def main():
    """主函数"""
    print_usage()
    
    # 检查服务器是否运行
    server_running = await check_server_running("127.0.0.1", 9000)
    
    if not server_running:
        print("⚠️  警告: 服务器似乎没有在 127.0.0.1:9000 运行")
        print("请先启动 sitemap_server.py（HTTP 模式）")
        print()
        
        response = input("是否继续测试? (y/n): ")
        if response.lower() != 'y':
            print("测试已取消")
            return
    
    # 运行测试
    await test_http_connection()
    
    print("=" * 50)
    print("测试完成")
    print()
    print("注意: 这是一个简化的测试客户端")
    print("实际应用中应该使用 FastMCP 的官方客户端库")

if __name__ == "__main__":
    # 检查依赖
    try:
        import aiohttp
    except ImportError:
        print("错误: 需要安装 aiohttp")
        print("运行: pip install aiohttp")
        sys.exit(1)
    
    # 运行测试
    asyncio.run(main())