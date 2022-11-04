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
from inmanta.server.config import dash_auth_url, dash_client_id, dash_enable, dash_path, dash_realm

web_console_enabled = Option(
    "web-console",
    "enabled",
    True,
    "[DEPRECATED] The web-console section is deprecated, please use the web-ui section instead. "
    "Whether the server should host the web-console or not",
    is_bool,
)
web_console_path = Option(
    "web-console",
    "path",
    "/usr/share/inmanta/web-console",
    "[DEPRECATED] The web-console section is deprecated, please use the web-ui section instead. "
    "The path on the local file system where the web-console can be found",
    is_str,
)
web_console_json_parser = Option(
    "web-console",
    "json_parser",
    "Native",
    "[DEPRECATED] The web-console section is deprecated, please use the web-ui section instead. "
    "Whether the web-console should use the 'Native' or the 'BigInt' JSON Parser. "
    "'BigInt' is useful when the web-console has to show very large integers (larger than 2^53 - 1).",
    is_str,
)

web_ui_console_enabled = Option(
    "web-ui",
    "console_enabled",
    True,
    "Whether the server should host the web-console or not",
    is_bool,
    predecessor_option=web_console_enabled,
)
web_ui_console_path = Option(
    "web-ui",
    "console_path",
    "/usr/share/inmanta/web-console",
    "The path on the local file system where the web-console can be found",
    is_str,
    predecessor_option=web_console_path,
)
web_ui_console_json_parser = Option(
    "web-ui",
    "console_json_parser",
    "Native",
    "Whether the web-console should use the 'Native' or the 'BigInt' JSON Parser. "
    "'BigInt' is useful when the web-console has to show very large integers (larger than 2^53 - 1).",
    is_str,
    predecessor_option=web_console_json_parser,
)

#############################
# Dashboard
#############################


web_ui_dashboard_enabled = Option(
    "web-ui",
    "dashboard_enabled",
    True,
    "Determines whether the server should host the dashboard or not",
    is_bool,
    predecessor_option=dash_enable,
)

web_ui_dashboard_path = Option(
    "web-ui",
    "dashboard_path",
    "/usr/share/inmanta/dashboard",
    "The path on the local file system where the dashboard can be found",
    is_str,
    predecessor_option=dash_path,
)

web_ui_dashboard_realm = Option(
    "web-ui",
    "dashboard_realm",
    "inmanta",
    "The realm to use for keycloak authentication.",
    is_str,
    predecessor_option=dash_realm,
)

web_ui_dashboard_auth_url = Option(
    "web-ui",
    "dashboard_auth_url",
    None,
    "The auth url of the keycloak server to use.",
    is_str,
    predecessor_option=dash_auth_url,
)
web_ui_dashboard_client_id = Option(
    "web-ui",
    "dashboard_client_id",
    None,
    "The client id configured in keycloak for this application.",
    is_str,
    predecessor_option=dash_client_id,
)
