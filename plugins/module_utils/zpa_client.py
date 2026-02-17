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

# =============================================================================
# Authentication Modes (mutually exclusive)
# =============================================================================
#
# 1. LEGACY API MODE
#    - use_legacy_client=true (required)
#    - Parameters: zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud (ALL required)
#    - ZPA_CLOUD env var; zpa_cloud is ALWAYS required
#    - Valid values: PRODUCTION, BETA, QA, QA2, GOV, GOVUS, PREVIEW, ZPATWO
#    - use_legacy_client MUST NOT be set when using OneAPI parameters
#
# 2. OneAPI MODE (default)
#    - use_legacy_client=false or omitted
#    - Parameters: client_id + (client_secret OR private_key) + vanity_domain
#    - Cloud: optional (ZSCALER_CLOUD, param name "cloud"); only beta or production
#    - For production, omit cloud or set to "production"
#
# Note: zpa_cloud (Legacy) and cloud (OneAPI) are separate params with different
#       env vars (ZPA_CLOUD vs ZSCALER_CLOUD) and valid value sets.
#
# =============================================================================

# Legacy API: ZPA_CLOUD values
VALID_ZPA_CLOUD = frozenset({
    "PRODUCTION",
    "BETA",
    "QA",
    "QA2",
    "GOV",
    "GOVUS",
    "PREVIEW",
    "ZPATWO",
})

# OneAPI: ZSCALER_CLOUD values only
VALID_ZSCALER_CLOUD = frozenset({"beta", "production"})

# Combined for argument_spec choices
CLOUD_CHOICES = sorted(VALID_ZPA_CLOUD | VALID_ZSCALER_CLOUD)


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

        provider = module.params.get("provider") or {}
        use_legacy_client = self._resolve_use_legacy_client(provider, module)

        if use_legacy_client:
            self._validate_no_oneapi_params_with_legacy(provider, module)
            self._client = self._init_legacy_client(module, provider)
        else:
            self._validate_legacy_params_require_use_legacy_client(provider, module)
            self._client = self._init_oneapi_client(module, provider)

        ansible_version = ansible_release.__version__
        self.user_agent = f"zpacloud-ansible/{ansible_version} (collection/{ansible_collection_version}) ({platform.system().lower()} {platform.machine()})"

    @staticmethod
    def _resolve_use_legacy_client(provider, module):
        """Resolve use_legacy_client from provider, module params, or env."""
        val = (
            provider.get("use_legacy_client")
            or module.params.get("use_legacy_client")
        )
        if val is not None:
            return bool(val)
        return os.getenv("ZSCALER_USE_LEGACY_CLIENT", "").lower() == "true"

    def _validate_legacy_params_require_use_legacy_client(self, provider, module):
        """When Legacy params are provided without use_legacy_client, fail with clear guidance."""
        params = self._resolve_legacy_params(provider, module)
        has_all_legacy = all([
            params["zpa_client_id"],
            params["zpa_client_secret"],
            params["zpa_customer_id"],
            params["zpa_cloud"],
        ])
        if has_all_legacy:
            module.fail_json(
                msg="You appear to be using Legacy API parameters (zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud). "
                "For Legacy authentication, set use_legacy_client=true in the provider or ZSCALER_USE_LEGACY_CLIENT=true as an environment variable."
            )

    def _validate_no_oneapi_params_with_legacy(self, provider, module):
        """use_legacy_client MUST NOT be set when using OneAPI parameters."""
        has_oneapi = (
            (provider.get("vanity_domain") or module.params.get("vanity_domain") or os.getenv("ZSCALER_VANITY_DOMAIN"))
            and (provider.get("client_id") or module.params.get("client_id") or os.getenv("ZSCALER_CLIENT_ID"))
            and (
                (provider.get("client_secret") or module.params.get("client_secret") or os.getenv("ZSCALER_CLIENT_SECRET"))
                or (provider.get("private_key") or module.params.get("private_key") or os.getenv("ZSCALER_PRIVATE_KEY"))
            )
        )
        if has_oneapi:
            module.fail_json(
                msg="Cannot use use_legacy_client=true with OneAPI parameters (client_id, vanity_domain, client_secret or private_key). "
                "Use use_legacy_client=false for OneAPI mode, or provide only Legacy parameters (zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud) for Legacy mode."
            )

    def __getattr__(self, name):
        """Delegate attribute access to the underlying client's zpa service"""
        try:
            # First try to get the attribute from the client's zpa service
            return getattr(self._client.zpa, name)
        except AttributeError:
            # If not found in zpa service, try the client directly
            return getattr(self._client, name)

    @staticmethod
    def _resolve_legacy_params(provider, module):
        """Resolve Legacy API params: zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud (ZPA_CLOUD)."""
        return {
            "zpa_client_id": provider.get("zpa_client_id") or module.params.get("zpa_client_id") or os.getenv("ZPA_CLIENT_ID"),
            "zpa_client_secret": provider.get("zpa_client_secret") or module.params.get("zpa_client_secret") or os.getenv("ZPA_CLIENT_SECRET"),
            "zpa_customer_id": provider.get("zpa_customer_id") or module.params.get("zpa_customer_id") or os.getenv("ZPA_CUSTOMER_ID"),
            "zpa_cloud": provider.get("zpa_cloud") or os.getenv("ZPA_CLOUD") or module.params.get("zpa_cloud"),
            "zpa_microtenant_id": provider.get("zpa_microtenant_id") or module.params.get("zpa_microtenant_id") or os.getenv("ZPA_MICROTENANT_ID"),
        }

    def _init_legacy_client(self, module, provider):
        """Legacy API mode: zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud (all required). use_legacy_client=true."""
        params = self._resolve_legacy_params(provider, module)
        client_id = params["zpa_client_id"]
        client_secret = params["zpa_client_secret"]
        customer_id = params["zpa_customer_id"]
        cloud_env = params["zpa_cloud"]
        microtenant_id = params["zpa_microtenant_id"]

        if not all([client_id, client_secret, customer_id, cloud_env]):
            module.fail_json(
                msg="All Legacy parameters must be provided: zpa_client_id, zpa_client_secret, zpa_customer_id, zpa_cloud. "
                "Use ZPA_CLOUD env var or provider zpa_cloud."
            )

        cloud_normalized = cloud_env.upper()
        if cloud_normalized not in VALID_ZPA_CLOUD:
            module.fail_json(
                msg=f"Invalid cloud '{cloud_env}' for Legacy client. "
                f"Valid values: {', '.join(sorted(VALID_ZPA_CLOUD))}. "
                "Use use_legacy_client=true with ZPA_CLOUD."
            )

        config = {
            "clientId": client_id,
            "clientSecret": client_secret,
            "customerId": customer_id,
            "microtenantId": microtenant_id,
            "cloud": cloud_normalized,
        }

        return LegacyZPAClient(config)

    @staticmethod
    def _resolve_oneapi_params(provider, module):
        """Resolve OneAPI params. Cloud uses ZSCALER_CLOUD (param name: cloud)."""
        return {
            "client_id": provider.get("client_id") or module.params.get("client_id") or os.getenv("ZSCALER_CLIENT_ID"),
            "client_secret": provider.get("client_secret") or module.params.get("client_secret") or os.getenv("ZSCALER_CLIENT_SECRET"),
            "private_key": provider.get("private_key") or module.params.get("private_key") or os.getenv("ZSCALER_PRIVATE_KEY"),
            "vanity_domain": provider.get("vanity_domain") or module.params.get("vanity_domain") or os.getenv("ZSCALER_VANITY_DOMAIN"),
            "cloud": provider.get("cloud") or os.getenv("ZSCALER_CLOUD") or module.params.get("cloud"),
            "customer_id": provider.get("customer_id") or module.params.get("customer_id") or os.getenv("ZPA_CUSTOMER_ID"),
            "microtenant_id": provider.get("microtenant_id") or module.params.get("microtenant_id") or os.getenv("ZPA_MICROTENANT_ID"),
        }

    def _init_oneapi_client(self, module, provider):
        """OneAPI mode: client_id + (client_secret OR private_key) + vanity_domain. Cloud optional."""
        p = self._resolve_oneapi_params(provider, module)
        client_id = p["client_id"]
        client_secret = p["client_secret"]
        private_key = p["private_key"]
        vanity_domain = p["vanity_domain"]
        cloud_env = p["cloud"]
        customer_id = p["customer_id"]
        microtenant_id = p["microtenant_id"]

        # Required fields
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

        # OneAPI cloud: optional. Only "beta" is passed; production is default.
        # Ignore Legacy names (PRODUCTION, BETA, GOV, etc.) - they would break the URL.
        if cloud_env:
            cloud_lower = cloud_env.lower()
            if cloud_lower == "beta":
                config["cloud"] = "beta"
            elif cloud_lower == "production" or cloud_lower.upper() in VALID_ZPA_CLOUD:
                # Production (explicit or Legacy name): omit - SDK defaults to production
                pass
            else:
                module.fail_json(
                    msg=f"Invalid cloud '{cloud_env}' for OneAPI. "
                    "Only 'beta' (for beta environment) or 'production' (default, optional) are supported. "
                    "Legacy cloud names (PRODUCTION, BETA, GOV, etc.) require use_legacy_client=true. "
                    "For production, omit the cloud parameter or set to 'production'."
                )

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
                        fallback=(env_fallback, ["ZPA_CLOUD"]),
                        type="str",
                        choices=CLOUD_CHOICES,
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
                        fallback=(env_fallback, ["ZSCALER_CLOUD"]),
                        type="str",
                        choices=CLOUD_CHOICES,
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
                fallback=(env_fallback, ["ZPA_CLOUD"]),
                type="str",
                choices=CLOUD_CHOICES,
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
                fallback=(env_fallback, ["ZSCALER_CLOUD"]),
                type="str",
                choices=CLOUD_CHOICES,
            ),
            use_legacy_client=dict(
                type="bool",
                required=False,
                default=False,
                fallback=(env_fallback, ["ZSCALER_USE_LEGACY_CLIENT"]),
            ),
        )
