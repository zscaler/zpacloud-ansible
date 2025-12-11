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

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPALocationControllerInfoModule(ModuleTestCase):
    """Unit tests for zpa_location_controller_info module."""

    SAMPLE_EXTRANET_RESOURCE = {
        "id": "216199618143442000",
        "name": "Partner_ER",
        "enabled": True,
    }

    SAMPLE_LOCATION = {
        "id": "216199618143442001",
        "name": "San Jose Location",
        "enabled": True,
    }

    SAMPLE_LOCATION_2 = {
        "id": "216199618143442002",
        "name": "Austin Location",
        "enabled": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_location_by_name(self, mock_client, mocker):
        """Test fetching a Location Controller by name."""
        mock_ers = [MockBox(self.SAMPLE_EXTRANET_RESOURCE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.collect_all_items",
            return_value=(mock_ers, None),
        )

        mock_locations = [MockBox(self.SAMPLE_LOCATION), MockBox(self.SAMPLE_LOCATION_2)]
        mock_client.location_controller.get_location_extranet_resource.return_value = (
            mock_locations,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="San Jose Location",
            zia_er_name="Partner_ER",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_location_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["locations"]) == 1
        assert result.value.result["locations"][0]["name"] == "San Jose Location"

    def test_extranet_resource_not_found(self, mock_client, mocker):
        """Test when extranet resource is not found."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="San Jose Location",
            zia_er_name="NonExistent_ER",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_location_controller_info.main()

        assert "not found" in result.value.result["msg"]

    def test_location_not_found(self, mock_client, mocker):
        """Test when location is not found."""
        mock_ers = [MockBox(self.SAMPLE_EXTRANET_RESOURCE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.collect_all_items",
            return_value=(mock_ers, None),
        )

        mock_locations = [MockBox(self.SAMPLE_LOCATION)]
        mock_client.location_controller.get_location_extranet_resource.return_value = (
            mock_locations,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Location",
            zia_er_name="Partner_ER",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_location_controller_info.main()

        assert "not found" in result.value.result["msg"]

    def test_missing_required_params(self, mock_client):
        """Test when required parameters are missing."""
        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="San Jose Location",
            # Missing zia_er_name
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(SystemExit):
            zpa_location_controller_info.main()

    def test_api_error_on_list(self, mock_client, mocker):
        """Test error when listing extranet resources."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="San Jose Location",
            zia_er_name="Partner_ER",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_location_controller_info.main()

        assert "error" in result.value.result["msg"].lower()

    def test_api_error_on_get_locations(self, mock_client, mocker):
        """Test error when fetching locations."""
        mock_ers = [MockBox(self.SAMPLE_EXTRANET_RESOURCE)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_location_controller_info.collect_all_items",
            return_value=(mock_ers, None),
        )

        mock_client.location_controller.get_location_extranet_resource.return_value = (
            None,
            None,
            "API Error",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="San Jose Location",
            zia_er_name="Partner_ER",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_location_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_location_controller_info.main()

        assert "error" in result.value.result["msg"].lower()
