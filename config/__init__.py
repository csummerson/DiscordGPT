import os
import toml
from pathlib import Path

config_path = Path(__file__).parent / "settings.toml"
_config = toml.load(config_path)


DISCORD_TOKEN = os.environ.get("KEVIN_TOKEN", _config["discord"].get("token"))
BOT_STATUS = _config["discord"].get("status")
BOT_OWNER_ID = _config["discord"].get("owner_id")


OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY", _config["openai"].get("api_key"))
GPT_MODEL = _config["openai"].get("model")
TOKEN_LIMIT = _config["openai"].get("token_limit")


RUN_WATCHERS = _config["behavior"].get("run_watchers")


EXTRANEOUS_PROMPT = _config["prompts"].get("extraneous")
DEFAULT_PROMPT = _config["prompts"].get("default")
