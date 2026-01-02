import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


def _project_root() -> Path:
    # .../utils/config_loader.py -> parents[1] == project root
    return Path(__file__).resolve().parents[1]
    
def load_config(config_path: str| None = None)->dict:
    """
    This function loads a YAML configuration file and returns its contents as a dictionary.
    Args:
        config_path (str|None): The path to the YAML configuration file. If None, the default configuration is returned.

    Returns:
        dict: The contents of the YAML configuration file as a dictionary.
    """
    
    config_path = str(_project_root()/"config"/"config.yaml")
    
    path = Path(config_path)
    
    if not path.is_absolute():
        path = _project_root()/path
    if not path.exists():
        raise FileNotFoundError(f"config file not found : {path}")
    
    with open(path,'r',encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

# print(load_config('multi_doc_chat/config/config.yaml'))