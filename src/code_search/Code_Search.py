# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class SearchResult:
    file_path: str
    line_number: int
    column: int
    line_content: str
    context_before: List[str]
    context_after: List[str]
    match_type: str


class CodeSearchEngine:    
    def __init__(self, project_path: Path):
        """
        Initializes the code search engine with a project path.

        Args:
        project_path: Path to the project directory
        """
        self.project_path = project_path
        self.symbol_index = defaultdict(list)
        self.import_graph = defaultdict(set)
        self._build_index()
    
    def _build_index(self):
        """
        Builds an index of symbols in the project by analyzing Python files.
        Creates symbol index for classes, functions, and imports.
        """
        for py_file in self.project_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analizar AST para Python
                tree = ast.parse(content, filename=str(py_file))
                self._index_python_symbols(tree, py_file)
                
            except (SyntaxError, UnicodeDecodeError):
                continue
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Determines if a file should be skipped during indexing.

        Args:
            file_path: Path to check

        Returns:
            True if file should be skipped, False otherwise
        """
        skip_dirs = {'venv', 'env', '__pycache__', '.git', 'node_modules'}
        
        for parent in file_path.parents:
            if parent.name in skip_dirs:
                return True
        
        return False
    
    def _index_python_symbols(self, tree: ast.AST, file_path: Path):
        """
        Indexes Python symbols (classes, functions, imports) from an AST.

        Args:
            tree: Abstract Syntax Tree of the Python file
            file_path: Path to the file being indexed
        """
        relative_path = file_path.relative_to(self.project_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.symbol_index['class'].append({
                    'name': node.name,
                    'file': str(relative_path),
                    'line': node.lineno,
                    'type': 'class'
                })
            
            elif isinstance(node, ast.FunctionDef):
                self.symbol_index['function'].append({
                    'name': node.name,
                    'file': str(relative_path),
                    'line': node.lineno,
                    'type': 'function'
                })
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imported_name = alias.name
                    self.symbol_index['import'].append({
                        'name': imported_name,
                        'file': str(relative_path),
                        'line': node.lineno,
                        'type': 'import'
                    })
                    
                    # Construir grafo de importaciones
                    if isinstance(node, ast.ImportFrom) and node.module:
                        self.import_graph[str(relative_path)].add(node.module)
    
    def search_text(self, query: str, file_pattern: str = "*",
                    case_sensitive: bool = False, whole_word: bool = False,
                    regex: bool = False, context_lines: int = 2) -> List[SearchResult]:
        """
        Performs text search with advanced options.

        Args:
            query: Text or pattern to search for
            file_pattern: File pattern to match
            case_sensitive: Whether search is case-sensitive
            whole_word: Search for whole word only
            regex: Use regular expression
            context_lines: Number of context lines to include

        Returns:
            List of search results with context
        """
        results = []
        
        # Preparar patrón de búsqueda
        if regex:
            pattern = re.compile(query, re.IGNORECASE if not case_sensitive else 0)
        else:
            if whole_word:
                query = r'\b' + re.escape(query) + r'\b'
            pattern = re.compile(query, re.IGNORECASE if not case_sensitive else 0)
        
        # Determinar extensiones a buscar
        extensions = self._parse_file_pattern(file_pattern)
        
        # Buscar en archivos
        for file_path in self._get_searchable_files(extensions):
            matches = self._search_in_file(file_path, pattern, context_lines)
            results.extend(matches)
        
        return results
    
    def search_symbol(self, symbol_name: str,
                      symbol_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs text search with advanced options.

        Args:
            query: Text or pattern to search for
            file_pattern: File pattern to match
            case_sensitive: Whether search is case-sensitive
            whole_word: Search for whole word only
            regex: Use regular expression
            context_lines: Number of context lines to include

        Returns:
            List of search results with context
        """
        results = []
        
        search_types = [symbol_type] if symbol_type else ['class', 'function', 'import']
        
        for sym_type in search_types:
            for symbol in self.symbol_index.get(sym_type, []):
                if symbol_name.lower() in symbol['name'].lower():
                    results.append(symbol)
        
        return results
    
    def find_references(self, symbol_name: str) -> List[SearchResult]:
        """
        Finds all references to a symbol in the project.

        Args:
            symbol_name: Name of the symbol

        Returns:
            List of references as search results
        """
        return self.search_text(symbol_name, whole_word=True)
    
    def find_definition(self, symbol_name: str) -> Optional[Dict[str, Any]]:
        """
        Finds the definition of a symbol.

        Args:
            symbol_name: Name of the symbol

        Returns:
            Symbol definition information or None if not found
        """
        for symbol_type in ['class', 'function']:
            for symbol in self.symbol_index.get(symbol_type, []):
                if symbol['name'] == symbol_name:
                    return symbol
        
        return None
    
    def analyze_imports(self, file_path: str) -> Dict[str, Any]:
        """
        Analyzes the imports in a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Import information and dependencies
        """
        relative_path = Path(file_path).relative_to(self.project_path)
        
        imports = []
        for symbol in self.symbol_index.get('import', []):
            if symbol['file'] == str(relative_path):
                imports.append(symbol)
        
        dependencies = list(self.import_graph.get(str(relative_path), set()))
        
        return {
            'file': str(relative_path),
            'imports': imports,
            'dependencies': dependencies
        }
    
    def _parse_file_pattern(self, pattern: str) -> List[str]:
        """
        Converts a file pattern to a list of extensions.

        Args:
            pattern: File pattern (e.g., "*.py,*.js" or ".py,.js")

        Returns:
            List of file extensions or None for all files
        """
        if pattern == "*":
            return []
        
        extensions = []
        for part in pattern.split(','):
            part = part.strip()
            if part.startswith('*.'):
                extensions.append(part[1:])
            elif part.startswith('.'):
                extensions.append(part)
            else:
                extensions.append('.' + part)
        
        return extensions
    
    def _get_searchable_files(self, extensions: List[str]) -> List[Path]:
        files = []
        
        for ext in extensions or ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go']:
            files.extend(self.project_path.rglob(f"*{ext}"))
        
        return [f for f in files if not self._should_skip_file(f)]
    
    def _search_in_file(self, file_path: Path, pattern: re.Pattern,
                        context_lines: int) -> List[SearchResult]:
        """
        Searches for text in a specific file.

        Args:
            file_path: Path to the file
            query: Text to search for
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of matches with line numbers and content
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            relative_path = file_path.relative_to(self.project_path)
            
            for i, line in enumerate(lines):
                matches = list(pattern.finditer(line))
                
                for match in matches:
                    start_context = max(0, i - context_lines)
                    end_context = min(len(lines), i + context_lines + 1)
                    
                    context_before = [lines[j].rstrip() for j in range(start_context, i)]
                    context_after = [lines[j].rstrip() for j in range(i + 1, end_context)]
                    
                    results.append(SearchResult(
                        file_path=str(relative_path),
                        line_number=i + 1,
                        column=match.start() + 1,
                        line_content=line.rstrip(),
                        context_before=context_before,
                        context_after=context_after,
                        match_type='text'
                    ))
        
        except (UnicodeDecodeError, IOError):
            pass
        
        return results
