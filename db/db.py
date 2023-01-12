from tinydb import TinyDB, Query
from tinydb.table import Document

from pathlib import Path

class DatabaseSingleton(type):
    
    _instance = {}
    
    def __call__(cls, *args, **kwargs):
        
        if cls not in cls._instance:
            instance = super().__call__(*args, **kwargs)
            cls._instance[cls] = instance
        
        return cls._instance[cls]
    
class ModsDB(TinyDB, metaclass=DatabaseSingleton):
    
    def __init__(self, path: str, **kwargs):

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(path, **kwargs)
