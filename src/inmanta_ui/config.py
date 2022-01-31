"""
    Copyright 2022 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
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
web_console_json_parser = Option(
    "web-console",
    "json_parser",
    "Native",
    "Whether the web-console should use the 'Native' or the 'BigInt' JSON Parser. "
    "'BigInt' is useful when the web-console has to show very large integers (larger than 2^53 - 1).",
    is_str,
)
