# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class TestZPAAppProtectionSecurityProfileInfoModule(ModuleTestCase):
    SAMPLE_PROFILES = [
        {"id": "123", "name": "Security_Profile_01", "paranoia_level": "1"},
        {"id": "456", "name": "Security_Profile_02", "paranoia_level": "2"},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_protection_security_profile_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_profiles(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_protection_security_profile_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_protection_security_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_security_profile_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["profiles"]) == 2

    def test_get_profile_by_id(self, mock_client):
        mock_client.app_protection.get_profile.return_value = (
            MockBox(self.SAMPLE_PROFILES[0]),
            None,
            None,
        )
        set_module_args(provider=DEFAULT_PROVIDER, id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_protection_security_profile_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_security_profile_info.main()
        assert result.value.result["profiles"][0]["name"] == "Security_Profile_01"

    def test_profile_not_found_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_protection_security_profile_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_app_protection_security_profile_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_protection_security_profile_info.main()
        assert "not found" in result.value.result["msg"]
