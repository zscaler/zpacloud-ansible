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

    def test_bulk_delete(self, mock_client, mocker):
        """Test bulk delete with connector IDs"""
        mock_client.app_connectors.bulk_delete_connectors.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            ids=["id1", "id2", "id3"],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is True
        assert "deleted_connectors" in result.value.result["data"]

    def test_bulk_delete_error(self, mock_client, mocker):
        """Test bulk delete error handling"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.app_connectors.bulk_delete_connectors.return_value = (None, None, "Bulk delete error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            ids=["id1", "id2"],
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller.main()

        assert "bulk delete" in result.value.result["msg"].lower()

    def test_get_connector_by_id(self, mock_client, mocker):
        """Test retrieving connector by ID"""
        mock_client.app_connectors.get_connector.return_value = (
            MockBox(self.SAMPLE_CONNECTOR), None, None
        )
        mock_client.app_connectors.delete_connector.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="216199618143441990",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is True

    def test_get_connector_by_id_error(self, mock_client, mocker):
        """Test error handling when retrieving connector by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mock_client.app_connectors.get_connector.return_value = (None, None, "API Error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            id="invalid_id",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller.main()

        assert "error" in result.value.result["msg"].lower()

    def test_update_connector(self, mock_client, mocker):
        """Test updating an existing connector"""
        existing = {**self.SAMPLE_CONNECTOR, "description": "Old description"}
        mock_client.app_connectors.get_connector.return_value = (MockBox(existing), None, None)
        mock_client.app_connectors.update_connector.return_value = (
            MockBox({**existing, "description": "New description"}), None, None
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            id="216199618143441990",
            description="New description",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is True

    def test_update_no_change(self, mock_client, mocker):
        """Test no update when values match"""
        mock_client.app_connectors.get_connector.return_value = (MockBox(self.SAMPLE_CONNECTOR), None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            id="216199618143441990",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleExitJson) as result:
            zpa_app_connector_controller.main()

        assert result.value.result["changed"] is False

    def test_list_connectors_error(self, mock_client, mocker):
        """Test error handling when listing connectors"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.collect_all_items",
            return_value=(None, "List error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller.main()

        assert "error" in result.value.result["msg"].lower()

    def test_delete_error(self, mock_client, mocker):
        """Test error handling when deleting connector"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_app_connector_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_CONNECTOR)], None),
        )
        mock_client.app_connectors.delete_connector.return_value = (None, None, "Delete error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_App_Connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_app_connector_controller

        with pytest.raises(AnsibleFailJson) as result:
            zpa_app_connector_controller.main()

        assert "error" in result.value.result["msg"].lower()
