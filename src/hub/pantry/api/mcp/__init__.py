from fastmcp import FastMCP

from .recipes import mcp as recipes_mcp

mcp = FastMCP("Pantry MCP")

mcp.mount(recipes_mcp, namespace="recipes")

app = mcp.http_app(path="/mcp")
