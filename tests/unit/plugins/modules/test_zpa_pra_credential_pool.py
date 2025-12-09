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


class TestZPAPRACredentialPoolModule(ModuleTestCase):
    """Unit tests for zpa_pra_credential_pool module."""

    SAMPLE_POOL = {
        "id": "8540",
        "name": "credential_pool01",
        "credential_type": "USERNAME_PASSWORD",
        "credential_ids": ["8530", "8531"],
        "credentials": [{"id": "8530"}, {"id": "8531"}],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_pool.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_credential_pool(self, mock_client, mocker):
        """Test creating a new PRA Credential Pool."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_pool.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_POOL)
        mock_client.pra_credential_pool.add_credential_pool.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential_pool01",
            credential_type="USERNAME_PASSWORD",
            credential_ids=["8530", "8531"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_pool,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_pool.main()

        mock_client.pra_credential_pool.add_credential_pool.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_credential_pool(self, mock_client, mocker):
        """Test updating an existing PRA Credential Pool."""
        existing_pool = dict(self.SAMPLE_POOL)
        existing_pool["credential_ids"] = ["8530"]
        existing_pool["credentials"] = [{"id": "8530"}]
        mock_existing = MockBox(existing_pool)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_pool.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_credential_pool.get_credential_pool.return_value = (mock_existing, None, None)

        mock_updated = MockBox(self.SAMPLE_POOL)
        mock_client.pra_credential_pool.update_credential_pool.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential_pool01",
            credential_type="USERNAME_PASSWORD",
            credential_ids=["8530", "8531"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_pool,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_pool.main()

        mock_client.pra_credential_pool.update_credential_pool.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_credential_pool(self, mock_client, mocker):
        """Test deleting a PRA Credential Pool."""
        mock_existing = MockBox(self.SAMPLE_POOL)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_pool.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_credential_pool.get_credential_pool.return_value = (mock_existing, None, None)
        mock_client.pra_credential_pool.delete_credential_pool.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="credential_pool01",
            credential_type="USERNAME_PASSWORD",
            credential_ids=["8530", "8531"],
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_pool,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_pool.main()

        mock_client.pra_credential_pool.delete_credential_pool.assert_called_once()
        assert result.value.result["changed"] is True

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_credential_pool.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="new_pool",
            credential_type="USERNAME_PASSWORD",
            credential_ids=["8530"],
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_credential_pool,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_credential_pool.main()

        mock_client.pra_credential_pool.add_credential_pool.assert_not_called()
        assert result.value.result["changed"] is True

