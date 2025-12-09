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


class TestZPAPRACredentialControllerModule(ModuleTestCase):
    """Unit tests for zpa_pra_credential_controller module."""

    SAMPLE_CRED = {
        "id": "8530",
        "name": "credential01",
        "description": "credential01",
        "credential_type": "USERNAME_PASSWORD",
        "user_name": "jdoe",
        "user_domain": "acme.com",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_credential(self, mock_client, mocker):
        """Test creating a new PRA Credential."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_CRED)
        mock_client.pra_credential.add_credential.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential01",
            description="credential01",
            credential_type="USERNAME_PASSWORD",
            user_name="jdoe",
            user_domain="acme.com",
            password="secret123",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller.main()

        mock_client.pra_credential.add_credential.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_credential(self, mock_client, mocker):
        """Test updating an existing PRA Credential."""
        existing_cred = dict(self.SAMPLE_CRED)
        existing_cred["description"] = "Old description"
        mock_existing = MockBox(existing_cred)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_updated = MockBox(self.SAMPLE_CRED)
        mock_client.pra_credential.update_credential.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential01",
            description="credential01",
            credential_type="USERNAME_PASSWORD",
            user_name="jdoe",
            user_domain="acme.com",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller.main()

        mock_client.pra_credential.update_credential.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_credential(self, mock_client, mocker):
        """Test deleting a PRA Credential."""
        mock_existing = MockBox(self.SAMPLE_CRED)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_credential.delete_credential.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential01",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller.main()

        mock_client.pra_credential.delete_credential.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when credential already matches desired state."""
        # Sample credential that matches the args exactly
        identical_cred = {
            "id": "8530",
            "name": "credential01",
            "description": "credential01",
            "credential_type": "USERNAME_PASSWORD",
            "user_name": "jdoe",
            "user_domain": "acme.com",
            "microtenant_id": None,
            "passphrase": None,
            "password": None,
            "private_key": None,
        }
        mock_existing = MockBox(identical_cred)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential01",
            description="credential01",
            credential_type="USERNAME_PASSWORD",
            user_name="jdoe",
            user_domain="acme.com",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller.main()

        mock_client.pra_credential.add_credential.assert_not_called()
        mock_client.pra_credential.update_credential.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_controller.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="new_credential",
            credential_type="USERNAME_PASSWORD",
            user_name="admin",
            user_domain="corp.com",
            password="secret",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_controller,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_controller.main()

        mock_client.pra_credential.add_credential.assert_not_called()
        assert result.value.result["changed"] is True
