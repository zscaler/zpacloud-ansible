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


class TestZPATrustedNetworksInfoModule(ModuleTestCase):
    """Unit tests for zpa_trusted_networks_info module."""

    SAMPLE_NETWORK = {
        "id": "216199618143266948",
        "name": "BDTrustedNetwork01 (zscalertwo.net)",
        "network_id": "aeba3ac7-d860-4fa4-b4b8-8936ed7bc686",
        "zscaler_cloud": "zscalertwo",
    }

    SAMPLE_NETWORK_2 = {
        "id": "216199618143266949",
        "name": "Corp_Network (zscalertwo.net)",
        "network_id": "beba4bc8-e970-5gb5-c5c9-9047fd8cd797",
        "zscaler_cloud": "zscalertwo",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_trusted_networks_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_network_by_id(self, mock_client):
        """Test fetching a Trusted Network by ID."""
        mock_network = MockBox(self.SAMPLE_NETWORK)
        mock_client.trusted_networks.get_network.return_value = mock_network

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143266948",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_trusted_networks_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_trusted_networks_info.main()

        mock_client.trusted_networks.get_network.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["networks"]) == 1

    def test_get_network_by_name(self, mock_client, mocker):
        """Test fetching a Trusted Network by name (with cloud suffix removal)."""
        mock_networks = [MockBox(self.SAMPLE_NETWORK), MockBox(self.SAMPLE_NETWORK_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_trusted_networks_info.collect_all_items",
            return_value=(mock_networks, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="BDTrustedNetwork01",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_trusted_networks_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_trusted_networks_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["networks"]) == 1

    def test_get_all_networks(self, mock_client, mocker):
        """Test fetching all Trusted Networks."""
        mock_networks = [MockBox(self.SAMPLE_NETWORK), MockBox(self.SAMPLE_NETWORK_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_trusted_networks_info.collect_all_items",
            return_value=(mock_networks, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_trusted_networks_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_trusted_networks_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["networks"]) == 2

    def test_network_not_found_by_id(self, mock_client):
        """Test fetching a non-existent network by ID."""
        mock_client.trusted_networks.get_network.return_value = None

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_trusted_networks_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_trusted_networks_info.main()

        assert "Failed to retrieve Trusted Network ID" in result.value.result["msg"]

    def test_network_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent network by name."""
        mock_networks = [MockBox(self.SAMPLE_NETWORK)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_trusted_networks_info.collect_all_items",
            return_value=(mock_networks, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Network",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_trusted_networks_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_trusted_networks_info.main()

        assert "not found" in result.value.result["msg"]

