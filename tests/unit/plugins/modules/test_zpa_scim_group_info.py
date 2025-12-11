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
        self.id = data.get("id")
        self.name = data.get("name")

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPASCIMGroupInfoModule(ModuleTestCase):
    """Unit tests for zpa_scim_group_info module."""

    SAMPLE_IDP = {
        "id": "123456789",
        "name": "Okta_Users",
    }

    SAMPLE_SCIM_GROUP = {
        "id": "645699",
        "name": "Engineering",
        "idp_id": "123456789",
        "internal_id": "645699",
    }

    SAMPLE_SCIM_GROUP_2 = {
        "id": "645700",
        "name": "Finance",
        "idp_id": "123456789",
        "internal_id": "645700",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_group_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_scim_group_by_id(self, mock_client):
        """Test fetching a SCIM Group by ID."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_group = MockBox(self.SAMPLE_SCIM_GROUP)
        mock_client.scim_groups.get_scim_group.return_value = (mock_group, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="645699",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_group_info.main()

        mock_client.scim_groups.get_scim_group.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Engineering"

    def test_get_scim_group_by_name(self, mock_client, mocker):
        """Test fetching a SCIM Group by name."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_groups = [MockBox(self.SAMPLE_SCIM_GROUP), MockBox(self.SAMPLE_SCIM_GROUP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Engineering",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Engineering"

    def test_get_all_scim_groups(self, mock_client, mocker):
        """Test fetching all SCIM Groups for an IdP."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_groups = [MockBox(self.SAMPLE_SCIM_GROUP), MockBox(self.SAMPLE_SCIM_GROUP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_group_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 2

    def test_idp_not_found(self, mock_client):
        """Test when IdP is not found."""
        mock_client.idp.list_idps.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="NonExistent_IdP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_group_info.main()

        assert "not found" in result.value.result["msg"]

    def test_scim_group_not_found_by_name(self, mock_client, mocker):
        """Test when SCIM Group is not found by name."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_groups = [MockBox(self.SAMPLE_SCIM_GROUP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_group_info.collect_all_items",
            return_value=(mock_groups, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Group",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_group_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list_idps(self, mock_client):
        """Test error handling when listing IdPs"""
        mock_client.idp.list_idps.return_value = (None, None, "API Error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_group_info.main()

        assert "error" in result.value.result["msg"].lower()

    def test_api_error_on_get_scim_group(self, mock_client):
        """Test error handling when getting SCIM group by ID"""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)
        mock_client.scim_groups.get_scim_group.return_value = (None, None, "Not found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_group_info.main()

        assert "not found" in result.value.result["msg"].lower()

    def test_api_error_on_list_scim_groups(self, mock_client, mocker):
        """Test error handling when listing SCIM groups"""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_group_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_group_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_group_info.main()

        assert "error" in result.value.result["msg"].lower()
