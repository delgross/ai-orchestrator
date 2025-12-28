# Static Resources Integration

## Overview

The Static Resources feature allows LLMs to access organizational knowledge, guidelines, definitions, and best practices stored in the `Static Resources` directory. This is integrated as a tool that LLMs can call during task execution.

## Directory Structure

Static resources are stored in:
```
agent_fs_root/Static Resources/
```

Currently contains:
- `Git Best Practices.md` - Git workflow and best practices

## Supported File Types

The tool automatically discovers and indexes:
- `.md` - Markdown files
- `.txt` - Plain text files
- `.rst` - reStructuredText files
- `.adoc` - AsciiDoc files

## How It Works

### For LLMs

When an LLM needs to consult guidelines or best practices, it can use the `query_static_resources` tool in three ways:

1. **List all resources**: `query_static_resources(list_all=True)`
   - Returns a list of all available resources with metadata

2. **Search by keyword**: `query_static_resources(query="git")`
   - Searches both filenames and content for the keyword
   - Returns matching resources with snippets showing where the keyword appears

3. **Retrieve specific resource**: `query_static_resources(resource_name="Git Best Practices.md")`
   - Returns the full content of a specific resource file
   - Content is truncated at 50,000 characters by default (configurable)

### System Prompt Integration

The system prompt has been updated to instruct LLMs to use this tool when they need to:
- Follow organizational standards
- Look up definitions
- Consult best practices
- Reference guidelines

## Example Usage

When an LLM receives a task like "Create a git commit following best practices", it will:

1. Call `query_static_resources(query="git commit")` to find relevant guidelines
2. Review the returned content
3. Apply those guidelines when creating the commit

## Adding New Resources

Simply add files to the `Static Resources` directory:

```bash
# Add a new guideline file
cp my-guideline.md ~/ai/agent_fs_root/Static\ Resources/

# The tool will automatically discover it on the next query
```

## Future Enhancements

This is a preliminary implementation before the RAG server is set up. Future improvements may include:

- Automatic indexing into the RAG system
- Semantic search capabilities
- Version tracking of resources
- Resource categorization and tagging
- Usage analytics

## Technical Details

- **Tool Name**: `query_static_resources`
- **Implementation**: `tool_query_static_resources()` in `agent_runner.py`
- **Tool Registration**: Added to `FILE_TOOLS` and `TOOL_IMPLS`
- **System Prompt**: Updated to mention the tool in the tool usage section






