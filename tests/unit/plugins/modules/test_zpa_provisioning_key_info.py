# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

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
        self.name = data.get("name")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAProvisioningKeyInfoModule(ModuleTestCase):
    """Unit tests for zpa_provisioning_key_info module."""

    SAMPLE_KEY = {
        "id": "38108",
        "name": "Provisioning_Key01",
        "enabled": True,
        "enrollment_cert_id": "16560",
        "enrollment_cert_name": "Connector",
        "max_usage": "10",
        "usage_count": "0",
        "zcomponent_id": "216199618143441990",
        "zcomponent_name": "test_app_connector_group",
    }

    SAMPLE_KEY_2 = {
        "id": "38109",
        "name": "Provisioning_Key02",
        "enabled": True,
        "enrollment_cert_id": "16560",
        "enrollment_cert_name": "Connector",
        "max_usage": "5",
        "usage_count": "1",
        "zcomponent_id": "216199618143441991",
        "zcomponent_name": "test_app_connector_group_2",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_key_by_id(self, mock_client):
        """Test fetching a Provisioning Key by ID."""
        mock_key = MockBox(self.SAMPLE_KEY)
        mock_client.provisioning.get_provisioning_key.return_value = (
            mock_key,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="38108",
            key_type="connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key_info.main()

        mock_client.provisioning.get_provisioning_key.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 1
        assert result.value.result["data"][0]["name"] == "Provisioning_Key01"

    def test_get_key_by_name(self, mock_client, mocker):
        """Test fetching a Provisioning Key by name."""
        mock_keys = [MockBox(self.SAMPLE_KEY), MockBox(self.SAMPLE_KEY_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key_info.collect_all_items",
            return_value=(mock_keys, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Provisioning_Key01",
            key_type="connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["provisioning_keys"]) == 1
        assert (
            result.value.result["provisioning_keys"][0]["name"] == "Provisioning_Key01"
        )

    def test_get_all_connector_keys(self, mock_client, mocker):
        """Test fetching all connector Provisioning Keys."""
        mock_keys = [MockBox(self.SAMPLE_KEY), MockBox(self.SAMPLE_KEY_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key_info.collect_all_items",
            return_value=(mock_keys, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            key_type="connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["provisioning_keys"]) == 2

    def test_key_not_found_by_id(self, mock_client):
        """Test fetching a non-existent key by ID."""
        mock_client.provisioning.get_provisioning_key.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
            key_type="connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_provisioning_key_info.main()

        assert "Failed to retrieve Provisioning Key ID" in result.value.result["msg"]

    def test_key_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent key by name."""
        mock_keys = [MockBox(self.SAMPLE_KEY)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key_info.collect_all_items",
            return_value=(mock_keys, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Key",
            key_type="connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_provisioning_key_info.main()

        assert "not found" in result.value.result["msg"]
