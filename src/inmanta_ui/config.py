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

from inmanta.config import Option, is_bool, is_list, is_str

web_console_enabled = Option(
    "web-ui", "console_enabled", True, "Whether the server should host the web-console or not", is_bool
)
web_console_path = Option(
    "web-ui",
    "console_path",
    "/usr/share/inmanta/web-console",
    "The path on the local file system where the web-console can be found",
    is_str,
)
web_console_features = Option(
    "web-ui",
    "features",
    "",
    "A list of features that should be enabled in the web console.",
    is_list,
)

################################
# OpenID Connect authentication
################################

# Legacy Keycloak-specific options (method: "oidc").
# Used when oidc_authority is not set. The frontend receives these as a
# keycloak-js config and uses the implicit flow.
oidc_realm = Option("web-ui", "oidc_realm", "inmanta", "The realm to use for OpenID Connect authentication.", is_str)
oidc_auth_url = Option("web-ui", "oidc_auth_url", None, "The auth url of the OpenID Connect server to use.", is_str)
oidc_client_id = Option(
    "web-ui", "oidc_client_id", None, "The OpenID Connect client id configured for this application.", is_str
)

# Generic OIDC options (method: "oidc-generic").
# When oidc_authority is set, the frontend uses oidc-client-ts with
# authorization code flow + PKCE instead of keycloak-js implicit flow.
# This works with any OIDC-compliant IdP (MS Entra ID, Okta, Auth0, etc.).
oidc_authority = Option(
    "web-ui",
    "oidc_authority",
    None,
    "The OIDC authority URL (e.g. https://login.microsoftonline.com/{tenant-id}/v2.0). "
    "When set, the web console uses the generic OIDC provider instead of Keycloak.",
    is_str,
)
oidc_scope = Option(
    "web-ui",
    "oidc_scope",
    None,
    "Optional OIDC scopes override for the generic OIDC provider (default: 'openid profile email').",
    is_str,
)
