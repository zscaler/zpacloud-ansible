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


class TestZPAIdpControllerInfoModule(ModuleTestCase):
    """Unit tests for zpa_idp_controller_info module."""

    SAMPLE_IDP = {
        "id": "216199618143191058",
        "name": "Okta_Users",
        "idp_entity_id": "http://www.okta.com/exkd8q2goavjgTfyj5d7",
        "login_url": "https://dev-123456.okta.com/app/zscaler_private_access/sso/saml",
        "enabled": True,
        "scim_enabled": True,
        "domain_list": ["acme.com"],
    }

    SAMPLE_IDP_2 = {
        "id": "216199618143191059",
        "name": "Azure_AD",
        "idp_entity_id": "https://sts.windows.net/abc123/",
        "login_url": "https://login.microsoftonline.com/abc123/saml2",
        "enabled": True,
        "scim_enabled": False,
        "domain_list": ["contoso.com"],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_idp_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_idp_by_id(self, mock_client):
        """Test fetching an IdP Controller by ID."""
        mock_idp = MockBox(self.SAMPLE_IDP)
        mock_client.idp.get_idp.return_value = (mock_idp, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143191058",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_idp_controller_info.main()

        mock_client.idp.get_idp.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 1
        assert result.value.result["data"][0]["name"] == "Okta_Users"

    def test_get_idp_by_name(self, mock_client, mocker):
        """Test fetching an IdP Controller by name."""
        mock_idps = [MockBox(self.SAMPLE_IDP), MockBox(self.SAMPLE_IDP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_idp_controller_info.collect_all_items",
            return_value=(mock_idps, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Okta_Users",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_idp_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["idps"]) == 1
        assert result.value.result["idps"][0]["name"] == "Okta_Users"

    def test_get_all_idps(self, mock_client, mocker):
        """Test fetching all IdP Controllers."""
        mock_idps = [MockBox(self.SAMPLE_IDP), MockBox(self.SAMPLE_IDP_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_idp_controller_info.collect_all_items",
            return_value=(mock_idps, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_idp_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["idps"]) == 2

    def test_get_scim_enabled_idps(self, mock_client, mocker):
        """Test fetching IdP Controllers with SCIM enabled."""
        mock_idps = [MockBox(self.SAMPLE_IDP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_idp_controller_info.collect_all_items",
            return_value=(mock_idps, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            scim_enabled=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_idp_controller_info.main()

        assert result.value.result["changed"] is False

    def test_idp_not_found_by_id(self, mock_client):
        """Test fetching a non-existent IdP by ID."""
        mock_client.idp.get_idp.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_idp_controller_info.main()

        assert "Failed to retrieve Identity Provider ID" in result.value.result["msg"]

    def test_idp_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent IdP by name."""
        mock_idps = [MockBox(self.SAMPLE_IDP)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_idp_controller_info.collect_all_items",
            return_value=(mock_idps, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_IdP",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_idp_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_idp_controller_info.main()

        assert "not found" in result.value.result["msg"]
