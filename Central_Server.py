# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

# Libraries
from mcp.server.fastmcp import FastMCP

from typing import Optional, Dict, Any, List

# Importing the Classes
from src.code_search import CodeSearchEngine, search_with_ast
from src.file_explorer import FileExplorer
from src.code_analyzer import CodeAnalyzer

# --- MCP Server Object

# Creating the MCP Server
mcp = FastMCP("Code Projects MCP")

# Crear instancia del explorador de archivos
file_explorer = FileExplorer()

# Variable global para el motor de búsqueda y analizador
search_engine: Optional[CodeSearchEngine] = None
code_analyzer = CodeAnalyzer()

@mcp.tool()
def explore_project(path: str) -> Dict[str, Any]:
    """
    Explores the general structure of a project.

    Args:
        path: Path to the project directory

    Returns:
        Information about the project structure including stats, file counts,
        directory structure, and file types
    """
    global search_engine
    
    # Establecer la ruta del proyecto
    result = file_explorer.set_project_path(path)
    if "error" in result:
        return result
    
    # Inicializar el motor de búsqueda
    search_engine = CodeSearchEngine(file_explorer.project_path)
    
    # Explorar el proyecto
    return file_explorer.explore_project()

@mcp.tool()
def list_files(directory: str = ".", recursive: bool = False,
               code_only: bool = True) -> Dict[str, Any]:
    """
    Lists files in a directory.

    Args:
        directory: Directory to list (relative to the project root)
        recursive: Whether to search recursively through subdirectories
        code_only: Show only code files if True

    Returns:
        List of found files with their metadata
    """
    return file_explorer.list_files(directory, recursive, code_only)

@mcp.tool()
def read_file(file_path: str, start_line: Optional[int] = None,
              end_line: Optional[int] = None) -> Dict[str, Any]:
    """
    Reads the content of a file.

    Args:
        file_path: Path to the file to read (relative to project root)
        start_line: Starting line number (optional)
        end_line: Ending line number (optional)

    Returns:
        File content with metadata including line range and encoding
    """
    return file_explorer.read_file(file_path, start_line, end_line)

@mcp.tool()
def search_files(query: str, file_pattern: str = "*",
                 case_sensitive: bool = False) -> Dict[str, Any]:
    """
    Searches for text in project files.

    Args:
        query: Text to search for
        file_pattern: File pattern to match (e.g., *.py)
        case_sensitive: Whether search is case-sensitive

    Returns:
        Search results with file locations and matching lines
    """

    return file_explorer.search_files(query, file_pattern, case_sensitive)

@mcp.tool()
def search_symbol(symbol_name: str, symbol_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Searches for symbols (classes, functions, imports) in the project.

    Args:
        symbol_name: Name of the symbol to search for
        symbol_type: Type of symbol ('class', 'function', 'import', or None for all)

    Returns:
        List of found symbols with their locations and types
    """
    if not search_engine:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        results = search_with_ast(
            file_explorer.project_path, 
            symbol_name, 
            search_type='symbol',
            symbol_type=symbol_type
        )
        
        return {
            'query': symbol_name,
            'type': symbol_type or 'all',
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def find_references(symbol_name: str) -> Dict[str, Any]:
    """
    Finds all references to a symbol in the project.

    Args:
        symbol_name: Name of the symbol to find references for

    Returns:
        List of references found with their locations
    """
    if not search_engine:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        results = search_with_ast(
            file_explorer.project_path,
            symbol_name,
            search_type='references'
        )
        
        return {
            'symbol': symbol_name,
            'references': results,
            'count': len(results)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def find_definition(symbol_name: str) -> Dict[str, Any]:
    """
    Finds the definition of a symbol.

    Args:
        symbol_name: Name of the symbol to find the definition for

    Returns:
        Location and details of the symbol definition
    """
    if not search_engine:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        results = search_with_ast(
            file_explorer.project_path,
            symbol_name,
            search_type='definition'
        )
        
        if results:
            return {
                'symbol': symbol_name,
                'definition': results[0],
                'found': True
            }
        else:
            return {
                'symbol': symbol_name,
                'found': False,
                'message': f"Definition not found for '{symbol_name}'"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_code_advanced(query: str, file_pattern: str = "*",
                         case_sensitive: bool = False,
                         whole_word: bool = False,
                         regex: bool = False,
                         context_lines: int = 2) -> Dict[str, Any]:
    """
    Advanced code search with support for regex and context.

    Args:
        query: Text or pattern to search for
        file_pattern: File pattern to match (e.g., *.py,*.js)
        case_sensitive: Whether search is case-sensitive
        whole_word: Search for whole word only
        regex: Use regular expression
        context_lines: Number of context lines before and after match

    Returns:
        Search results with surrounding context
    """
    if not search_engine:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        results = search_with_ast(
            file_explorer.project_path,
            query,
            search_type='text',
            file_pattern=file_pattern,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            regex=regex,
            context_lines=context_lines
        )
        
        return {
            'query': query,
            'options': {
                'file_pattern': file_pattern,
                'case_sensitive': case_sensitive,
                'whole_word': whole_word,
                'regex': regex,
                'context_lines': context_lines
            },
            'results': results[:50],  # Only 50 results
            'total_matches': len(results)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_imports(file_path: str) -> Dict[str, Any]:
    """
    Analyzes the imports in a file.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Information about imports and dependencies in the file
    """
    if not search_engine:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        result = search_engine.analyze_imports(file_path)
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyzes a file and extracts code metrics.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Metrics and statistics for the file including lines of code,
        complexity, functions, classes, and imports
    """
    if not file_explorer.project_path:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        full_path = file_explorer.project_path / file_path
        
        if not full_path.exists():
            return {"error": f"File does not exists: {file_path}"}
        
        # Solo analizar archivos Python por ahora
        if full_path.suffix.lower() != '.py':
            return {"error": "Currently we only support python files"}
        
        metrics = code_analyzer.analyze_python_file(full_path)
        metrics['file_path'] = file_path
        
        return metrics
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def find_code_patterns(file_path: str, patterns: List[str]) -> Dict[str, Any]:
    """
    Searches for specific patterns in a code file.

    Args:
        file_path: Path to the file
        patterns: List of regex patterns to search for

    Returns:
        Matches found for each pattern with line numbers and positions
    """
    if not file_explorer.project_path:
        return {"error": "Not Initialized Project. Use explore_project first."}
    
    try:
        full_path = file_explorer.project_path / file_path
        
        if not full_path.exists():
            return {"error": f"File does not exists: {file_path}"}
        
        results = code_analyzer.find_code_patterns(full_path, patterns)
        
        return {
            'file_path': file_path,
            'patterns': patterns,
            'results': results
        }
    except Exception as e:
        return {"error": str(e)}
