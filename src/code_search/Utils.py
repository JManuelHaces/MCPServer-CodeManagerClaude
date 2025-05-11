# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

from pathlib import Path
from typing import List, Dict, Any
from src.code_search.Code_Search import CodeSearchEngine

# Funciones auxiliares para integrar con el servidor MCP
def search_with_ast(project_path: Path, query: str,
                    search_type: str = 'text', **kwargs) -> List[Dict[str, Any]]:
    """
    Unified interface for various code search and analysis functions using AST.
    Acts as a centralized adapter between the MCP server endpoints and the CodeSearchEngine class.

    Args:
        project_path: Path to the project directory
        query: Search query (text, symbol name, or pattern)
        search_type: Type of search to perform:
            - 'text': Searches for text content with context
            - 'symbol': Searches for symbol definitions (classes, functions, imports)
            - 'references': Finds all references to a symbol
            - 'definition': Locates the definition of a specific symbol
        **kwargs: Additional search parameters including:
            - symbol_type: For 'symbol' search, can be 'class', 'function', 'import', or None for all
            - file_pattern: Pattern for matching files (e.g., "*.py,*.js")
            - case_sensitive: Whether search should be case-sensitive
            - whole_word: Search for whole words only
            - regex: Treat query as regular expression
            - context_lines: Number of context lines to include in results

    Returns:
        List of formatted search results based on search type. Each result contains
        file path, line number, and other relevant information depending on the search type.
        For 'definition' searches, returns a single-item list or empty list if not found.
    """
    engine = CodeSearchEngine(project_path)
    
    if search_type == 'text':
        results = engine.search_text(query, **kwargs)
        return [
            {
                'file': r.file_path,
                'line': r.line_number,
                'column': r.column,
                'content': r.line_content,
                'context_before': r.context_before,
                'context_after': r.context_after,
                'type': r.match_type
            }
            for r in results
        ]
    
    elif search_type == 'symbol':
        return engine.search_symbol(query, kwargs.get('symbol_type'))
    
    elif search_type == 'references':
        results = engine.find_references(query)
        return [
            {
                'file': r.file_path,
                'line': r.line_number,
                'column': r.column,
                'content': r.line_content,
                'type': 'reference'
            }
            for r in results
        ]
    
    elif search_type == 'definition':
        result = engine.find_definition(query)
        return [result] if result else []
    
    return []
