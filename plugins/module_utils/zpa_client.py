# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) Zscaler Technology Alliances, <zscaler-partner-labs@z-bd.com>
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.basic import env_fallback
import platform
import ansible
import importlib
from zscaler import ZPA

VALID_ZPA_ENVIRONMENTS = {
    "PRODUCTION",  # Default
    "BETA",
    "QA",
    "QA2",
    "GOV",
    "GOVUS",
    "PREVIEW"
}

def deleteNone(_dict):
    """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = deleteNone(value)
            elif value is None or key is None:
                del _dict[key]
    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(deleteNone(item) for item in _dict if item is not None)
    return _dict

def to_zscaler_sdk_cls(pkg_name, cls_name):
    sdk_name = "zscaler_sdk_python"

    try:
        mod = importlib.import_module("{0}.{1}".format(sdk_name, pkg_name))
    except ModuleNotFoundError:
        raise Exception(f"Couldn't find the package named {pkg_name} in {sdk_name}")
    else:
        try:
            return getattr(mod, cls_name)
        except AttributeError:
            raise Exception(f"{sdk_name}.{pkg_name}.{cls_name} does not exist")


class ConnectionHelper:
    """ConnectionHelper class for managing and verifying connectivity."""

    def __init__(self, min_sdk_version):
        self.min_sdk_version = min_sdk_version
        self.sdk_installed = self._check_sdk_installed()

    def _check_sdk_installed(self):
        try:
            import zscaler_sdk_python
            installed_version = tuple(map(int, zscaler_sdk_python.__version__.split(".")))
            if installed_version < self.min_sdk_version:
                raise Exception(f"zscaler_sdk_python version should be >= {'.'.join(map(str, self.min_sdk_version))}")
            return True
        except ModuleNotFoundError:
            return False
        except AttributeError:
            raise Exception("zscaler_sdk_python does not have a __version__ attribute. Please ensure you have the correct SDK installed.")

    def ensure_sdk_installed(self):
        if not self.sdk_installed:
            raise Exception('Missing required SDK "zscaler_sdk_python".')


class ZPAClientHelper(ZPA):
    def __init__(self, module):
        self.connection_helper = ConnectionHelper(min_sdk_version=(1, 0, 0))
        self.connection_helper.ensure_sdk_installed()

        cloud_env = module.params.get("cloud", "PRODUCTION").upper()  # default to "PRODUCTION" if not provided
        if cloud_env not in VALID_ZPA_ENVIRONMENTS:
            raise ValueError(f"Invalid ZPA Cloud environment '{cloud_env}'. Supported environments are: {', '.join(VALID_ZPA_ENVIRONMENTS)}.")

        super().__init__(
            client_id=module.params.get("client_id", ""),
            client_secret=module.params.get("client_secret", ""),
            customer_id=module.params.get("customer_id", ""),
            cloud=cloud_env,  # using the validated cloud environment
        )

        # Set the User-Agent
        ansible_version = ansible.__version__  # Get the Ansible version
        self.user_agent = f"zpa-ansible/{ansible_version}/({platform.system().lower()} {platform.machine()})"

    @staticmethod
    def zpa_argument_spec():
        return dict(
            client_id=dict(
                no_log=True,
                fallback=(
                    env_fallback,
                    ["ZPA_CLIENT_ID"],
                ),
            ),
            client_secret=dict(
                no_log=True,
                fallback=(
                    env_fallback,
                    ["ZPA_CLIENT_SECRET"],
                ),
            ),
            customer_id=dict(
                no_log=True,
                fallback=(
                    env_fallback,
                    ["ZPA_CUSTOMER_ID"],
                ),
            ),
            cloud=dict(
                no_log=True,
                fallback=(
                    env_fallback,
                    ["ZPA_CLOUD"],
                ),
            ),
        )