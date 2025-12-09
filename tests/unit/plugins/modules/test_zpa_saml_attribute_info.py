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


class TestZPASAMLAttributeInfoModule(ModuleTestCase):
    """Unit tests for zpa_saml_attribute_info module."""

    SAMPLE_IDP = {
        "id": "123456789",
        "name": "Okta_Users",
    }

    SAMPLE_ATTR = {
        "id": "216196257331285827",
        "name": "DepartmentName_Okta_Users",
        "saml_name": "DepartmentName",
        "idp_id": "123456789",
        "idp_name": "Okta_Users",
        "user_attribute": False,
    }

    SAMPLE_ATTR_2 = {
        "id": "216196257331285828",
        "name": "Email_Okta_Users",
        "saml_name": "Email",
        "idp_id": "123456789",
        "idp_name": "Okta_Users",
        "user_attribute": True,
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_saml_attribute_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_attribute_by_id(self, mock_client):
        """Test fetching a SAML Attribute by ID."""
        mock_attr = MockBox(self.SAMPLE_ATTR)
        mock_client.saml_attributes.get_saml_attribute.return_value = (mock_attr, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216196257331285827",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_saml_attribute_info.main()

        mock_client.saml_attributes.get_saml_attribute.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["saml_attributes"]) == 1

    def test_get_attribute_by_name(self, mock_client, mocker):
        """Test fetching a SAML Attribute by name."""
        mock_attrs = [MockBox(self.SAMPLE_ATTR), MockBox(self.SAMPLE_ATTR_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_saml_attribute_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="DepartmentName_Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_saml_attribute_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["saml_attributes"]) == 1

    def test_get_all_attributes(self, mock_client, mocker):
        """Test fetching all SAML Attributes."""
        mock_attrs = [MockBox(self.SAMPLE_ATTR), MockBox(self.SAMPLE_ATTR_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_saml_attribute_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_saml_attribute_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["saml_attributes"]) == 2

    def test_get_attributes_by_idp(self, mock_client, mocker):
        """Test fetching SAML Attributes by IdP name."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.list_idps.return_value = ([mock_idp], None, None)

        mock_attrs = [MockBox(self.SAMPLE_ATTR)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_saml_attribute_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            idp_name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_saml_attribute_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["saml_attributes"]) == 1

    def test_attribute_not_found_by_id(self, mock_client):
        """Test fetching a non-existent attribute by ID."""
        mock_client.saml_attributes.get_saml_attribute.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_saml_attribute_info.main()

        assert "not found" in result.value.result["msg"]

    def test_attribute_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent attribute by name."""
        mock_attrs = [MockBox(self.SAMPLE_ATTR)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_saml_attribute_info.collect_all_items",
            return_value=(mock_attrs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Attr",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_saml_attribute_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_saml_attribute_info.main()

        assert "not found" in result.value.result["msg"]

