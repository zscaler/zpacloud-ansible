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
        self.config = data.get("config", {})

    def as_dict(self):
        return self._data


class TestZPALSSConfigControllerInfoModule(ModuleTestCase):
    SAMPLE_CONFIGS = [
        {"id": "123", "config": {"name": "LSS_Config01", "enabled": True}},
        {"id": "456", "config": {"name": "LSS_Config02", "enabled": True}},
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_all_configs(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller_info.collect_all_items",
            return_value=([MockBox(c) for c in self.SAMPLE_CONFIGS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 2

    def test_get_config_by_id(self, mock_client):
        mock_client.lss.get_config.return_value = (MockBox(self.SAMPLE_CONFIGS[0]), None, None)
        set_module_args(provider=DEFAULT_PROVIDER, id="123")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller_info.main()
        assert result.value.result["data"][0]["id"] == "123"

    def test_config_not_found_by_id(self, mock_client):
        mock_client.lss.get_config.return_value = (None, None, "Not found")
        set_module_args(provider=DEFAULT_PROVIDER, id="999")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_lss_config_controller_info.main()
        assert "Failed to retrieve" in result.value.result["msg"]

    def test_get_config_by_name(self, mock_client, mocker):
        """Test retrieving config by name"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller_info.collect_all_items",
            return_value=([MockBox(c) for c in self.SAMPLE_CONFIGS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="LSS_Config01")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller_info.main()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 1

    def test_config_not_found_by_name(self, mock_client, mocker):
        """Test error when config not found by name"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller_info.collect_all_items",
            return_value=([MockBox(c) for c in self.SAMPLE_CONFIGS], None),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent_Config")
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_lss_config_controller_info.main()
        assert "not found" in result.value.result["msg"].lower()

    def test_list_configs_error(self, mock_client, mocker):
        """Test error handling when listing configs"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller_info.collect_all_items",
            return_value=(None, "List error"),
        )
        set_module_args(provider=DEFAULT_PROVIDER)
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller_info
        with pytest.raises(AnsibleFailJson) as result:
            zpa_lss_config_controller_info.main()
        assert "error" in result.value.result["msg"].lower()
