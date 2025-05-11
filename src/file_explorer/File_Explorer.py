# Copyright (c) 2025 José Manuel Haces López
# Licensed under the MIT License.

import os
from pathlib import Path
from typing import Dict, Any, Optional

from src.file_explorer.Utils import (
    should_ignore,
    is_code_file,
    get_file_info,
    parse_file_pattern,
    search_in_file,
    read_file_content
)

class FileExplorer:    
    def __init__(self):
        self.project_path: Optional[Path] = None
    
    def set_project_path(self, path: str) -> Dict[str, Any]:
        """
        Sets the project path for the file explorer.

        Args:
            path: Path to the project directory

        Returns:
            Success status or error message
        """
        try:
            target_path = Path(path).resolve()
            
            if not target_path.exists():
                return {"error": f"Path not found: {path}"}
            
            if not target_path.is_dir():
                return {"error": f"Path is not a directory: {path}"}
            
            self.project_path = target_path
            return {"success": True, "path": str(target_path)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def explore_project(self) -> Dict[str, Any]:
        """
        Explores the general structure of the project.

        Returns:
            Project structure with statistics including file counts,
            code files, directories, file types, and total size
        """
        if not self.project_path:
            return {"error": "Not Initialized Project. Use explore_project first."}
        
        # Getting the project info
        stats = {
            'total_files': 0,
            'code_files': 0,
            'directories': 0,
            'file_types': {},
            'size_total': 0
        }
        
        structure = []
        
        # Explorar primer nivel
        for item in self.project_path.iterdir():
            if should_ignore(item):
                continue
            
            item_info = get_file_info(item, self.project_path)
            structure.append(item_info)
            
            if item.is_file():
                stats['total_files'] += 1
                stats['size_total'] += item.stat().st_size
                
                if is_code_file(item):
                    stats['code_files'] += 1
                
                ext = item.suffix.lower()
                if ext:
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
            else:
                stats['directories'] += 1
        
        # Ordenar estructura
        structure.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
        
        return {
            'project_path': str(self.project_path),
            'project_name': self.project_path.name,
            'stats': stats,
            'structure': structure[:20],
            'truncated': len(structure) > 20
        }
    
    def list_files(self, directory: str = ".", recursive: bool = False,
                   code_only: bool = True) -> Dict[str, Any]:
        """
        Lists files in a directory.

        Args:
            directory: Directory to list (relative to project root)
            recursive: Whether to search recursively
            code_only: Show only code files if True

        Returns:
            List of files with their metadata
        """
        if not self.project_path:
            return {"error": "Not Initialized Project. Use explore_project first."}
        
        target_dir = self.project_path / directory
        
        if not target_dir.exists():
            return {"error": f"Directory not found: {directory}"}
        
        files = []
        
        if recursive:
            for root, dirs, filenames in os.walk(target_dir):
                # Filtrar directorios ignorados
                dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    
                    if should_ignore(file_path):
                        continue
                    
                    if code_only and not is_code_file(file_path):
                        continue
                    
                    files.append(get_file_info(file_path, self.project_path))
        else:
            for item in target_dir.iterdir():
                if should_ignore(item):
                    continue
                
                if item.is_file():
                    if code_only and not is_code_file(item):
                        continue
                    files.append(get_file_info(item, self.project_path))
        
        # Ordenar por tipo y nombre
        files.sort(key=lambda x: (x.get('extension', ''), x['name'].lower()))
        
        return {
            'directory': directory,
            'files': files,
            'count': len(files)
        }
    
    def read_file(self, file_path: str, start_line: Optional[int] = None,
                  end_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Reads the content of a file.

        Args:
            file_path: Path to the file to read
            start_line: Starting line number (optional)
            end_line: Ending line number (optional)

        Returns:
            File content with metadata
        """
        if not self.project_path:
            return {"error": "Not Initialized Project. Use explore_project first."}
        
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        if not full_path.is_file():
            return {"error": f"It is not a file: {file_path}"}
        
        result = read_file_content(full_path, start_line, end_line)
        result['file_path'] = file_path
        
        return result
    
    def search_files(self, query: str, file_pattern: str = "*",
                     case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Searches for text in project files.

        Args:
            query: Text to search for
            file_pattern: File pattern to match
            case_sensitive: Whether search is case-sensitive

        Returns:
            Search results with file locations and matches
        """
        if not self.project_path:
            return {"error": "Not Initialized Project. Use explore_project first."}
        
        results = []
        extensions = parse_file_pattern(file_pattern)
        
        # Buscar en todos los archivos
        for root, dirs, files in os.walk(self.project_path):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
            
            for filename in files:
                file_path = Path(root) / filename
                
                if should_ignore(file_path):
                    continue
                
                # Verificar extensión
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                
                # Solo buscar en archivos de código
                if not is_code_file(file_path):
                    continue
                
                # Buscar en el archivo
                matches = search_in_file(file_path, query, case_sensitive)
                
                if matches:
                    relative_path = file_path.relative_to(self.project_path)
                    results.append({
                        'file': str(relative_path),
                        'matches': matches[:5],  # Limitar a 5 matches por archivo
                        'total_matches': len(matches)
                    })
        
        return {
            'query': query,
            'results': results[:20],  # Limitar a 20 archivos
            'total_files': len(results),
            'case_sensitive': case_sensitive,
            'file_pattern': file_pattern
        }
        