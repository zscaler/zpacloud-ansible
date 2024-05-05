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

ZSCALER_IMPORT_ERROR = None
VERSION_IMPORT_ERROR = None

try:
    from zscaler.zpa import ZPAClientHelper as ZPA

    HAS_ZSCALER = True
except ImportError as e:
    ZPA = object  # Use a generic object if the import fails
    HAS_ZSCALER = False
    ZSCALER_IMPORT_ERROR = missing_required_lib("zscaler")

try:
    from ansible_collections.zscaler.zpacloud.plugins.module_utils.version import (
        __version__ as ansible_collection_version,
    )

    HAS_VERSION = True
except ImportError as e:
    HAS_VERSION = False
    VERSION_IMPORT_ERROR = missing_required_lib("plugins.module_utils.version")


VALID_ZPA_ENVIRONMENTS = {
    "PRODUCTION",
    "BETA",
    "QA",
    "QA2",
    "GOV",
    "GOVUS",
    "PREVIEW",
    "ZPATWO",
}


class ZPAClientHelper(ZPA):
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

        # Use provider or environment variables
        client_id = (
            provider.get("client_id")
            or module.params.get("client_id")
            or os.getenv("ZPA_CLIENT_ID")
        )
        client_secret = (
            provider.get("client_secret")
            or module.params.get("client_secret")
            or os.getenv("ZPA_CLIENT_SECRET")
        )
        customer_id = (
            provider.get("customer_id")
            or module.params.get("customer_id")
            or os.getenv("ZPA_CUSTOMER_ID")
        )
        cloud_env = (
            provider.get("cloud")
            or module.params.get("cloud")
            or os.getenv("ZPA_CLOUD")
        )

        # Check that all parameters are provided
        if not all([client_id, client_secret, customer_id, cloud_env]):
            module.fail_json(msg="All authentication parameters must be provided.")

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            customer_id=customer_id,
            cloud=cloud_env.upper(),
        )

        ansible_version = ansible_release.__version__
        self.user_agent = f"zpacloud-ansible/{ansible_version} (collection/{ansible_collection_version}) ({platform.system().lower()} {platform.machine()})"

    @staticmethod
    def zpa_argument_spec():
        return dict(
            provider=dict(
                type="dict",
                required=False,
                options=dict(
                    client_id=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
                    ),
                    client_secret=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
                    ),
                    customer_id=dict(
                        type="str",
                        no_log=True,
                        required=False,
                        fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                    ),
                    cloud=dict(
                        type="str",
                        required=False,
                        choices=list(VALID_ZPA_ENVIRONMENTS),
                        fallback=(env_fallback, ["ZPA_CLOUD"]),
                    ),
                ),
            ),
            client_id=dict(
                type="str",
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
            ),
            client_secret=dict(
                type="str",
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
            ),
            customer_id=dict(
                type="str",
                no_log=True,
                required=False,
                fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
            ),
            cloud=dict(
                type="str",
                required=False,
                choices=list(VALID_ZPA_ENVIRONMENTS),
                fallback=(env_fallback, ["ZPA_CLOUD"]),
            ),
        )
