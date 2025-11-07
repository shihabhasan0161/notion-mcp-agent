import os
import asyncio
from dotenv import load_dotenv
from agents.mcp.server import MCPServerStdio, MCPServer
from agents import Agent, Runner, gen_trace_id, trace, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent


# Load environment variables
def load_env():
    load_dotenv()

    notion_api = os.getenv("NOTION_API")

    if not notion_api:
        raise ValueError("NOTION_API is required")

    return notion_api


# Get the instructions from prompts.md
def load_prompts():
    try:
        with open("prompts.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError("prompts.md file not found")


async def create_mcp_server(notion_api: str) -> MCPServerStdio:
    """Create and return an MCP server connection for Notion."""
    return MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@notionhq/notion-mcp-server"],
            "env": {
                "OPENAPI_MCP_HEADERS": f'{{"Authorization": "Bearer {notion_api}", "Notion-Version": "2022-06-28"}}'
            },
        }
    )


async def run_agent(mcp_server: MCPServer, prompts: str):

    # create the agent
    agent = Agent(
        name="Notion Agent",
        model="gpt-4.1-2025-04-14",
        instructions=prompts,
        mcp_servers=[mcp_server],
    )
    ModelSettings.tool_choice = "required"

    # Store conversation history
    input_items = []

    print("*** Notion MCP Agent ***")
    print("Enter e to exit")

    while True:
        try:
            user_input = input("User Input: ")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        # Add user input to input_items
        input_items.append({"content": user_input, "role": "user"})

        if user_input.lower() == "e":
            print("Exiting...")
            break

        if not user_input.strip():
            print("Please write something or enter 'e' to exit.")
            continue

        print("\nAgent: ", end="", flush=True)

        try:
            # Run the agent with streaming
            result = Runner.run_streamed(
                agent,
                input=input_items,
            )
            
            # Process streaming events
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    # Print text deltas as they come in
                    print(event.data.delta, end="", flush=True)
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        print(f"\n-- Calling Tool: {event.item.raw_item.name}...")
                    elif event.item.type == "tool_call_output_item":
                        print("-- Tool call completed.")
                    elif event.item.type == "message_output_item":
                        # Add assistant response to conversation history
                        input_items.append({
                            "content": f"{event.item.raw_item.content[0].text}", 
                            "role": "assistant"
                        })

            print("\n")
            print("\n if you want to exit, type 'e'.")

        except Exception as e:
            print(f"\nError occurred: {e}")
            print("Please try again or type 'e' to quit.")


async def main():
    try:
        notion_api = load_env()
        prompts = load_prompts()

        # Create MCP server connection
        async with await create_mcp_server(notion_api) as mcp:

            # Generate trace id
            trace_id = gen_trace_id()
            with trace(workflow_name="Notion MCP Agent", trace_id=trace_id):
                print(f"Trace URL: https://platform.openai.com/traces/trace?trace_id={trace_id}")


            # List MCP tools
            tools = await mcp.list_tools()
            print(f"Connected to {len(tools)} MCP tools:")

            await run_agent(mcp, prompts)

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
