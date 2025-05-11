# MCP Code Server

A Model Context Protocol (MCP) server that provides advanced code exploration, search, and analysis capabilities for software projects. This server acts as a bridge between AI assistants and your codebase, enabling intelligent code navigation and understanding.

## Features

### 🔍 Code Search & Navigation
- **Symbol Search**: Find classes, functions, and imports across your codebase
- **Definition Finder**: Quickly locate where symbols are defined
- **Reference Finder**: Discover all references to specific symbols
- **Advanced Text Search**: Search with regex support, whole word matching, and context display

### 📁 File Explorer
- **Project Exploration**: Analyze project structure and file types
- **File Reading**: Read file contents with line range selection
- **Directory Listing**: Browse files and directories with filtering options
- **Code-specific Search**: Search within specific file patterns

### 📊 Code Analysis
- **File Metrics**: Analyze code complexity, function counts, and more
- **Import Analysis**: Track dependencies and import relationships
- **Pattern Matching**: Find specific code patterns using regex
- **Code Statistics**: Get insights into your codebase structure

## Installation

Install the MCP Code Server using the included installation script:

```bash
uv venv
```

```bash
uv sync
```

```bash
uv run mcp install Central_Server.py
```

## Usage

Once installed, the server provides the following tools that can be used by AI assistants:

### Core Functions

| Tool | Description |
|------|-------------|
| `explore_project` | Initialize and explore a project directory |
| `list_files` | List files in a directory with filtering options |
| `read_file` | Read file contents (with line range support) |
| `search_files` | Search for text within files |
| `search_symbol` | Find symbols (classes, functions, imports) |
| `find_references` | Locate all references to a symbol |
| `find_definition` | Find where a symbol is defined |
| `search_code_advanced` | Advanced search with regex and context |
| `analyze_imports` | Analyze import statements and dependencies |
| `analyze_file` | Get code metrics and statistics |
| `find_code_patterns` | Search for specific code patterns |


## Architecture

The project is organized as follows:

```
mcp-code-server/
├── Central_Server.py      # Main MCP server implementation
├── src/
│   ├── code_analyzer/     # Code analysis utilities
│   ├── code_search/       # Code search and AST parsing
│   └── file_explorer/     # File system navigation
├── examples/              # Usage examples
└── pyproject.toml         # Project configuration
```

### Components

- **Central_Server.py**: The main server file that exposes MCP tools
- **CodeSearchEngine**: Provides AST-based code search capabilities
- **FileExplorer**: Handles file system operations and project exploration
- **CodeAnalyzer**: Performs code analysis and pattern matching

## Requirements

- Python 3.11 or higher
- Dependencies:
  - `mcp[cli]>=1.8.0`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please [create an issue](link-to-issues) in the repository.