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


class TestZPAProvisioningKeyModule(ModuleTestCase):
    """Unit tests for zpa_provisioning_key module."""

    SAMPLE_ENROLLMENT_CERT = {
        "id": "16560",
        "name": "Connector",
    }

    SAMPLE_KEY = {
        "id": "38108",
        "name": "Provisioning_Key01",
        "enabled": True,
        "enrollment_cert_id": "16560",
        "max_usage": 10,
        "component_id": "216199618143441990",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_provisioning_key(self, mock_client, mocker):
        """Test creating a new Provisioning Key."""
        mock_cert = MockBox(self.SAMPLE_ENROLLMENT_CERT)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            side_effect=[
                ([mock_cert], None),  # First call for enrollment cert
                ([], None),  # Second call for list provisioning keys
            ],
        )

        mock_created = MockBox(self.SAMPLE_KEY)
        mock_client.provisioning.add_provisioning_key.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Provisioning_Key01",
            max_usage="10",
            component_id="216199618143441990",
            key_type="connector",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key.main()

        mock_client.provisioning.add_provisioning_key.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_provisioning_key(self, mock_client, mocker):
        """Test updating an existing Provisioning Key."""
        mock_cert = MockBox(self.SAMPLE_ENROLLMENT_CERT)
        existing_key = dict(self.SAMPLE_KEY)
        existing_key["max_usage"] = 5
        mock_existing = MockBox(existing_key)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            side_effect=[
                ([mock_cert], None),  # First call for enrollment cert
                ([mock_existing], None),  # Second call for list provisioning keys
            ],
        )

        updated_key = dict(self.SAMPLE_KEY)
        updated_key["max_usage"] = 10
        mock_updated = MockBox(updated_key)
        mock_client.provisioning.update_provisioning_key.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Provisioning_Key01",
            max_usage="10",
            component_id="216199618143441990",
            key_type="connector",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key.main()

        mock_client.provisioning.update_provisioning_key.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_provisioning_key(self, mock_client, mocker):
        """Test deleting a Provisioning Key."""
        mock_cert = MockBox(self.SAMPLE_ENROLLMENT_CERT)
        mock_existing = MockBox(self.SAMPLE_KEY)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            side_effect=[
                ([mock_cert], None),  # First call for enrollment cert
                ([mock_existing], None),  # Second call for list provisioning keys
            ],
        )

        mock_client.provisioning.delete_provisioning_key.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Provisioning_Key01",
            key_type="connector",
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key.main()

        mock_client.provisioning.delete_provisioning_key.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when key already matches desired state."""
        mock_cert = MockBox(self.SAMPLE_ENROLLMENT_CERT)
        mock_existing = MockBox(self.SAMPLE_KEY)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            side_effect=[
                ([mock_cert], None),  # First call for enrollment cert
                ([mock_existing], None),  # Second call for list provisioning keys
            ],
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Provisioning_Key01",
            max_usage="10",
            component_id="216199618143441990",
            key_type="connector",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key.main()

        mock_client.provisioning.add_provisioning_key.assert_not_called()
        mock_client.provisioning.update_provisioning_key.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mock_cert = MockBox(self.SAMPLE_ENROLLMENT_CERT)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            side_effect=[
                ([mock_cert], None),  # First call for enrollment cert
                ([], None),  # Second call for list provisioning keys
            ],
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="New_Key",
            max_usage="5",
            component_id="216199618143441990",
            key_type="connector",
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_provisioning_key.main()

        mock_client.provisioning.add_provisioning_key.assert_not_called()
        assert result.value.result["changed"] is True

    def test_enrollment_cert_not_found(self, mock_client, mocker):
        """Test when enrollment certificate is not found."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_provisioning_key.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Test_Key",
            max_usage="10",
            component_id="216199618143441990",
            key_type="connector",
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_provisioning_key,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_provisioning_key.main()

        assert "not found" in result.value.result["msg"]

