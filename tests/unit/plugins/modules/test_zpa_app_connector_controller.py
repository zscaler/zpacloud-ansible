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


class TestZPAAppConnectorControllerModule(ModuleTestCase):
    """Unit tests for zpa_app_connector_controller module."""

    SAMPLE_CONNECTOR = {
        "id": "216199618143441990",
        "name": "Test_App_Connector",
        "description": "Test App Connector",
        "enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_delete_connector(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CONNECTOR)], None),
        )
        mock_client.app_connectors.delete_connector.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_App_Connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is True

    def test_delete_nonexistent_connector(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is False

    def test_check_mode(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CONNECTOR)], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_App_Connector",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is True

