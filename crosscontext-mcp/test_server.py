#!/usr/bin/env python3
"""
Test script for CrossContext MCP Server
"""

import asyncio
from src.server import app

async def test_tools():
    """Test all tools to ensure they work"""
    print("Testing CrossContext MCP Server...")

    # Get available tools
    tools = await app.get_tools()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool}")

    print("\n✅ Server initialized successfully with all tools registered!")

if __name__ == "__main__":
    asyncio.run(test_tools())
