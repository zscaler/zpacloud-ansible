# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>

#                              MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import platform
from ansible.module_utils.basic import missing_required_lib, env_fallback
from ansible.module_utils import ansible_release

# Initialize import error variables
ZSCALER_IMPORT_ERROR = None
VERSION_IMPORT_ERROR = None

try:
    from zscaler.oneapi_client import LegacyZPAClient
    from zscaler import ZscalerClient as OneAPIClient

    HAS_ZSCALER = True
except ImportError as e:
    LegacyZPAClient = object  # Default to object if import fails
    OneAPIClient = object
    HAS_ZSCALER = False
    ZSCALER_IMPORT_ERROR = missing_required_lib("zscaler")

try:
    from ansible_collections.zscaler.zpacloud.plugins.module_utils.version import (
        __version__ as ansible_collection_version,
    )

    HAS_VERSION = True
except ImportError as e:
    HAS_VERSION = False
    VERSION_IMPORT_ERROR = missing_required_lib(
        "plugins.module_utils.version (version information)"
    )

VALID_ZPA_CLOUD = {
    "PRODUCTION",
    "BETA",
    "QA",
    "QA2",
    "GOV",
    "GOVUS",
    "PREVIEW",
    "ZPATWO",
}


class ZPAClientHelper:
    def __init__(self, module):
        if not HAS_ZSCALER:
            module.fail_json(
                msg="The 'zscaler' library is required for this module.",
                exception=ZSCALER_IMPORT_ERROR,
            )
        if not HAS_VERSION:
            module.fail_json(
                msg="Failed to import the version from the collection's module_utils.",
                exception=VERSION_IMPORT_ERROR,
            )

        # Initialize provider to an empty dict if None
        provider = module.params.get("provider") or {}

        # Get use_legacy_client flag from provider, module params, or environment
        use_legacy_client = (
            provider.get("use_legacy_client")
            or module.params.get("use_legacy_client")
            or os.getenv("ZSCALER_USE_LEGACY_CLIENT", "").lower() == "true"
        )

        if use_legacy_client:
            self._client = self._init_legacy_client(module, provider)
        else:
            self._client = self._init_oneapi_client(module, provider)

        # Set user agent for both client types
        ansible_version = ansible_release.__version__
        self.user_agent = f"zpacloud-ansible/{ansible_version} (collection/{ansible_collection_version}) ({platform.system().lower()} {platform.machine()})"

    def __getattr__(self, name):
        """Delegate attribute access to the underlying client's zpa service"""
        try:
            # First try to get the attribute from the client's zpa service
            return getattr(self._client.zpa, name)
        except AttributeError:
            # If not found in zpa service, try the client directly
            return getattr(self._client, name)

    def _init_legacy_client(self, module, provider):
        """Initialize the legacy ZPA client with clientId/clientSecret/customerId authentication"""
        client_id = (
            provider.get("zpa_client_id")
            or module.params.get("zpa_client_id")
            or os.getenv("ZPA_CLIENT_ID")
        )
        client_secret = (
            provider.get("zpa_client_secret")
            or module.params.get("zpa_client_secret")
            or os.getenv("ZPA_CLIENT_SECRET")
        )
        customer_id = (
            provider.get("zpa_customer_id")
            or module.params.get("zpa_customer_id")
            or os.getenv("ZPA_CUSTOMER_ID")
        )
        microtenant_id = (
            provider.get("zpa_microtenant_id")
            or module.params.get("zpa_microtenant_id")
            or os.getenv("ZPA_MICROTENANT_ID")
        )
        cloud_env = (
            provider.get("zpa_cloud")
            or module.params.get("zpa_cloud")
            or os.getenv("ZPA_CLOUD")
        )

        if not all([client_id, client_secret, customer_id, cloud_env]):
            module.fail_json(
                msg="All legacy parameters must be provided: zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud."
            )

        if cloud_env:
            cloud_env_normalized = cloud_env.upper()
            if cloud_env_normalized not in VALID_ZPA_CLOUD:
                module.fail_json(msg=f"Invalid ZPA Cloud environment '{cloud_env}'.")
            cloud_env = cloud_env_normalized  # Overwrite with validated uppercase

        config = {
            "clientId": client_id,
            "clientSecret": client_secret,
            "customerId": customer_id,
            "microtenantId": microtenant_id,
            "cloud": cloud_env.upper(),
        }

        return LegacyZPAClient(config)

    def _init_oneapi_client(self, module, provider):
        """Initialize the OneAPI client with OAuth2 authentication"""
        # Retrieve credentials from all sources
        client_id = (
            provider.get("client_id")
            or module.params.get("client_id")
            or os.getenv("ZSCALER_CLIENT_ID")
        )
        client_secret = (
            provider.get("client_secret")
            or module.params.get("client_secret")
            or os.getenv("ZSCALER_CLIENT_SECRET")
        )
        private_key = (
            provider.get("private_key")
            or module.params.get("private_key")
            or os.getenv("ZSCALER_PRIVATE_KEY")
        )
        vanity_domain = (
            provider.get("vanity_domain")
            or module.params.get("vanity_domain")
            or os.getenv("ZSCALER_VANITY_DOMAIN")
        )
        cloud_env = (
            provider.get("cloud")
            or module.params.get("cloud")
            or os.getenv("ZSCALER_CLOUD")
        )
        customer_id = (
            provider.get("customer_id")
            or module.params.get("customer_id")
            or os.getenv("ZPA_CUSTOMER_ID")
        )
        microtenant_id = (
            provider.get("microtenant_id")
            or module.params.get("microtenant_id")
            or os.getenv("ZPA_MICROTENANT_ID")
        )

        # ✅ Required fields
        if not vanity_domain:
            module.fail_json(msg="vanity_domain is required for OneAPI authentication")

        if not client_id:
            module.fail_json(msg="client_id is required for OneAPI authentication")

        if not client_secret and not private_key:
            module.fail_json(
                msg="Either client_secret or private_key must be provided for OneAPI authentication"
            )

        if client_secret and private_key:
            module.fail_json(
                msg="Only one authentication method can be used at a time: client_secret OR private_key (not both)"
            )

        # ✅ Construct OneAPI config
        config = {
            "clientId": client_id,
            "vanityDomain": vanity_domain,
            "customerId": customer_id,
            "microtenantId": microtenant_id,
            "logging": {"enabled": True, "verbose": False},
        }

        if client_secret:
            config["clientSecret"] = client_secret
        elif private_key:
            config["privateKey"] = private_key

        if cloud_env:
            config["cloud"] = cloud_env.lower()

        return OneAPIClient(config)

    @staticmethod
    def zpa_argument_spec():
        """Return the argument specification for both legacy and OneAPI authentication"""
        return dict(
            provider=dict(
                type="dict",
                options=dict(
                    zpa_client_id=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
                    ),
                    zpa_client_secret=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
                    ),
                    zpa_customer_id=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                    ),
                    zpa_microtenant_id=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_MICROTENANT_ID"]),
                    ),
                    zpa_cloud=dict(
                        no_log=False,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLOUD", "ZSCALER_CLOUD"]),
                        type="str",
                        choices=[
                            "BETA",
                            "GOV",
                            "GOVUS",
                            "PRODUCTION",
                            "QA",
                            "QA2",
                            "PREVIEW",
                            "beta",
                            "production",
                        ],
                    ),
                    # OneAPI authentication parameters
                    client_id=dict(
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZSCALER_CLIENT_ID"]),
                        type="str",
                    ),
                    client_secret=dict(
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZSCALER_CLIENT_SECRET"]),
                        type="str",
                    ),
                    private_key=dict(
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZSCALER_PRIVATE_KEY"]),
                        type="str",
                    ),
                    vanity_domain=dict(
                        no_log=False,
                        required=False,
                        fallback=(env_fallback, ["ZSCALER_VANITY_DOMAIN"]),
                        type="str",
                    ),
                    customer_id=dict(
                        no_log=False,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                        type="str",
                    ),
                    microtenant_id=dict(
                        no_log=False,
                        required=False,
                        fallback=(env_fallback, ["ZPA_MICROTENANT_ID"]),
                        type="str",
                    ),
                    cloud=dict(
                        no_log=False,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLOUD", "ZSCALER_CLOUD"]),
                        type="str",
                        choices=[
                            "BETA",
                            "GOV",
                            "GOVUS",
                            "PRODUCTION",
                            "QA",
                            "QA2",
                            "PREVIEW",
                            "beta",
                            "production",
                        ],
                    ),
                    use_legacy_client=dict(
                        type="bool",
                        default=False,
                        fallback=(env_fallback, ["ZSCALER_USE_LEGACY_CLIENT"]),
                    ),
                ),
            ),
            zpa_client_id=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
                type="str",
            ),
            zpa_client_secret=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
                type="str",
            ),
            zpa_customer_id=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                type="str",
            ),
            zpa_microtenant_id=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_MICROTENANT_ID"]),
                type="str",
            ),
            zpa_cloud=dict(
                no_log=False,
                required=False,
                fallback=(env_fallback, ["ZPA_CLOUD", "ZSCALER_CLOUD"]),
                type="str",
                choices=[
                    "BETA",
                    "GOV",
                    "GOVUS",
                    "PRODUCTION",
                    "QA",
                    "QA2",
                    "PREVIEW",
                    "beta",
                    "production",
                ],
            ),
            # OneAPI authentication parameters
            client_id=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZSCALER_CLIENT_ID"]),
                type="str",
            ),
            client_secret=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZSCALER_CLIENT_SECRET"]),
                type="str",
            ),
            private_key=dict(
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZSCALER_PRIVATE_KEY"]),
                type="str",
            ),
            vanity_domain=dict(
                no_log=False,
                required=False,
                fallback=(env_fallback, ["ZSCALER_VANITY_DOMAIN"]),
                type="str",
            ),
            customer_id=dict(
                no_log=False,
                required=False,
                fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                type="str",
            ),
            microtenant_id=dict(
                no_log=False,
                required=False,
                fallback=(env_fallback, ["ZPA_MICROTENANT_ID"]),
                type="str",
            ),
            cloud=dict(
                no_log=False,
                required=False,
                fallback=(env_fallback, ["ZPA_CLOUD", "ZSCALER_CLOUD"]),
                type="str",
                choices=[
                    "BETA",
                    "GOV",
                    "GOVUS",
                    "PRODUCTION",
                    "QA",
                    "QA2",
                    "PREVIEW",
                    "beta",
                    "production",
                ],
            ),
            use_legacy_client=dict(
                type="bool",
                required=False,
                default=False,
                fallback=(env_fallback, ["ZSCALER_USE_LEGACY_CLIENT"]),
            ),
        )
