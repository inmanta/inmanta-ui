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

import asyncio
import concurrent
import datetime
import logging
import os

import pytest

from inmanta import config
from inmanta.server.bootloader import InmantaBootloader

logger = logging.getLogger(__name__)


@pytest.fixture
def inmanta_ui_config(server_config, postgres_db, database_name, web_console_path):
    config.Config.set("server", "enabled_extensions", "ui")
    config.Config.set("web-ui", "console_path", str(web_console_path))
    config.Config.set("web-ui", "features", "A, B, C")


@pytest.fixture
async def server(inmanta_ui_config, server_config):
    """
    Override standard inmanta server to allow more config to be injected
    """
    ibl = InmantaBootloader(configure_logging=True)
    await ibl.start()

    yield ibl.restserver

    try:
        await asyncio.wait_for(ibl.stop(), 15)
    except concurrent.futures.TimeoutError:
        logger.exception("Timeout during stop of the server in teardown")

    logger.info("Server clean up done")


@pytest.fixture
def build_date() -> datetime.datetime:
    """
    The build date of the web-console for the tests.
    """
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture
def version_json(build_date: datetime.datetime) -> str:
    """
    The content of the version.json file in the root of the web-console directory.
    """
    # TODO: This is a quickfix, restore the original implementation when format version.json file is fixed.
    build_date_str = build_date.strftime("%a %b %d %Y %H:%M:%S %Z%z (Central European Summer Time)")
    # build_date_str = build_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
    # build_date_str = f"{build_date_str[0:-3]}Z"
    return (
        """
    {
      "version_info": {
        "buildDate": "%s"
      }
    }
    """
        % build_date_str
    )


@pytest.fixture
def web_console_path(tmpdir, version_json: str):
    with open(os.path.join(tmpdir, "index.html"), "w") as index:
        index.write(
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Should be served by default</title>
</head>
<body>

</body>
</html>"""
        )
    with open(os.path.join(tmpdir, "asset.js"), "w") as asset_file:
        asset_file.write("// Additional javascript file")
    with open(os.path.join(tmpdir, "version.json"), "w") as fh:
        fh.write(version_json)

    return tmpdir
