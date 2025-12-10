# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args, AnsibleExitJson, AnsibleFailJson, ModuleTestCase, DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import ZPAClientHelper

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class TestZPABrowserProtectionInfoModule(ModuleTestCase):
    SAMPLE_PROFILES = [
        {"id": "123", "name": "Browser_Profile_01", "default_csp": True, "criteria": {}},
        {"id": "456", "name": "Browser_Profile_02", "default_csp": False, "criteria": {}},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_default_profile(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_browser_protection_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_browser_protection_info.main()
        assert result.value.result["changed"] is False
        assert "profile" in result.value.result

    def test_get_profile_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="Browser_Profile_02")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_browser_protection_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_browser_protection_info.main()
        assert result.value.result["profile"]["name"] == "Browser_Profile_02"

    def test_profile_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_browser_protection_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_browser_protection_info.main()
        assert "Couldn't find" in result.value.result["msg"]

    def test_no_profiles_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_browser_protection_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_browser_protection_info.main()
        assert "No browser protection profiles found" in result.value.result["msg"]

