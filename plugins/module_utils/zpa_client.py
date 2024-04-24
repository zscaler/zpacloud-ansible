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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import platform
from ansible.module_utils.basic import missing_required_lib, env_fallback
from ansible.module_utils import ansible_release

try:
    from zscaler.zpa import ZPAClientHelper as ZPA

    HAS_ZSCALER = True
    ZSCALER_IMPORT_ERROR = None
except ImportError:
    ZPA = object  # Default to object if import fails
    HAS_ZSCALER = False
    ZSCALER_IMPORT_ERROR = missing_required_lib("zscaler")

VALID_ZPA_ENVIRONMENTS = {
    "PRODUCTION",  # Default
    "BETA",
    "QA",
    "QA2",
    "GOV",
    "GOVUS",
    "PREVIEW",
    "ZPATWO",
}


class ConnectionHelper:
    def __init__(self, min_sdk_version):
        if not HAS_ZSCALER:
            raise ImportError(ZSCALER_IMPORT_ERROR)

        self.min_sdk_version = min_sdk_version
        self.check_sdk_installed()

    def check_sdk_installed(self):
        import zscaler

        installed_version = tuple(map(int, zscaler.__version__.split(".")))
        if installed_version < self.min_sdk_version:
            raise Exception(
                f"zscaler version should be >= {'.'.join(map(str, self.min_sdk_version))}"
            )


class ZPAClientHelper(ZPA):
    def __init__(self, module):
        if not HAS_ZSCALER:
            module.fail_json(
                msg="The 'zscaler' library is required for this module.",
                exception=ZSCALER_IMPORT_ERROR,
            )

        self.connection_helper = ConnectionHelper(min_sdk_version=(0, 1, 0))
        provider = module.params.get("provider") or {}
        client_id = provider.get("client_id") or module.params.get("client_id")
        client_secret = provider.get("client_secret") or module.params.get(
            "client_secret"
        )
        customer_id = provider.get("customer_id") or module.params.get("customer_id")
        cloud_env = provider.get("cloud") or module.params.get("cloud")
        cloud_env = cloud_env.upper()  # Ensure the cloud environment is in uppercase

        if cloud_env not in VALID_ZPA_ENVIRONMENTS:
            raise ValueError(f"Invalid ZPA Cloud environment '{cloud_env}'.")

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            customer_id=customer_id,
            cloud=cloud_env,
        )
        ansible_version = ansible_release.__version__
        self.user_agent = f"zpa-ansible/{ansible_version}/({platform.system().lower()} {platform.machine()})"

    @staticmethod
    def zpa_argument_spec():
        return dict(
            provider=dict(
                type="dict",
                options=dict(
                    client_id=dict(
                        no_log=True,
                        required=True,
                        fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
                        type="str",
                    ),
                    client_secret=dict(
                        no_log=True,
                        required=True,
                        fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
                        type="str",
                    ),
                    customer_id=dict(
                        no_log=True,
                        required=True,
                        fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                        type="str",
                    ),
                    cloud=dict(
                        no_log=False,
                        required=True,
                        choices=[
                            "PRODUCTION",
                            "BETA",
                            "GOV",
                            "GOVUS",
                            "PREVIEW",
                            "QA",
                            "QA2",
                        ],
                        fallback=(env_fallback, ["ZPA_CLOUD"]),
                        type="str",
                    ),
                ),
            ),
            client_id=dict(
                no_log=True,
                required=True,
                fallback=(env_fallback, ["ZPA_CLIENT_ID"]),
                type="str",
            ),
            client_secret=dict(
                no_log=True,
                required=True,
                fallback=(env_fallback, ["ZPA_CLIENT_SECRET"]),
                type="str",
            ),
            customer_id=dict(
                no_log=True,
                required=True,
                fallback=(env_fallback, ["ZPA_CUSTOMER_ID"]),
                type="str",
            ),
            cloud=dict(
                no_log=False,
                required=True,
                choices=[
                    "PRODUCTION",
                    "BETA",
                    "GOV",
                    "GOVUS",
                    "PREVIEW",
                    "QA",
                    "QA2",
                ],
                fallback=(env_fallback, ["ZPA_CLOUD"]),
                type="str",
            ),
        )
