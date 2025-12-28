# AI Orchestrator: MCP Tools & Capabilities

This file serves as a reference for all available MCP servers currently integrated into the AI Orchestrator. Each server provides specialized tools that can be used by your LLMs.

---

## 1. Perplexity AI (`perplexity`)
**Description**: Perplexity is a powerful research engine that provides up-to-date information with real-world citations. It excels at deep technical analysis, real-time news retrieval, and strategic reasoning. Use this when you need accurate, cited facts from across the web.
*   **Tools**: `perplexity_ask`, `perplexity_research`, `perplexity_reason`, `perplexity_search`
*   **Workflow Hint**: Ask the agent to "use Perplexity research" for complex technical topics or "Perplexity search" for the absolute latest breaking news.

## 2. Exa Neural Search (`exa`)
**Description**: Exa is a search engine designed specifically for AI models, using neural embeddings to find high-quality web content. It is exceptionally good at finding specific data points, like current stock prices, technical documentation, or niche articles. It bypasses traditional SEO noise to find the most relevant results.
*   **Tools**: `web_search_exa`, `get_code_context_exa`
*   **Workflow Hint**: Use Exa when you need high-precision data like "latest Apple stock price" or specific code snippets from GitHub.

## 3. Playwright Web Browser (`playwright`)
**Description**: Provides a fully automated headless browser that the agent can control to interact with the live web. It can navigate pages, fill out forms, take screenshots, and extract data from dynamic JavaScript-heavy sites. This is your "remote hand" for the internet.
*   **Tools**: `browser_navigate`, `browser_click`, `browser_type`, `browser_take_screenshot`, `browser_snapshot`, `browser_evaluate`, etc. (22 total tools)
*   **Workflow Hint**: Ask the agent to "navigate to [URL] and take a screenshot" to verify a site's layout or "fill out the login form" for complex automated tasks.

## 4. MacOS Automator (`macos_automator`)
**Description**: A bridge to your local Mac system that allows the AI to control applications and automate OS-level tasks. It can execute AppleScript and JXA (JavaScript for Automation) to interact with apps like Calendar, Mail, or System Settings. It provides a direct interface for local computer control.
*   **Tools**: `execute_script`, `get_scripting_tips`
*   **Workflow Hint**: Use this to automate local tasks like "create a new calendar event for 2pm tomorrow" or "get the current volume level of my Mac."

## 5. Firecrawl Scraper (`firecrawl-mcp`)
**Description**: Specialized in deep web crawling and scraping, turning entire websites into clean, LLM-ready markdown. It can handle complex site maps and perform recursive crawls to build a comprehensive knowledge base from a domain. It is ideal for gathering large amounts of data for RAG.
*   **Tools**: `firecrawl_scrape`, `firecrawl_search`, `firecrawl_crawl`, `firecrawl_extract`, `firecrawl_map`
*   **Workflow Hint**: Use `firecrawl_scrape` when you want the full, clean text of a long article or `firecrawl_crawl` to index an entire documentation site.

## 6. Scrapezy Structured Extraction (`scrapezy`)
**Description**: A specialized extraction engine that uses AI to turn messy web pages into perfectly structured JSON data. It is highly effective at identifying schemas within pages, such as product lists, job postings, or real estate data. It ensures that the data returned to the LLM is organized and consistent.
*   **Tools**: `extract_structured_data`
*   **Workflow Hint**: Ask the agent to "extract product details as JSON" from a shopping site using Scrapezy for highly predictable results.

## 7. Sequential Thinking (`thinking`)
**Description**: A reasoning-enhancement tool that provides a structured "Chain of Thought" scratchpad for the LLM. It forces the model to break down complex problems into logical steps before attempting a final answer. This drastically reduces logic errors and tool-calling hallucinations.
*   **Tools**: `sequentialthinking`
*   **Workflow Hint**: The agent will naturally use this for difficult logic puzzles or complex multi-step research tasks. You can prompt it to "think through the steps carefully" to trigger it.

## 8. Tavily AI Search (`tavily-search`)
**Description**: A high-speed search engine optimized for LLMs that provides concise, relevant search snippets. It is a reliable alternative to Exa and Perplexity for general knowledge queries and quick facts. It helps ground the agent in current events with minimal latency.
*   **Tools**: `tavily_search`, `tavily_extract`
*   **Workflow Hint**: Use Tavily for quick fact-checking or general info queries where speed is more important than deep citations.

## 9. Pandoc Document Converter (`mcp-pandoc`)
**Description**: A powerful document conversion engine that can transform between dozens of file formats (Markdown, PDF, DOCX, etc.). It allows the agent to process and generate complex documents while maintaining formatting. It is the core tool for the orchestrator's "document assistant" capabilities.
*   **Tools**: `convert_contents`
*   **Workflow Hint**: Ask the agent to "convert my README.md to a PDF" or "read this DOCX file" to utilize Pandoc's processing power.










