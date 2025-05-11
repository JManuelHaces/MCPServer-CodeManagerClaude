# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

import ast
import re
from pathlib import Path
from typing import Dict, List, Any


class CodeAnalyzer:
    @staticmethod
    def analyze_python_file(file_path: Path) -> Dict[str, Any]:
        """
        Analyzes a Python file and extracts metrics.

        Args:
            file_path: Path to the Python file

        Returns:
            Metrics including lines of code, functions, classes,
            imports, and cyclomatic complexity
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            metrics = {
                'lines_of_code': len(content.splitlines()),
                'lines_blank': len([line for line in content.splitlines() if not line.strip()]),
                'lines_comment': len([line for line in content.splitlines() if line.strip().startswith('#')]),
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        'docstring': ast.get_docstring(node),
                        'complexity': CodeAnalyzer._calculate_complexity(node)
                    }
                    metrics['functions'].append(func_info)
                    metrics['complexity'] += func_info['complexity']
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [],
                        'methods': [],
                        'docstring': ast.get_docstring(node)
                    }
                    
                    # Obtener clases base
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            class_info['bases'].append(base.id)
                    
                    # Obtener métodos
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append(item.name)
                    
                    metrics['classes'].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metrics['imports'].append({
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        metrics['imports'].append({
                            'name': f"{module}.{alias.name}",
                            'alias': alias.asname,
                            'line': node.lineno,
                            'from': module
                        })
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _calculate_complexity(node: ast.FunctionDef) -> int:
        """
        Calculates the cyclomatic complexity of a function.

        Args:
            node: AST node representing a function

        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    @staticmethod
    def find_code_patterns(file_path: Path, patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Searches for specific patterns in code using regex.

        Args:
            file_path: Path to the file
            patterns: List of regex patterns to search for

        Returns:
            List of matches with pattern, line number, and position
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    results.append({
                        'pattern': pattern,
                        'match': match.group(0),
                        'line': line_no,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        except Exception as e:
            return [{'error': str(e)}]
        
        return results
