# -*- coding: utf-8 -*-
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


class TestZPAServiceEdgeControllerModule(ModuleTestCase):
    SAMPLE_SERVICE_EDGE = {
        "id": "123",
        "name": "ServiceEdge01",
        "description": "Test Service Edge",
        "enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_bulk_delete(self, mock_client):
        mock_client.service_edges.bulk_delete_service_edges.return_value = (
            None,
            None,
            None,
        )
        set_module_args(provider=DEFAULT_PROVIDER, ids=["123", "456"])
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["deleted_service_edges"] == ["123", "456"]

    def test_delete_by_id(self, mock_client):
        mock_client.service_edges.get_service_edge.return_value = (
            MockBox(self.SAMPLE_SERVICE_EDGE),
            None,
            None,
        )
        mock_client.service_edges.delete_connector.return_value = (None, None, None)
        set_module_args(provider=DEFAULT_PROVIDER, id="123", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is True

    def test_delete_nonexistent(self, mock_client):
        mock_client.service_edges.get_service_edge.return_value = (None, None, None)
        set_module_args(provider=DEFAULT_PROVIDER, id="999", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is False

    def test_delete_by_name(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_SERVICE_EDGE)], None),
        )
        mock_client.service_edges.delete_connector.return_value = (None, None, None)
        set_module_args(provider=DEFAULT_PROVIDER, name="ServiceEdge01", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is True

    def test_bulk_delete_error(self, mock_client):
        """Test bulk delete error handling"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.service_edges.bulk_delete_service_edges.return_value = (
            None,
            None,
            "Bulk delete failed",
        )
        set_module_args(provider=DEFAULT_PROVIDER, ids=["123", "456"])
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_controller.main()
        assert "bulk delete" in result.value.result["msg"].lower()

    def test_get_service_edge_by_id_error(self, mock_client):
        """Test error handling when retrieving service edge by ID"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.service_edges.get_service_edge.return_value = (
            None,
            None,
            "API Error",
        )
        set_module_args(provider=DEFAULT_PROVIDER, id="123", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_list_service_edges_error(self, mock_client, mocker):
        """Test error handling when listing service edges"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_service_edge_controller.collect_all_items",
            return_value=(None, "List error"),
        )
        set_module_args(provider=DEFAULT_PROVIDER, name="ServiceEdge01", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_delete_error(self, mock_client):
        """Test error handling when deleting service edge"""
        from tests.unit.plugins.modules.common.utils import AnsibleFailJson

        mock_client.service_edges.get_service_edge.return_value = (
            MockBox(self.SAMPLE_SERVICE_EDGE),
            None,
            None,
        )
        mock_client.service_edges.delete_connector.return_value = (
            None,
            None,
            "Delete failed",
        )
        set_module_args(provider=DEFAULT_PROVIDER, id="123", state="absent")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_service_edge_controller.main()
        assert "error" in result.value.result["msg"].lower()

    def test_check_mode_present(self, mock_client):
        """Test check mode with present state"""
        mock_client.service_edges.get_service_edge.return_value = (
            MockBox(self.SAMPLE_SERVICE_EDGE),
            None,
            None,
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="123",
            state="present",
            _ansible_check_mode=True,
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        # Service edge exists, state=present, no change needed
        assert "changed" in result.value.result

    def test_fallback_no_id_no_name(self, mock_client):
        """Test fallback when neither ID nor name provided"""
        set_module_args(provider=DEFAULT_PROVIDER, state="present")
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is False

    def test_check_mode_delete(self, mock_client):
        """Test check mode for delete"""
        mock_client.service_edges.get_service_edge.return_value = (
            MockBox(self.SAMPLE_SERVICE_EDGE),
            None,
            None,
        )
        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="123",
            state="absent",
            _ansible_check_mode=True,
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        mock_client.service_edges.delete_connector.assert_not_called()
        assert result.value.result["changed"] is True

    def test_with_microtenant_id(self, mock_client, mocker):
        """Test with microtenant_id parameter"""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules."
            "zpa_service_edge_controller.collect_all_items",
            return_value=([MockBox(self.SAMPLE_SERVICE_EDGE)], None),
        )
        mock_client.service_edges.delete_connector.return_value = (None, None, None)
        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="ServiceEdge01",
            microtenant_id="123456",
            state="absent",
        )
        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_service_edge_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_service_edge_controller.main()
        assert result.value.result["changed"] is True
