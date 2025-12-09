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


class TestZPAPRACredentialControllerInfoModule(ModuleTestCase):
    """Unit tests for zpa_pra_credential_controller_info module."""

    SAMPLE_CRED = {
        "id": "8530",
        "name": "credential01",
        "description": "credential01",
        "credential_type": "USERNAME_PASSWORD",
        "user_name": "jdoe",
        "user_domain": "acme.com",
    }

    SAMPLE_CRED_2 = {
        "id": "8531",
        "name": "credential02",
        "description": "credential02",
        "credential_type": "SSH_KEY",
        "user_name": "admin",
        "user_domain": "corp.com",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_credential_by_id(self, mock_client):
        """Test fetching a PRA Credential by ID."""
        mock_cred = MockBox(self.SAMPLE_CRED)
        mock_client.pra_credential.get_credential.return_value = (mock_cred, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="8530",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller_info.main()

        mock_client.pra_credential.get_credential.assert_called_once()
        assert result.value.result["changed"] is False

    def test_get_credential_by_name(self, mock_client, mocker):
        """Test fetching a PRA Credential by name."""
        mock_creds = [MockBox(self.SAMPLE_CRED), MockBox(self.SAMPLE_CRED_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller_info.collect_all_items",
            return_value=(mock_creds, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential01",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["creds"]) == 1

    def test_get_all_credentials(self, mock_client, mocker):
        """Test fetching all PRA Credentials."""
        mock_creds = [MockBox(self.SAMPLE_CRED), MockBox(self.SAMPLE_CRED_2)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller_info.collect_all_items",
            return_value=(mock_creds, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["creds"]) == 2

    def test_credential_not_found_by_id(self, mock_client):
        """Test fetching a non-existent credential by ID."""
        mock_client.pra_credential.get_credential.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_credential_controller_info.main()

        assert "Failed to retrieve PRA Credential ID" in result.value.result["msg"]

    def test_credential_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent credential by name."""
        mock_creds = [MockBox(self.SAMPLE_CRED)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller_info.collect_all_items",
            return_value=(mock_creds, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Cred",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_credential_controller_info.main()

        assert "not found" in result.value.result["msg"]

