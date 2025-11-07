# Notion Project Ideas Generator Agent

An AI-powered agent that helps users generate portfolio project ideas through Notion integration. Perfect for students targeting internships and building their technical portfolio.

## Features

- Generates project ideas across multiple difficulty levels (Beginner, Intermediate, Advanced)
- Integrates directly with your Notion workspace
- Focuses on technically valuable and resume-worthy projects

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your API keys:
    - Notion API key: https://www.notion.so/profile/integrations (create a new integration -> copy the secret key -> add your notion page in the access section for the agent to read/write content)

    - OpenAI API key: https://platform.openai.com/account/api-keys (create a new secret key)

3. Set up environment variables:
   - Create a `.env` file
   - Add your Notion API key:
```bash
NOTION_API=your_notion_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the agent:
```bash
python notion_agent.py
```

## Usage

1. Start the agent and wait for the connection to Notion
2. Input your project requirements or preferences
3. The agent will generate and organize ideas directly in your Notion workspace
4. Type 'e' to exit

## Agent Instructions
#### if you'd like to build your own Notion MCP agent for different task, you can change the prompts.md file to customize the agent's behavior.

## Requirements

- Python 3.7+
- Notion API access
- Node.js (for Notion MCP server)