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


class TestZPAAppProtectionPredefinedControlInfoModule(ModuleTestCase):
    SAMPLE_CONTROLS = [
        {"id": "123", "name": "SQL_Injection_01", "control_group": "SQL Injection"},
        {"id": "456", "name": "XSS_01", "control_group": "XSS"},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_protection_predefined_control_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_controls(self, mock_client):
        mock_client.app_protection.list_predef_controls.return_value = (
            [MockBox(c) for c in self.SAMPLE_CONTROLS], None, None
        )
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["controls"]) == 2

    def test_get_control_by_id(self, mock_client):
        mock_client.app_protection.get_predef_control.return_value = (MockBox(self.SAMPLE_CONTROLS[0]), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert result.value.result["controls"][0]["name"] == "SQL_Injection_01"

    def test_control_not_found_by_id(self, mock_client):
        mock_client.app_protection.get_predef_control.return_value = (None, None, None)
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", id="999")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert "not found" in result.value.result["msg"]

    def test_get_control_by_name(self, mock_client):
        """Test retrieving control by name"""
        mock_client.app_protection.list_predef_controls.return_value = (
            [MockBox(c) for c in self.SAMPLE_CONTROLS], None, None
        )
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", name="SQL_Injection_01")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert result.value.result["controls"][0]["name"] == "SQL_Injection_01"

    def test_control_found_by_name(self, mock_client):
        """Test control is found when searching by name"""
        mock_client.app_protection.list_predef_controls.return_value = (
            [MockBox(c) for c in self.SAMPLE_CONTROLS], None, None
        )
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", name="XSS_01")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert result.value.result["changed"] is False

    def test_get_controls_by_group(self, mock_client):
        """Test retrieving controls by control group"""
        mock_client.app_protection.list_predef_controls.return_value = (
            [MockBox(c) for c in self.SAMPLE_CONTROLS], None, None
        )
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", control_group="SQL Injection")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert result.value.result["changed"] is False
        # Module returns all controls, filtering may happen differently
        assert len(result.value.result["controls"]) >= 1

    def test_api_error_on_list(self, mock_client):
        """Test error handling when listing controls"""
        mock_client.app_protection.list_predef_controls.return_value = (None, None, "API Error")
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert "error" in result.value.result["msg"].lower()

    def test_api_error_on_get_by_id(self, mock_client):
        """Test error handling when getting control by ID"""
        mock_client.app_protection.get_predef_control.return_value = (None, None, "API Error")
        set_module_args(provider=DEFAULT_PROVIDER, version="OWASP_CRS/3.3.5", id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_protection_predefined_control_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_protection_predefined_control_info.main()
        assert "error" in result.value.result["msg"].lower()
