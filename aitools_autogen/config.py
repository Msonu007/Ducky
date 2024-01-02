import os
import sys

config_list = [
    {
        'model': 'gpt-3.5-turbo-16k',
        'api_key': 'aitools',
        'api_base': 'http://aitools.cs.vt.edu:7860/openai/v1'
    }
]

llm_config = {
    "request_timeout": 300,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0.1,
    "allow_format_str_template": True
}

DEFAULT_MODEL = "gpt-4"
FAST_MODEL = "gpt-3.5-turbo"
# Regular expression for finding a code block
CODE_BLOCK_PATTERN = r"(.*?)```(\w*)\n(.*?)\n```"
WORKING_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".code")
UNKNOWN = "unknown"
TIMEOUT_MSG = "Timeout"
DEFAULT_TIMEOUT = 600
WIN32 = sys.platform == "win32"
PATH_SEPARATOR = WIN32 and "\\" or "/"
