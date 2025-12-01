#!/usr/bin/env python3
"""
BAIT PRO ULTIMATE - Advanced File Management System
- File indexing and smart search
- Auto-organization by type/date
- Duplicate file detection
- Compression utilities
- File system monitoring
"""

import os
import hashlib
import shutil
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json
import zipfile
import mimetypes

# Try whoosh for indexing
try:
    from whoosh.index import create_in, open_dir, exists_in
    from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
    from whoosh.qparser import QueryParser, MultifieldParser
    from whoosh import writing
    HAS_WHOOSH = True
except Import Error:
    HAS_WHOOSH = False
    logging.warning("Whoosh not available - search will be limited")

# Try send2trash
try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False
    logging.warning("send2trash not available - will use permanent delete")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# FILE INDEXER
# ═══════════════════════════════════════════════════════════════

class FileIndexer:
    """
    Index files for fast searching
    """
    
    def __init__(self, index_dir: str = ".file_index"):
        """
        Initialize file indexer
        
        Args:
            index_dir: Directory for index storage
        """
        self.index_dir =  index_dir
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        
        if HAS_WHOOSH:
            self.schema = Schema(
                path=ID(stored=True, unique=True),
                filename=TEXT(stored=True),
                extension=TEXT(stored=True),
                size=NUMERIC(stored=True),
                modified=DATETIME(stored=True),
                content=TEXT()  # For text files
            )
            
            if not exists_in(index_dir):
                self.ix = create_in(index_dir, self.schema)
            else:
                self.ix = open_dir(index_dir)
        else:
            self.ix = None
        
        logger.info(f"File Indexer initialized (index: {index_dir})")
    
    def index_directory(self, directory: str, recursive: bool = True):
        """
        Index all files in directory
        
        Args:
            directory: Directory to index
            recursive: Index subdirectories
        """
        if not self.ix:
            logger.error("Whoosh not available")
            return
        
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return
        
        logger.info(f"Indexing directory: {directory}")
        
        writer = self.ix.writer()
        count = 0
        
        try:
            for item in directory.rglob('*') if recursive else directory.glob('*'):
                if item.is_file():
                    try:
                        stats = item.stat()
                        
                        # Read content for text files
                        content = ""
                        if item.suffix in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                            try:
                                with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read(10000)  # First 10KB
                            except:
                                pass
                        
                        writer.add_document(
                            path=str(item.absolute()),
                            filename=item.name,
                            extension=item.suffix[1:] if item.suffix else '',
                            size=stats.st_size,
                            modified=datetime.fromtimestamp(stats.st_mtime),
                            content=content
                        )
                        
                        count += 1
                        
                        if count % 100 == 0:
                            logger.info(f"Indexed {count} files...")
                    
                    except Exception as e:
                        logger.warning(f"Error indexing {item}: {e}")
            
            writer.commit()
            logger.info(f"Indexing complete: {count} files")
        
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            writer.cancel()
    
    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search indexed files
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching files
        """
        if not self.ix:
            return []
        
        try:
            with self.ix.searcher() as searcher:
                # Search in filename and content
                qp = MultifieldParser(["filename", "content"], self.ix.schema)
                q = qp.parse(query)
                
                results = searcher.search(q, limit=limit)
                
                files = []
                for r in results:
                    files.append({
                        'path': r['path'],
                        'filename': r['filename'],
                        'extension': r['extension'],
                        'size': r['size'],
                        'modified': r['modified'].isoformat() if r['modified'] else None
                    })
                
                logger.info(f"Search '{query}': {len(files)} results")
                return files
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

# ═══════════════════════════════════════════════════════════════
# FILE ORGANIZER
# ═══════════════════════════════════════════════════════════════

class FileOrganizer:
    """
    Auto-organize files by type, date, etc.
    """
    
    FILE_CATEGORIES = {
        'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css'],
        'Spreadsheets': ['.xlsx', '.xls', '.csv', '.ods'],
        'Presentations': ['.pptx', '.ppt', '.odp'],
        'Other': []
    }
    
    def __init__(self):
        """Initialize file organizer"""
        logger.info("File Organizer initialized")
    
    def organize_by_type(self, directory: str, create_folders: bool = True) -> Dict[str, int]:
        """
        Organize files into folders by type
        
        Args:
            directory: Directory to organize
            create_folders: Create category folders
            
        Returns:
            Dict of category -> file count
        """
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return {}
        
        stats = {cat: 0 for cat in self.FILE_CATEGORIES.keys()}
        
        for item in directory.glob('*'):
            if item.is_file():
                category = self._get_category(item)
                
                if create_folders:
                    target_dir = directory / category
                    target_dir.mkdir(exist_ok=True)
                    
                    target_path = target_dir / item.name
                    shutil.move(str(item), str(target_path))
                
                stats[category] += 1
        
        logger.info(f"Organized files: {stats}")
        return stats
    
    def _get_category(self, file_path: Path) -> str:
        """Determine file category"""
        ext = file_path.suffix.lower()
        
        for category, extensions in self.FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        
        return 'Other'
    
    def organize_by_date(self, directory: str, format: str = "%Y/%m") -> Dict[str, int]:
        """
        Organize files by modification date
        
        Args:
            directory: Directory to organize
            format: Date format for folders (e.g., "%Y/%m" for Year/Month)
            
        Returns:
            Dict of date folder -> file count
        """
        directory = Path(directory)
        stats = {}
        
        for item in directory.glob('*'):
            if item.is_file():
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                date_folder = mtime.strftime(format)
                
                target_dir = directory / date_folder
                target_dir.mkdir(parents=True, exist_ok=True)
                
                target_path = target_dir / item.name
                shutil.move(str(item), str(target_path))
                
                stats[date_folder] = stats.get(date_folder, 0) + 1
        
        logger.info(f"Organized by date: {stats}")
        return stats

# ═══════════════════════════════════════════════════════════════
# DUPLICATE FINDER
# ═══════════════════════════════════════════════════════════════

class DuplicateFinder:
    """
    Find duplicate files based on content hash
    """
    
    def __init__(self):
        """Initialize duplicate finder"""
        self.hash_cache = {}
        logger.info("Duplicate Finder initialized")
    
    def find_duplicates(self, directory: str, recursive: bool = True) -> Dict[str, List[str]]:
        """
        Find duplicate files
        
        Args:
            directory: Directory to scan
            recursive: Scan subdirectories
            
        Returns:
            Dict of hash -> list of file paths
        """
        directory = Path(directory)
        hash_map = {}
        
        logger.info(f"Scanning for duplicates in: {directory}")
        
        items = directory.rglob('*') if recursive else directory.glob('*')
        
        for item in items:
            if item.is_file():
                file_hash = self._hash_file(item)
                
                if file_hash in hash_map:
                    hash_map[file_hash].append(str(item))
                else:
                    hash_map[file_hash] = [str(item)]
        
        # Filter to only duplicates
        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
        
        total_dupes = sum(len(files) - 1 for files in duplicates.values())
        logger.info(f"Found {total_dupes} duplicate files in {len(duplicates)} groups")
        
        return duplicates
    
    def _hash_file(self, file_path: Path, block_size: int = 65536) -> str:
        """Calculate MD5 hash of file"""
        if str(file_path) in self.hash_cache:
            return self.hash_cache[str(file_path)]
        
        hasher = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    block = f.read(block_size)
                    if not block:
                        break
                    hasher.update(block)
            
            file_hash = hasher.hexdigest()
            self.hash_cache[str(file_path)] = file_hash
            return file_hash
        
        except Exception as e:
            logger.warning(f"Hash error for {file_path}: {e}")
            return ""
    
    def remove_duplicates(self, duplicates: Dict[str, List[str]], keep_first: bool = True):
        """
        Remove duplicate files
        
        Args:
            duplicates: Output from find_duplicates()
            keep_first: Keep first occurrence, delete others
        """
        count = 0
        
        for file_hash, files in duplicates.items():
            files_to_delete = files[1:] if keep_first else files[:-1]
            
            for file_path in files_to_delete:
                try:
                    if HAS_SEND2TRASH:
                        send2trash(file_path)
                    else:
                        os.remove(file_path)
                    count += 1
                    logger.info(f"Deleted duplicate: {file_path}")
                except Exception as e:
                    logger.error(f"Delete error: {e}")
        
        logger.info(f"Removed {count} duplicate files")

# ═══════════════════════════════════════════════════════════════
# FILE MANAGER (Main Class)
# ═══════════════════════════════════════════════════════════════

class FileManager:
    """
    Advanced file management system
    """
    
    def __init__(self, index_dir: str = ".file_index"):
        """
        Initialize file manager
        
        Args:
            index_dir: Directory for search index
        """
        self.indexer = FileIndexer(index_dir) if HAS_WHOOSH else None
        self.organizer = FileOrganizer()
        self.duplicate_finder = DuplicateFinder()
        
        logger.info("File Manager initialized")
    
    def search_files(self, query: str, directory: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for files
        
        Args:
            query: Search query
            directory: Optional directory to index first
            limit: Maximum results
            
        Returns:
            List of matching files
        """
        if directory and self.indexer:
            self.indexer.index_directory(directory)
        
        if self.indexer:
            return self.indexer.search(query, limit)
        else:
            # Fallback: simple filename search
            return self._simple_search(query, directory, limit)
    
    def _simple_search(self, query: str, directory: str, limit: int) -> List[Dict[str, Any]]:
        """Simple fallback search"""
        if not directory:
            return []
        
        results = []
        query_lower = query.lower()
        
        for item in Path(directory).rglob('*'):
            if item.is_file() and query_lower in item.name.lower():
                stats = item.stat()
                results.append({
                    'path': str(item),
                    'filename': item.name,
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def organize_directory(self, directory: str, method: str = 'type') -> Dict[str, Any]:
        """
        Organize directory
        
        Args:
            directory: Directory to organize
            method: 'type' or 'date'
            
        Returns:
            Organization statistics
        """
        if method == 'type':
            return self.organizer.organize_by_type(directory)
        elif method == 'date':
            return self.organizer.organize_by_date(directory)
        else:
            logger.error(f"Unknown method: {method}")
            return {}
    
    def find_and_remove_duplicates(self, directory: str, auto_remove: bool = False) -> Dict[str, List[str]]:
        """
        Find (and optionally remove) duplicates
        
        Args:
            directory: Directory to scan
            auto_remove: Automatically remove duplicates
            
        Returns:
            Duplicate file groups
        """
        duplicates = self.duplicate_finder.find_duplicates(directory)
        
        if auto_remove and duplicates:
            self.duplicate_finder.remove_duplicates(duplicates)
        
        return duplicates
    
    def compress_directory(self, directory: str, output_file: str) -> bool:
        """
        Compress directory to ZIP
        
        Args:
            directory: Directory to compress
            output_file: Output ZIP file path
            
        Returns:
            True if successful
        """
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in Path(directory).rglob('*'):
                    if item.is_file():
                        arcname = item.relative_to(directory)
                        zipf.write(item, arcname)
            
            logger.info(f"Compressed {directory} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return False

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

def main():
    """Standalone testing"""
    print("=" * 60)
    print("BAIT File Manager - Test Mode")
    print("=" * 60)
    
    manager = FileManager()
    
    # Test search
    test_dir = os.path.expanduser("~/Documents")
    if os.path.exists(test_dir):
        print(f"\n🔍 Searching for 'test' in {test_dir}...")
        results = manager.search_files("test", test_dir, limit=5)
        for r in results:
            print(f"  - {r['filename']} ({r['size']} bytes)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
