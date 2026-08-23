import asyncio
# from mcp_client_test import tavily_mcp_search , get_all_tools
from mcp_client import get_All_tools


if __name__ =="__main__":
    # query = "latest news about AI"
    asyncio.run(get_All_tools())

