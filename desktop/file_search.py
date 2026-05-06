"""
File Search Module
Search for files and folders on macOS using Spotlight (mdfind)
"""

import subprocess
import logging
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class FileSearcher:
    """
    Search for files using macOS Spotlight (mdfind).
    Provides natural language file searching capabilities.
    """
    
    def __init__(self):
        """Initialize file searcher."""
        logger.info("File searcher initialized")
        
        # Common search locations
        self.common_paths = {
            'desktop': str(Path.home() / 'Desktop'),
            'documents': str(Path.home() / 'Documents'),
            'downloads': str(Path.home() / 'Downloads'),
            'home': str(Path.home()),
            'pictures': str(Path.home() / 'Pictures'),
            'music': str(Path.home() / 'Music'),
            'movies': str(Path.home() / 'Movies'),
        }
    
    def search(
        self,
        query: str,
        limit: int = 10,
        file_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files using Spotlight.
        
        Args:
            query: Search query (filename or content)
            limit: Maximum number of results
            file_type: Filter by type ('document', 'image', 'video', 'audio', 'pdf', etc.)
            location: Search location ('desktop', 'documents', 'downloads', or path)
        
        Returns:
            List of file info dictionaries
        """
        logger.info(f"Searching for: '{query}' (type={file_type}, location={location})")
        
        try:
            # Build mdfind query
            mdfind_query = self._build_mdfind_query(query, file_type)
            
            # Build command
            cmd = ['mdfind']
            
            # Add location constraint if specified
            if location:
                search_path = self._resolve_location(location)
                if search_path:
                    cmd.extend(['-onlyin', search_path])
            
            cmd.append(mdfind_query)
            
            # Execute search
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Search failed: {result.stderr}")
                return []
            
            # Parse results
            file_paths = result.stdout.strip().split('\n')
            file_paths = [p for p in file_paths if p]  # Remove empty lines
            
            # Limit results
            file_paths = file_paths[:limit]
            
            # Get file info
            files = []
            for path in file_paths:
                info = self._get_file_info(path)
                if info:
                    files.append(info)
            
            logger.info(f"Found {len(files)} results")
            return files
        
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    def search_by_name(
        self,
        name: str,
        limit: int = 10,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files by name only.
        
        Args:
            name: Filename to search for
            limit: Maximum results
            location: Search location
        
        Returns:
            List of matching files
        """
        query = f'kMDItemFSName == "*{name}*"c'
        return self.search(query, limit=limit, location=location)
    
    def search_recent(
        self,
        days: int = 7,
        limit: int = 10,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for recently modified files.
        
        Args:
            days: Number of days to look back
            limit: Maximum results
            file_type: Filter by file type
        
        Returns:
            List of recent files
        """
        query = f'kMDItemFSContentChangeDate >= $time.today(-{days})'
        
        if file_type:
            type_query = self._get_type_query(file_type)
            query = f'{query} && {type_query}'
        
        return self.search(query, limit=limit)
    
    def find_file(self, filename: str) -> Optional[str]:
        """
        Find a specific file and return its path.
        
        Args:
            filename: Name of file to find
        
        Returns:
            Full path to file, or None if not found
        """
        results = self.search_by_name(filename, limit=1)
        
        if results:
            return results[0]['path']
        return None
    
    def open_file(self, path: str) -> bool:
        """
        Open a file with its default application.
        
        Args:
            path: Path to file
        
        Returns:
            True if successful
        """
        logger.info(f"Opening file: {path}")
        
        try:
            subprocess.run(['open', path], timeout=2)
            return True
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False
    
    def reveal_in_finder(self, path: str) -> bool:
        """
        Reveal file in Finder.
        
        Args:
            path: Path to file
        
        Returns:
            True if successful
        """
        logger.info(f"Revealing in Finder: {path}")
        
        try:
            subprocess.run(['open', '-R', path], timeout=2)
            return True
        except Exception as e:
            logger.error(f"Error revealing file: {e}")
            return False
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed file information.
        
        Args:
            path: Path to file
        
        Returns:
            File info dictionary
        """
        return self._get_file_info(path)
    
    # =========================
    # PRIVATE HELPER METHODS
    # =========================
    
    def _build_mdfind_query(self, query: str, file_type: Optional[str] = None) -> str:
        """Build mdfind query string."""
        
        # If query already looks like an mdfind query, use as-is
        if 'kMDItem' in query or '==' in query:
            return query
        
        # Otherwise, build a simple name/content search
        base_query = f'kMDItemTextContent == "*{query}*"c || kMDItemFSName == "*{query}*"c'
        
        # Add file type filter if specified
        if file_type:
            type_query = self._get_type_query(file_type)
            return f'({base_query}) && {type_query}'
        
        return base_query
    
    def _get_type_query(self, file_type: str) -> str:
        """Get mdfind query for specific file type."""
        
        type_mappings = {
            'document': 'kMDItemContentTypeTree == "public.text"',
            'pdf': 'kMDItemContentType == "com.adobe.pdf"',
            'image': 'kMDItemContentTypeTree == "public.image"',
            'video': 'kMDItemContentTypeTree == "public.video"',
            'audio': 'kMDItemContentTypeTree == "public.audio"',
            'code': 'kMDItemContentTypeTree == "public.source-code"',
            'folder': 'kMDItemContentType == "public.folder"',
        }
        
        return type_mappings.get(file_type.lower(), f'kMDItemFSName == "*.{file_type}"c')
    
    def _resolve_location(self, location: str) -> Optional[str]:
        """Resolve location name to path."""
        
        # Check if it's a common location
        if location.lower() in self.common_paths:
            return self.common_paths[location.lower()]
        
        # Check if it's already a valid path
        if os.path.exists(location):
            return location
        
        # Try to expand ~ and resolve
        expanded = os.path.expanduser(location)
        if os.path.exists(expanded):
            return expanded
        
        logger.warning(f"Could not resolve location: {location}")
        return None
    
    def _get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a file."""
        
        try:
            if not os.path.exists(path):
                return None
            
            stat = os.stat(path)
            
            info = {
                'path': path,
                'name': os.path.basename(path),
                'directory': os.path.dirname(path),
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_birthtime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'is_file': os.path.isfile(path),
                'is_directory': os.path.isdir(path),
                'extension': os.path.splitext(path)[1],
            }
            
            return info
        
        except Exception as e:
            logger.error(f"Error getting file info for {path}: {e}")
            return None
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} PB"


# Convenience functions
def search_files(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for files."""
    searcher = FileSearcher()
    return searcher.search(query, limit=limit)


def find_file(filename: str) -> Optional[str]:
    """Find a file by name."""
    searcher = FileSearcher()
    return searcher.find_file(filename)


def open_file(path: str) -> bool:
    """Open a file."""
    searcher = FileSearcher()
    return searcher.open_file(path)


def search_recent_files(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for recent files."""
    searcher = FileSearcher()
    return searcher.search_recent(days=days, limit=limit)
