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
import os
from typing import List, cast

from tornado import routing, web

from inmanta.server import SLICE_SERVER, SLICE_TRANSPORT
from inmanta.server import config as opt
from inmanta.server import protocol
from inmanta.server.protocol import ServerSlice
from inmanta.server.server import Server
from inmanta_ui.const import SLICE_UI

from .config import web_console_enabled, web_console_json_parser, web_console_path


class UISlice(ServerSlice):
    def __init__(self) -> None:
        super().__init__(SLICE_UI)

    async def prestart(self, server: protocol.Server) -> None:
        _server = cast(Server, server.get_slice(SLICE_SERVER))
        self.add_web_console_handler(_server)
        await super(UISlice, self).prestart(server)

    async def start(self) -> None:
        await super(UISlice, self).start()

    async def prestop(self) -> None:
        await super(UISlice, self).prestop()

    async def stop(self) -> None:
        await super(UISlice, self).stop()

    def get_dependencies(self) -> List[str]:
        return []

    def get_depended_by(self) -> List[str]:
        # Ensure we are started before the HTTP endpoint becomes available
        return [SLICE_TRANSPORT]

    def add_web_console_handler(self, server: Server) -> None:
        if not web_console_enabled.get():
            return

        path = web_console_path.get()
        if path is None:
            return

        config_js_content = ""
        if opt.server_enable_auth.get():
            config_js_content = f"""
        window.auth = {{
            'realm': '{opt.dash_realm.get()}',
            'url': '{opt.dash_auth_url.get()}',
            'clientId': '{opt.dash_client_id.get()}'
        }};\n"""  # Use the same client-id as the dashboard
        json_parser_option = web_console_json_parser.get()
        if json_parser_option == "BigInt":
            config_js_content += f"window.jsonParserId = '{json_parser_option}';\n"

        server.add_static_content("/console/config.js", content=config_js_content)
        location = "/console/"
        options = {"path": path, "default_filename": "index.html"}
        server._handlers.append(
            routing.Rule(
                routing.PathMatches(r"%s(.*\.[^\s]{2,5}$)" % location),
                FlatFileHandler,
                options,
            )
        )
        server._handlers.append(
            routing.Rule(routing.PathMatches(r"%s" % location[:-1]), web.RedirectHandler, {"url": location[1:]})
        )
        server._handlers.append(
            routing.Rule(
                routing.PathMatches(r"%s(.*)" % location), SingleFileHandler, {"path": os.path.join(path, "index.html")}
            )
        )
        self._handlers.append((r"/", web.RedirectHandler, {"url": location[1:]}))


class SingleFileHandler(web.StaticFileHandler):
    """Always serves the single file given in the path option, useful for single page applications with client-side routing"""

    @classmethod
    def get_absolute_path(cls, root, path):
        return web.StaticFileHandler.get_absolute_path(root, "")


class FlatFileHandler(web.StaticFileHandler):
    """Always serves files from the root folder, useful when using a proxy"""

    @classmethod
    def get_absolute_path(cls, root, path):
        parts = os.path.split(path)
        if parts:
            return web.StaticFileHandler.get_absolute_path(root, parts[-1])
        return web.StaticFileHandler.get_absolute_path(root, "")
