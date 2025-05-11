# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

from pathlib import Path
from typing import Dict, Any, List, Optional

# Extensiones de archivo de código comunes
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.cs',
    '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.sql',
    '.html', '.css', '.scss', '.vue', '.svelte', '.json', '.yaml', '.yml',
    '.md', '.txt', '.sh', '.bash', '.zsh', '.ps1', '.dockerfile', '.gitignore'
}

# Archivos/carpetas a ignorar
IGNORE_PATTERNS = {
    'node_modules', '.git', '__pycache__', '.pytest_cache', 
    'venv', 'env', '.env', 'dist', 'build', '.idea', '.vscode',
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'
}

def should_ignore(path: Path) -> bool:
    """Determina si un archivo/carpeta debe ser ignorado"""
    name = path.name
    
    # Ignorar archivos/carpetas ocultos (excepto algunos importantes)
    if name.startswith('.') and name not in ['.gitignore', '.env.example']:
        return True
    
    # Ignorar patrones específicos
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    
    return False

def is_code_file(path: Path) -> bool:
    """Determina si un archivo es código"""
    return path.suffix.lower() in CODE_EXTENSIONS

def get_file_info(path: Path, base_path: Path) -> Dict[str, Any]:
    """Obtiene información sobre un archivo"""
    try:
        stat = path.stat()
        relative_path = path.relative_to(base_path)
        
        return {
            'path': str(relative_path),
            'name': path.name,
            'type': 'file' if path.is_file() else 'directory',
            'size': stat.st_size if path.is_file() else None,
            'extension': path.suffix.lower() if path.is_file() else None,
            'modified': stat.st_mtime
        }
    except Exception as e:
        return {'error': str(e), 'path': str(path)}

def read_file_content(
    file_path: Path,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> Dict[str, Any]:
    """Lee el contenido de un archivo con soporte para rangos de líneas"""
    try:
        # Leer archivo
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Intentar con latin-1 si utf-8 falla
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        
        total_lines = len(lines)
        
        # Aplicar rango de líneas si se especifica
        if start_line is not None or end_line is not None:
            start = max(0, (start_line - 1) if start_line else 0)
            end = min(total_lines, end_line if end_line else total_lines)
            selected_lines = lines[start:end]
            content = ''.join(selected_lines)
            line_range = f"{start + 1}-{end}"
        else:
            content = ''.join(lines)
            line_range = f"1-{total_lines}"
        
        return {
            'content': content,
            'total_lines': total_lines,
            'line_range': line_range,
            'size': file_path.stat().st_size,
            'encoding': 'utf-8'
        }
    except Exception as e:
        return {'error': str(e)}

def search_in_file(
    file_path: Path,
    query: str,
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """Busca texto en un archivo específico"""
    matches = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        search_query = query if case_sensitive else query.lower()
        
        for i, line in enumerate(lines, 1):
            search_line = line if case_sensitive else line.lower()
            if search_query in search_line:
                matches.append({
                    'line_number': i,
                    'line_content': line.strip(),
                    'column': search_line.index(search_query) + 1
                })
    
    except (UnicodeDecodeError, IOError):
        pass
    
    return matches

def parse_file_pattern(pattern: str) -> Optional[List[str]]:
    """Convierte un patrón de archivo a lista de extensiones"""
    if pattern == "*":
        return None
    
    extensions = []
    for ext in pattern.split(','):
        ext = ext.strip()
        if not ext.startswith('.'):
            ext = '.' + ext
        extensions.append(ext.lower())
    
    return extensions
