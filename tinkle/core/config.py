from pydantic_settings import BaseSettings, SettingsConfigDict
from tinkle.core.schemas import Permission

class Settings(BaseSettings):
 app_name:str="Tinkle"
 env:str="development"
 log_level:str="INFO"
 api_prefix:str="/api/v1"
 api_keys:str="dev-key"
 api_key_permissions:str="dev-key=read,write,execute,admin"
 api_key_principals:str="dev-key=default"
 max_task_prompt_length:int=10000
 background_workers:int=2
 default_model:str="small-local"
 local_ai_base_url:str="http://127.0.0.1:11434"
 cloud_ai_base_url:str="https://api.openai.com/v1"
 cloud_ai_api_key:str=""
 voice_id:str="uju3wxzG5OhpWcoi3SMy"
 security_rate_limit_per_minute:int=120
 security_max_tool_input_bytes:int=64000
 model_config=SettingsConfigDict(env_file=".env",env_prefix="TINKLE_",extra="ignore")
 @property
 def valid_api_keys(self)->set[str]: return {x.strip() for x in self.api_keys.split(",") if x.strip()}
 def _mapping(self, raw:str)->dict[str,str]:
  result={}
  for item in raw.split(";"):
   if "=" in item:
    key,value=item.split("=",1); result[key.strip()]=value.strip()
  return result
 def permissions_for_key(self,key:str)->set[Permission]:
  raw=self._mapping(self.api_key_permissions).get(key,"")
  return {Permission(x.strip()) for x in raw.split(",") if x.strip()}
 def principal_for_key(self,key:str)->str:
  return self._mapping(self.api_key_principals).get(key,"default")
settings=Settings()
