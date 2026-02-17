# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License
#
# Common utilities for unit testing Ansible modules.
# Adapted from Ansible and Palo Alto Networks testing patterns.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from unittest.mock import MagicMock

import pytest
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from box import Box


class MockBox(Box):
    """
    A mock Box object that behaves like the Zscaler SDK response objects.
    The SDK returns Box objects which have an as_dict() method.
    """

    def __init__(self, data=None, **kwargs):
        if data is None:
            data = {}
        super().__init__(data, **kwargs)

    def as_dict(self):
        """Convert Box to regular dict, like SDK objects do."""
        return self.to_dict()


def set_module_args(**args):
    """
    Set module arguments for testing.
    This injects arguments into the module's input.
    Compatible with all Ansible versions (2.14+, 2.15+, 2.16+, 2.17+).
    """
    # Add required Ansible internal parameters for all versions
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    # Additional parameters required for Ansible 2.15+
    if "_ansible_no_log" not in args:
        args["_ansible_no_log"] = False
    if "_ansible_debug" not in args:
        args["_ansible_debug"] = False
    if "_ansible_diff" not in args:
        args["_ansible_diff"] = False
    if "_ansible_verbosity" not in args:
        args["_ansible_verbosity"] = 0
    if "_ansible_selinux_special_fs" not in args:
        args["_ansible_selinux_special_fs"] = [
            "fuse",
            "nfs",
            "vboxsf",
            "ramfs",
            "9p",
            "vfat",
        ]
    if "_ansible_syslog_facility" not in args:
        args["_ansible_syslog_facility"] = "LOG_USER"
    if "_ansible_version" not in args:
        args["_ansible_version"] = "2.15.0"
    if "_ansible_module_name" not in args:
        args["_ansible_module_name"] = "test_module"
    if "_ansible_string_conversion_action" not in args:
        args["_ansible_string_conversion_action"] = "warn"
    if "_ansible_tmpdir" not in args:
        args["_ansible_tmpdir"] = "/tmp"

    # Create the args JSON for basic._ANSIBLE_ARGS (works for all versions)
    args_json = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args_json)

    # Also patch _load_params to return our args directly (for Ansible 2.17+)
    def _mock_load_params():
        return args

    basic._load_params = _mock_load_params


class AnsibleExitJson(SystemExit):
    """
    Exception raised when module calls exit_json().
    Inherits from SystemExit so it won't be caught by 'except Exception'.
    """

    def __init__(self, kwargs):
        self.result = kwargs
        super().__init__(0)


class AnsibleFailJson(SystemExit):
    """
    Exception raised when module calls fail_json().
    Inherits from SystemExit so it won't be caught by 'except Exception'.
    """

    def __init__(self, kwargs):
        self.result = kwargs
        super().__init__(1)


def exit_json(*args, **kwargs):
    """Mock exit_json that raises an exception for testing"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """Mock fail_json that raises an exception for testing"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


class ModuleTestCase:
    """
    Base class for module unit tests.
    Provides common fixtures and helper methods.
    """

    @pytest.fixture(autouse=True)
    def module_mock(self, mocker):
        """
        Automatically mock exit_json and fail_json for all tests.
        This allows us to capture module output.
        """
        return mocker.patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )

    @pytest.fixture
    def zpa_client_mock(self, mocker):
        """
        Mock the ZPAClientHelper to avoid actual API calls.
        Returns the mocked client for further configuration.
        """
        client_mock = mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ZPAClientHelper"
        )
        return client_mock.return_value

    @pytest.fixture
    def mock_client(self, mocker):
        """
        Mock the ZPAClientHelper class and return the mock instance.
        This is the primary fixture used by module tests.
        """
        mock_zpa_client_helper_class = mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.ZPAClientHelper"
        )
        mock_client_instance = MagicMock()
        mock_zpa_client_helper_class.return_value = mock_client_instance
        return mock_client_instance

    def _run_module(self, module, module_args):
        """
        Run a module with given arguments and return the result.
        Expects module to call exit_json (success).
        """
        set_module_args(**module_args)

        with pytest.raises(AnsibleExitJson) as ex:
            module.main()
        return ex.value.args[0]

    def _run_module_fail(self, module, module_args):
        """
        Run a module with given arguments expecting failure.
        Expects module to call fail_json (failure).
        """
        set_module_args(**module_args)

        with pytest.raises(AnsibleFailJson) as ex:
            module.main()
        return ex.value.args[0]


def generate_test_name(test_case):
    """Generate test name from test case dict"""
    return test_case.get("name", "unnamed_test")


# Common mock data factories
def create_mock_segment_group(
    id="123456789",
    name="Test Segment Group",
    description="Test Description",
    enabled=True,
    **kwargs
):
    """Create mock segment group data"""
    data = {
        "id": id,
        "name": name,
        "description": description,
        "enabled": enabled,
    }
    data.update(kwargs)
    return data


def create_mock_app_connector_group(
    id="123456789",
    name="Test App Connector Group",
    description="Test Description",
    enabled=True,
    city_country="San Jose, US",
    country_code="US",
    latitude="37.3382082",
    longitude="-121.8863286",
    location="San Jose, CA, USA",
    **kwargs
):
    """Create mock app connector group data"""
    data = {
        "id": id,
        "name": name,
        "description": description,
        "enabled": enabled,
        "city_country": city_country,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "location": location,
    }
    data.update(kwargs)
    return data


def create_mock_private_cloud_group(
    id="123456789",
    name="Test Private Cloud Group",
    description="Test Description",
    enabled=True,
    city_country="Sydney, AU",
    country_code="AU",
    latitude="-33.8688197",
    longitude="151.2092955",
    location="Sydney NSW, Australia",
    upgrade_day="SUNDAY",
    **kwargs
):
    """Create mock private cloud group data"""
    data = {
        "id": id,
        "name": name,
        "description": description,
        "enabled": enabled,
        "city_country": city_country,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "location": location,
        "upgrade_day": upgrade_day,
    }
    data.update(kwargs)
    return data


# Provider configuration for tests
DEFAULT_PROVIDER = {
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "customer_id": "test_customer_id",
    "cloud": "PRODUCTION",
    "vanity_domain": "test_domain",
}
