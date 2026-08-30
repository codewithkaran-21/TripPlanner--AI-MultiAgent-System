import os 
import certifi 
import sys
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from pathlib import Path
from langchain_groq import ChatGroq

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROJECT_DIR = Path(__file__).resolve().parent
WEATHER_SERVER_PATH = PROJECT_DIR / "custom_weather_mcp_server.py"



# Preserve the complete Windows environment when starting
# local stdio MCP servers.
AVIATION_ENV = os.environ.copy()
AVIATION_ENV["AVIATION_STACK_API_KEY"] = (
    AVIATION_STACK_API_KEY or ""
)


WEATHER_ENV = os.environ.copy()
WEATHER_ENV["OPENWEATHER_API_KEY"] = (
    OPENWEATHER_API_KEY or ""
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)



client = MultiServerMCPClient(
    {
       "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "aviationstack-mcp"
            ],
            "env": AVIATION_ENV
        },

        "weather" : {
            "transport" : "stdio",

            # Use the same Python environment that runs app.py.
            "command" : sys.executable,

            # Automatically use custom_weather_mcp_server.py
            # from the current project directory.
            "args": [
                str(WEATHER_SERVER_PATH)
            ],

            "env": WEATHER_ENV
        }
  
    }
)


async def get_all_tools():
    """
    Load each MCP server separately.

    A broken server will no longer prevent the other
    working servers from loading.
    """
    
    tools = await client.get_tools()
    print("\nAvailable MCP Tools:\n")

    for tool in tools:
        print(tool.name)   


search_tool = None 
aviation_tools = None

async def initialize_mcp():
    global search_tool 
    global aviation_tools

    if search_tool is not None and aviation_tools :
        return 

    tools = await client.get_tools()

    print("\nAvailaible MCP Tools\n")
    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = next(
            tool
            for tool in tools
            if tool.name != "tavily_search"
        )


async def tavily_mcp_search(query : str):
    await initialize_mcp()
    result = await search_tool.ainvoke({
        "query":query
    })

    return result
    # print(result)


async def aviation_mcp_call():
    tool_name : str 
    tool_args : dict = None 

    tool = await client.get_tools()

    tool = next(
        t for  t in tool
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result

