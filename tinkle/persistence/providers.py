from __future__ import annotations
import json, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class ProviderStatus:
    name:str; configured:bool; available:bool; mode:str

class PostgreSQLAdapter:
    def __init__(self,url:str|None=None): self.url=url; self._db=None
    def connect(self):
        if self.url and self.url.startswith("sqlite://"):
            path=self.url[9:]; Path(path).parent.mkdir(parents=True,exist_ok=True); self._db=sqlite3.connect(path); return True
        return False
    def status(self)->ProviderStatus: return ProviderStatus("PostgreSQL",bool(self.url),bool(self._db),"sqlite-compat" if self._db else "optional")

class RedisAdapter:
    def __init__(self,url:str|None=None): self.url=url; self._data={}
    def set(self,key:str,value:Any): self._data[key]=value
    def get(self,key:str): return self._data.get(key)
    def status(self)->ProviderStatus: return ProviderStatus("Redis",bool(self.url),True,"local-cache")

class QdrantAdapter:
    def __init__(self,url:str|None=None): self.url=url; self._points=[]
    def upsert(self,vector:list[float],payload:dict[str,Any]): self._points.append((vector,payload))
    def search(self,vector:list[float],top_k:int=5):
        def score(v): return sum(a*b for a,b in zip(vector,v))
        return sorted(({**p,"score":score(v)} for v,p in self._points),key=lambda x:x["score"],reverse=True)[:top_k]
    def status(self)->ProviderStatus: return ProviderStatus("Qdrant",bool(self.url),True,"local-vector-compat")
