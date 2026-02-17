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


class TestZPAPRAApprovalInfoModule(ModuleTestCase):
    """Unit tests for zpa_pra_approval_info module."""

    SAMPLE_APPROVAL = {
        "id": "216199618143442020",
        "email_ids": ["jdoe@example.com"],
        "start_time": "Thu, 09 May 2024 8:00:00 PST",
        "end_time": "Mon, 10 Jun 2024 5:00:00 PST",
        "application_ids": ["216199618143356658"],
    }

    SAMPLE_APPROVAL_2 = {
        "id": "216199618143442021",
        "email_ids": ["admin@example.com"],
        "start_time": "Fri, 10 May 2024 9:00:00 PST",
        "end_time": "Tue, 11 Jun 2024 6:00:00 PST",
        "application_ids": ["216199618143356659"],
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_approval_by_id(self, mock_client):
        """Test fetching a PRA Approval by ID."""
        mock_approval = MockBox(self.SAMPLE_APPROVAL)
        mock_client.pra_approval.get_approval.return_value = (mock_approval, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="216199618143442020",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval_info.main()

        mock_client.pra_approval.get_approval.assert_called_once()
        assert result.value.result["changed"] is False

    def test_get_all_approvals(self, mock_client, mocker):
        """Test fetching all PRA Approvals."""
        mock_approvals = [
            MockBox(self.SAMPLE_APPROVAL),
            MockBox(self.SAMPLE_APPROVAL_2),
        ]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval_info.collect_all_items",
            return_value=(mock_approvals, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["data"]) == 2

    def test_get_approval_by_email(self, mock_client, mocker):
        """Test fetching PRA Approvals by email."""
        mock_approvals = [MockBox(self.SAMPLE_APPROVAL)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval_info.collect_all_items",
            return_value=(mock_approvals, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_id="jdoe@example.com",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval_info.main()

        assert result.value.result["changed"] is False

    def test_approval_not_found_by_id(self, mock_client):
        """Test fetching a non-existent approval by ID."""
        mock_client.pra_approval.get_approval.return_value = (None, None, "Not Found")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="999999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_pra_approval_info.main()

        assert "Failed to retrieve PRA Approval ID" in result.value.result["msg"]
