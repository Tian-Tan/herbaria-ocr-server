import yaml
from pathlib import Path

class Settings:
    def __init__(self):
        config_path = Path(__file__).parent / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file at {config_path} not found")
        
        with config_path.open("r") as file:
            config = yaml.safe_load(file)
        
        self.app_name = config.get("app_name")
        self.display_name = config.get("display_name")
        self.model_name = config.get("model_name")
        self.server_version = config.get("server_version")
        self.api_version = config.get("api_version")
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 8000)
        self.azure_route = config.get("azure_route")

# Instantiate settings
settings = Settings()