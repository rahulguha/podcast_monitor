import glob
import json
import csv
import pickle
from pathlib import Path
from typing import Dict, Any, List, Union

class FileLoader:
    """Utility class to load multiple files from a directory using glob."""
    
    @staticmethod
    def load_text(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, str]]:
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def load_pickle(file_path: str) -> Any:
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    
    @classmethod
    def load_file(cls, file_path: str) -> Union[str, Dict, List, Any]:
        extension = Path(file_path).suffix.lower()
        
        loaders = {
            '.txt': cls.load_text,
            '.json': cls.load_json,
            '.csv': cls.load_csv,
            '.pkl': cls.load_pickle,
            '.pickle': cls.load_pickle
        }
        
        return loaders.get(extension, cls.load_text)(file_path)
    
    @classmethod
    def load_directory(cls, 
                      directory_path: str, 
                      recursive: bool = True,
                      file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Load files from a directory using glob patterns.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search subdirectories
            file_extensions: List of file extensions to load (e.g., ['.txt', '.json'])
        
        Returns:
            Dictionary with relative file paths as keys and file contents as values
        """
        loaded_files = {}
        base_path = Path(directory_path).resolve()
        
        # Create glob pattern
        pattern = f"**/*" if recursive else "*"
        if file_extensions:
            for ext in file_extensions:
                for file_path in base_path.glob(f"{pattern}{ext}"):
                    try:
                        relative_path = file_path.relative_to(base_path).as_posix()
                        loaded_files[relative_path] = cls.load_file(str(file_path))
                    except Exception as e:
                        print(f"Error loading {file_path}: {str(e)}")
        else:
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    try:
                        relative_path = file_path.relative_to(base_path).as_posix()
                        loaded_files[relative_path] = cls.load_file(str(file_path))
                    except Exception as e:
                        print(f"Error loading {file_path}: {str(e)}")
        
        return loaded_files