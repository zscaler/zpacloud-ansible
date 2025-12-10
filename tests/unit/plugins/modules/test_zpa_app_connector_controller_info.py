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

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAAppConnectorControllerInfoModule(ModuleTestCase):
    """Unit tests for zpa_app_connector_controller_info module."""

    SAMPLE_CONNECTOR = {
        "id": "216199618143441990",
        "name": "Test_App_Connector",
        "description": "Test App Connector",
        "enabled": True,
        "application_start_time": "1693027293",
        "ctrl_broker_name": "broker.example.com",
        "current_version": "22.4.1",
        "expected_version": "22.4.1",
        "last_broker_connect_time": "1693027293",
        "last_broker_disconnect_time": "",
        "last_upgrade_time": "1693027293",
        "latitude": "37.33874",
        "longitude": "-121.8852525",
        "platform": "linux",
        "provisioning_key_id": "216199618143441991",
        "provisioning_key_name": "Test_Provisioning_Key",
    }

    SAMPLE_CONNECTOR_2 = {
        "id": "216199618143441992",
        "name": "Test_App_Connector_2",
        "description": "Test App Connector 2",
        "enabled": True,
        "application_start_time": "1693027293",
        "ctrl_broker_name": "broker.example.com",
        "current_version": "22.4.1",
        "expected_version": "22.4.1",
        "last_broker_connect_time": "1693027293",
        "last_broker_disconnect_time": "",
        "last_upgrade_time": "1693027293",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "platform": "linux",
        "provisioning_key_id": "216199618143441993",
        "provisioning_key_name": "Test_Provisioning_Key_2",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_connector_by_id(self, mock_client):
        mock_connector = MockBox(self.SAMPLE_CONNECTOR)
        mock_client.app_connectors.get_connector.return_value = (mock_connector, None, None)

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller_info.main()

        assert result.value.result["changed"] is False

    def test_get_connector_by_name(self, mock_client, mocker):
        mock_connectors = [MockBox(self.SAMPLE_CONNECTOR), MockBox(self.SAMPLE_CONNECTOR_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller_info.collect_all_items",
            return_value=(mock_connectors, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="Test_App_Connector")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller_info.main()

        assert result.value.result["changed"] is False

    def test_get_all_connectors(self, mock_client, mocker):
        mock_connectors = [MockBox(self.SAMPLE_CONNECTOR), MockBox(self.SAMPLE_CONNECTOR_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller_info.collect_all_items",
            return_value=(mock_connectors, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller_info.main()

        assert result.value.result["changed"] is False

    def test_connector_not_found_by_id(self, mock_client):
        mock_client.app_connectors.get_connector.return_value = (None, None, "Not Found")

        set_module_args(provider=DEFAULT_PROVIDER, id="999999999999999999")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller_info.main()

        assert "Failed" in result.value.result["msg"] or "not found" in result.value.result["msg"].lower()

    def test_api_error_on_list(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller_info.main()

        assert "Error" in result.value.result["msg"]

