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


class TestZPACloudConfigModule(ModuleTestCase):
    SAMPLE_CONFIG = {"zia_cloud_domain": "zscaler.net", "zia_username": "admin@example.com"}

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_config.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_absent_state_no_op(self, mock_client):
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            zia_cloud_domain="zscaler",
            zia_username="admin@example.com",
            zia_password="password123",
            zia_sandbox_api_token="token123",
            zia_cloud_service_api_key="key123",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_cloud_config
        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_config.main()
        assert result.value.result["changed"] is False
        assert "cannot be deleted" in result.value.result["msg"]

    def test_create_config(self, mock_client):
        mock_client.zia_customer_config.get_zia_cloud_service_config.return_value = ([], None, None)
        mock_client.zia_customer_config.add_zia_cloud_service_config.return_value = (MockBox({}), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            zia_cloud_domain="zscaler",
            zia_username="admin@example.com",
            zia_password="password123",
            zia_sandbox_api_token="token123",
            zia_cloud_service_api_key="key123",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_cloud_config
        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_config.main()
        assert result.value.result["changed"] is True
