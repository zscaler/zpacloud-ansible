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

    def get(self, key, default=None):
        return self._data.get(key, default)


class TestZPASCIMAttributeHeaderInfoModule(ModuleTestCase):
    """Unit tests for zpa_scim_attribute_header_info module."""

    SAMPLE_IDP = {
        "id": "123456789",
        "name": "Okta_Users",
    }

    SAMPLE_ATTR = {
        "id": "216196257331285842",
        "name": "costCenter",
        "data_type": "String",
        "case_sensitive": False,
        "multivalued": False,
        "idp_id": "123456789",
    }

    SAMPLE_ATTR_2 = {
        "id": "216196257331285843",
        "name": "department",
        "data_type": "String",
        "case_sensitive": False,
        "multivalued": False,
        "idp_id": "123456789",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_attribute_header_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_attribute_by_id(self, mock_client):
        """Test fetching a SCIM Attribute by ID."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_attr = MockBox(self.SAMPLE_ATTR)
        mock_client.scim_attributes.get_scim_attribute.return_value = (
            mock_attr,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216196257331285842",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_attribute_header_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_attribute_header_info.main()

        mock_client.scim_attributes.get_scim_attribute.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["attributes"]) == 1
        assert result.value.result["attributes"][0]["name"] == "costCenter"

    def test_get_attribute_by_name(self, mock_client, mocker):
        """Test fetching a SCIM Attribute by name."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_attrs = [MockBox(self.SAMPLE_ATTR), MockBox(self.SAMPLE_ATTR_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_attribute_header_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="costCenter",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_attribute_header_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_attribute_header_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["attributes"]) == 1
        assert result.value.result["attributes"][0]["name"] == "costCenter"

    def test_get_all_attributes(self, mock_client, mocker):
        """Test fetching all SCIM Attributes for an IdP."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_attrs = [MockBox(self.SAMPLE_ATTR), MockBox(self.SAMPLE_ATTR_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_attribute_header_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_attribute_header_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_scim_attribute_header_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["attributes"]) == 2

    def test_idp_not_found(self, mock_client):
        """Test when IdP is not found."""
        mock_client.idp.list_idps.return_value = ([], None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="NonExistent_IdP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_attribute_header_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_attribute_header_info.main()

        assert "not found" in result.value.result["msg"]

    def test_attribute_not_found_by_name(self, mock_client, mocker):
        """Test when SCIM Attribute is not found by name."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_attrs = [MockBox(self.SAMPLE_ATTR)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_scim_attribute_header_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Attr",
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_scim_attribute_header_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_scim_attribute_header_info.main()

        assert "not found" in result.value.result["msg"]
