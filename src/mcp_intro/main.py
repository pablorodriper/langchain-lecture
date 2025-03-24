import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

import dotenv
dotenv.load_dotenv()

from langchain_ollama import ChatOllama
model = ChatOllama(model="llama3.2:3b")

# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="gpt-4o-mini")

async def execute_query():
    async with MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8083/sse",
                "transport": "sse",
            },
            "math": {
                "url": "http://localhost:8082/sse",
                "transport": "sse",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        # math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
        # print([msg.pretty_print() for msg in math_response["messages"]])
        print([msg.pretty_print() for msg in weather_response["messages"]])


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(execute_query())
    loop.close()

if __name__ == '__main__':
    main()