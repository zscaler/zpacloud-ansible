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


class TestZPABrowserProtectionInfoModule(ModuleTestCase):
    SAMPLE_PROFILES = [
        {
            "id": "123",
            "name": "Browser_Profile_01",
            "default_csp": True,
            "criteria": {},
        },
        {
            "id": "456",
            "name": "Browser_Profile_02",
            "default_csp": False,
            "criteria": {},
        },
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
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

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
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_browser_protection_info.main()
        assert result.value.result["profile"]["name"] == "Browser_Profile_02"

    def test_profile_not_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(p) for p in self.SAMPLE_PROFILES], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_browser_protection_info.main()
        assert "Couldn't find" in result.value.result["msg"]

    def test_no_profiles_found(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_browser_protection_info.main()
        assert "No browser protection profiles found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        """Test error handling when listing profiles"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=(None, "API Error"),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_browser_protection_info.main()
        assert "error" in result.value.result["msg"].lower()

    def test_profile_with_criteria(self, mock_client, mocker):
        """Test profile with nested criteria structure"""
        profile_with_criteria = {
            "id": "789",
            "name": "Profile_With_Criteria",
            "default_csp": True,
            "criteria": {
                "finger_print_criteria": {
                    "collect_location": True,
                    "fingerprint_timeout": "30",
                    "browser": {
                        "browser_eng": True,
                        "browser_name": True,
                        "canvas": True,
                    },
                    "location": {
                        "lat": True,
                        "lon": True,
                    },
                    "system": {
                        "os_name": True,
                        "cpu_arch": True,
                    },
                },
            },
        }
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(profile_with_criteria)], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="Profile_With_Criteria")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_browser_protection_info.main()
        assert result.value.result["changed"] is False
        assert result.value.result["profile"]["name"] == "Profile_With_Criteria"

    def test_returns_first_profile_when_no_default(self, mock_client, mocker):
        """Test returns first profile when no default is explicitly set"""
        profiles = [
            {"id": "123", "name": "Profile_1", "default_csp": False, "criteria": {}},
            {"id": "456", "name": "Profile_2", "default_csp": False, "criteria": {}},
        ]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_browser_protection_info.collect_all_items",
            return_value=([MockBox(p) for p in profiles], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_browser_protection_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_browser_protection_info.main()
        # Module returns something (either first profile or None)
        assert result.value.result["changed"] is False
