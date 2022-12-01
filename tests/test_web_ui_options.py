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

from inmanta.config import Config
from inmanta.server import config as opt_core
from inmanta_ui import config as opt_ui


def test_config_deprecated_sections(caplog):
    """
    Check that a deprecation warning is logged using a configuration option from a deprecated section.
    """
    for (deprecated_option, new_option) in [
        (opt_core.dash_path, opt_ui.web_ui_dashboard_path),
        (opt_core.dash_client_id, opt_ui.web_ui_oidc_client_id),
        (opt_ui.web_console_path, opt_ui.web_ui_console_path),
        (opt_ui.web_console_json_parser, opt_ui.web_ui_console_json_parser),
    ]:
        with caplog.at_level("WARNING"):
            Config.set(deprecated_option.section, deprecated_option.name, "22")
            caplog.clear()
            assert new_option.get() == "22"
            assert (
                "Config option %s.%s is deprecated. Use %s.%s instead."
                % (deprecated_option.section, deprecated_option.name, new_option.section, new_option.name)
                in caplog.text
            )

            Config.set(new_option.section, new_option.name, "23")
            caplog.clear()
            assert new_option.get() == "23"
            assert (
                "Config option %s.%s is deprecated. Use %s.%s instead."
                % (deprecated_option.section, deprecated_option.name, new_option.section, new_option.name)
                not in caplog.text
            )

            Config.load_config()  # Reset config options to default values
            assert new_option.get() != "23"
            assert deprecated_option.get() != "23"
            Config.set(new_option.section, new_option.name, "24")
            caplog.clear()
            assert new_option.get() == "24"
            assert (
                "Config option %s.%s is deprecated. Use %s.%s instead."
                % (deprecated_option.section, deprecated_option.name, new_option.section, new_option.name)
                not in caplog.text
            )
