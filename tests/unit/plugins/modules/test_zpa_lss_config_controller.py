# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.plugins.modules.common.utils import (
    set_module_args,
    AnsibleExitJson,
    ModuleTestCase,
    DEFAULT_PROVIDER,
)

from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockListResult:
    def __init__(self, items):
        self._items = items

    def to_list(self):
        return self._items


class TestZPALSSConfigControllerModule(ModuleTestCase):
    """Unit tests for zpa_lss_config_controller module."""

    SAMPLE_CONFIG = {
        "id": "123456",
        "config": {
            "id": "123456",
            "name": "Test_LSS_Config",
            "description": "Test LSS Configuration",
            "enabled": True,
            "lss_host": "10.1.1.1",
            "lss_port": "20000",
            "source_log_type": "user_activity",
            "source_log_format": "json",
            "use_tls": True,
        },
        "app_connector_group_ids": ["111111"],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_lss_config_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_lss_config(self, mock_client):
        """Test creating a new LSS config"""
        mock_client.lss.list_configs.return_value = MockListResult([])
        mock_client.lss.add_lss_config.return_value = {"id": "123456"}

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            config={
                "name": "Test_LSS_Config",
                "description": "Test LSS Configuration",
                "enabled": True,
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
            app_connector_group_ids=["111111"],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is True

    def test_update_lss_config_by_id(self, mock_client):
        """Test updating an existing LSS config by ID"""
        mock_client.lss.get_config.return_value = self.SAMPLE_CONFIG.copy()
        mock_client.lss.list_configs.return_value = MockListResult([self.SAMPLE_CONFIG])
        mock_client.lss.update_lss_config.return_value = {"id": "123456"}

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            id="123456",
            config={
                "name": "Test_LSS_Config",
                "description": "Updated description",
                "enabled": True,
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is True

    def test_update_lss_config_by_name(self, mock_client):
        """Test updating an existing LSS config by name"""
        mock_client.lss.list_configs.return_value = MockListResult([self.SAMPLE_CONFIG])
        mock_client.lss.update_lss_config.return_value = {"id": "123456"}

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            config={
                "name": "Test_LSS_Config",
                "description": "Updated description",
                "enabled": True,
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is True

    def test_delete_lss_config(self, mock_client):
        """Test deleting an LSS config"""
        mock_client.lss.get_config.return_value = self.SAMPLE_CONFIG.copy()
        mock_client.lss.delete_lss_config.return_value = 204

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="123456",
            config={
                "name": "Test_LSS_Config",
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is True

    def test_delete_nonexistent_config(self, mock_client):
        """Test deleting a nonexistent config"""
        mock_client.lss.get_config.return_value = None
        mock_client.lss.list_configs.return_value = MockListResult([])

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            config={
                "name": "NonExistent_Config",
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is False

    def test_delete_with_error_code(self, mock_client):
        """Test delete returning error code"""
        mock_client.lss.get_config.return_value = self.SAMPLE_CONFIG.copy()
        mock_client.lss.delete_lss_config.return_value = 400

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="123456",
            config={
                "name": "Test_LSS_Config",
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is False

    def test_create_with_policy_rule_resource(self, mock_client):
        """Test creating LSS config with policy rule resource"""
        mock_client.lss.list_configs.return_value = MockListResult([])
        mock_client.lss.add_lss_config.return_value = {"id": "123456"}

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            config={
                "name": "Test_LSS_Config",
                "lss_host": "10.1.1.1",
                "lss_port": "20000",
                "source_log_type": "user_activity",
            },
            policy_rule_resource={
                "name": "Test_Policy_Rule",
                "action": "LOG",
            },
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_lss_config_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_lss_config_controller.main()

        assert result.value.result["changed"] is True
