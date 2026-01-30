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

import datetime
import os
import os.path

import pytest
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest

from inmanta.server import config


@pytest.mark.asyncio
async def test_web_console_handler(server, inmanta_ui_config):
    base_url = f"http://127.0.0.1:{config.server_bind_port.get()}/console"
    client = AsyncHTTPClient()
    response = await client.fetch(base_url)
    assert response.code == 200

    response = await client.fetch(base_url + "/assets/asset.js")
    assert response.code == 200

    with pytest.raises(HTTPClientError) as exc:
        await client.fetch(base_url + "/assets/not_existing_asset.json")
    assert 404 == exc.value.code

    response = await client.fetch(base_url + "/lsm/catalog")
    assert response.code == 200
    assert "Should be served by default" in response.body.decode("UTF-8")

    # The app should handle the missing view
    response = await client.fetch(base_url + "/lsm/abc")
    assert response.code == 200
    assert "Should be served by default" in response.body.decode("UTF-8")

    # Should handle client side routes that don't start with 'lsm'
    response = await client.fetch(base_url + "/resources")
    assert response.code == 200
    assert "Should be served by default" in response.body.decode("UTF-8")


@pytest.fixture
def inmanta_ui_config_with_auth_enabled(inmanta_ui_config):
    config.Config.set("server", "auth", "True")


@pytest.mark.asyncio
async def test_auth_enabled(inmanta_ui_config_with_auth_enabled, server):
    """
    Ensure that the ui extension doesn't crash if server.auth config option is enabled
    and the server.auth_method is left to its default value.
    """
    base_url = f"http://127.0.0.1:{config.server_bind_port.get()}/console"
    client = AsyncHTTPClient()
    response = await client.fetch(base_url)
    assert response.code == 200


@pytest.mark.asyncio
async def test_start_location_redirect(server, inmanta_ui_config):
    """
    Ensure that the "start" location will redirect to the web console. (issue #202)
    """
    port = config.server_bind_port.get()
    response_url = f"http://localhost:{port}/console/"
    http_client = AsyncHTTPClient()
    request = HTTPRequest(
        url="http://localhost:%s/" % (port),
    )
    response = await http_client.fetch(request, raise_error=False)
    assert response.effective_url == response_url


@pytest.mark.asyncio
async def test_web_console_config(server, inmanta_ui_config):
    base_url = f"http://127.0.0.1:{config.server_bind_port.get()}/console/config.js"
    client = AsyncHTTPClient()
    response = await client.fetch(base_url)
    assert response.code == 200

    assert '\nexport const features = ["A", "B", "C"];' in response.body.decode()

    # test fetching from a deeper path
    base_url = f"http://127.0.0.1:{config.server_bind_port.get()}/console/lsm/config.js"
    client = AsyncHTTPClient()
    response = await client.fetch(base_url)
    assert response.code == 200

    assert '\nexport const features = ["A", "B", "C"];' in response.body.decode()


async def test_caching(server, inmanta_ui_config, web_console_path: str):
    """
    Verify that requests for files like version.json, config.js and index.html
    set the response header that stops the browser from caching the file.
    """

    # Ensure the required files exist in the root of the web-console folder.
    for file in ["version.json", "config.js", "something.css", "something.js"]:
        path = os.path.join(web_console_path, file)
        with open(path, "w") as fh:
            fh.write("test")

    # The modification timestamps are used by Tornado to determine the values
    # for the last-modified header. The last-modified header has seconds precision.
    modification_timestamp = datetime.datetime.now().replace(microsecond=0).astimezone()
    access_timestamp = modification_timestamp + datetime.timedelta(hours=5)
    for root, dirs, files in os.walk(web_console_path):
        for file in files:
            os.utime(
                path=os.path.join(root, file),
                times=(access_timestamp.timestamp(), modification_timestamp.timestamp()),
            )

    for url_path in [
        "/",
        "/console/",
        "/console/index.html",
        "/console/something/else",
        "/console/version.json",
        "/console/config.js",
        "/console/something/else/config.js",
        "/console/something.css",
        "/console/aaa/bbb/something.css",
        "/console/something.js",
        "/console/aaa/bbb/something.js",
    ]:
        base_url = f"http://127.0.0.1:{config.server_bind_port.get()}{url_path}"
        client = AsyncHTTPClient()
        response = await client.fetch(base_url)
        assert response.code == 200
        cache_control_headers = response.headers.get_list("Cache-Control")
        assert len(cache_control_headers) == 1, f"No Cache-Control header found for {url_path}"
        assert cache_control_headers[0] == "no-cache", f"Invalid value found for Cache-Control header for {url_path}"
        assert response.headers.get_list("Etag")
        last_modified_header = response.headers.get_list("Last-Modified")
        if url_path.endswith("/config.js"):
            # The config.js file is never cached
            assert len(last_modified_header) == 0
        else:
            assert len(last_modified_header) == 1
            actual_last_modified_timestamp = datetime.datetime.strptime(last_modified_header[0], "%a, %d %b %Y %H:%M:%S %Z")
            actual_last_modified_timestamp = actual_last_modified_timestamp.replace(tzinfo=datetime.timezone.utc)
            assert actual_last_modified_timestamp == modification_timestamp


async def test_config_js(server, inmanta_ui_config, web_console_path: str):
    """
    Verify that the config.js is handled correctly by the webserver.
    """

    # Add a config.js file to the root
    path_config_js = os.path.join(web_console_path, "config.js")
    with open(path_config_js, "w"):
        pass

    client = AsyncHTTPClient()
    base_url = f"http://127.0.0.1:{config.server_bind_port.get()}/console"

    for url, response_code in [
        (f"{base_url}/config.js", 200),
        # Fetching the config.js from a non-root path should be possible as well
        # to allow the application to run behind a reverse-proxy.
        (f"{base_url}/something/config.js", 200),
        # Only serve the config.js and no other files with the same prefix.
        (f"{base_url}/config.json", 404),
        (f"{base_url}/something/config.json", 404),
    ]:
        response = await client.fetch(url, raise_error=False)
        assert response.code == response_code, url
