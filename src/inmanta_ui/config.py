"""
    :copyright: 2019 Inmanta
    :contact: code@inmanta.com
    :license: Inmanta EULA
"""
from inmanta.config import Option, is_bool, is_str

web_console_enabled = Option("web-console", "enabled", True, "Should the server should host the web-console or not", is_bool)
web_console_path = Option(
    "web-console",
    "path",
    "/usr/share/inmanta/web-console",
    "The path on the local file system where the web-console can be found",
    is_str,
)
