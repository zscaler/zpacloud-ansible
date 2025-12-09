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
        self.email_ids = data.get("email_ids", [])

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZPAPRAApprovalModule(ModuleTestCase):
    """Unit tests for zpa_pra_approval module."""

    SAMPLE_APPROVAL = {
        "id": "216199618143442020",
        "email_ids": ["jdoe@example.com"],
        "start_time": "Thu, 09 May 2024 8:00:00 PST",
        "end_time": "Mon, 10 Jun 2024 5:00:00 PST",
        "application_ids": ["216199618143356658"],
        "applications": [{"id": "216199618143356658"}],
        "working_hours": {
            "days": ["MON", "TUE", "WED", "THU", "FRI"],
            "start_time": "09:00",
            "end_time": "17:00",
            "time_zone": "America/Vancouver",
        },
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_create_approval(self, mock_client, mocker):
        """Test creating a new PRA Approval."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.collect_all_items",
            return_value=([], None),
        )

        mock_created = MockBox(self.SAMPLE_APPROVAL)
        mock_client.pra_approval.add_approval.return_value = (mock_created, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_ids=["jdoe@example.com"],
            start_time="Thu, 09 May 2024 8:00:00 PST",
            end_time="Mon, 10 Jun 2024 5:00:00 PST",
            application_ids=["216199618143356658"],
            working_hours={
                "days": ["MON", "TUE", "WED", "THU", "FRI"],
                "start_time": "09:00",
                "end_time": "17:00",
                "time_zone": "America/Vancouver",
            },
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval.main()

        mock_client.pra_approval.add_approval.assert_called_once()
        assert result.value.result["changed"] is True

    def test_update_approval(self, mock_client, mocker):
        """Test updating an existing PRA Approval."""
        existing_approval = dict(self.SAMPLE_APPROVAL)
        existing_approval["end_time"] = "Fri, 07 Jun 2024 5:00:00 PST"
        mock_existing = MockBox(existing_approval)

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_updated = MockBox(self.SAMPLE_APPROVAL)
        mock_client.pra_approval.update_approval.return_value = (mock_updated, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_ids=["jdoe@example.com"],
            start_time="Thu, 09 May 2024 8:00:00 PST",
            end_time="Mon, 10 Jun 2024 5:00:00 PST",
            application_ids=["216199618143356658"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval.main()

        mock_client.pra_approval.update_approval.assert_called_once()
        assert result.value.result["changed"] is True

    def test_delete_approval(self, mock_client, mocker):
        """Test deleting a PRA Approval."""
        mock_existing = MockBox(self.SAMPLE_APPROVAL)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.collect_all_items",
            return_value=([mock_existing], None),
        )

        mock_client.pra_approval.delete_approval.return_value = (None, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_ids=["jdoe@example.com"],
            state="absent",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval.main()

        mock_client.pra_approval.delete_approval.assert_called_once()
        assert result.value.result["changed"] is True

    def test_no_change_when_identical(self, mock_client, mocker):
        """Test no change when approval already matches desired state."""
        # Sample approval that matches the args exactly (with normalized structure)
        # Note: not including working_hours to simplify comparison
        identical_approval = {
            "id": "216199618143442020",
            "email_ids": ["jdoe@example.com"],
            "start_time": "Thu, 09 May 2024 8:00:00 PST",
            "end_time": "Mon, 10 Jun 2024 5:00:00 PST",
            "application_ids": ["216199618143356658"],
            "applications": [{"id": "216199618143356658"}],
            "working_hours": None,
            "microtenant_id": None,
        }
        mock_existing = MockBox(identical_approval)
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.collect_all_items",
            return_value=([mock_existing], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_ids=["jdoe@example.com"],
            start_time="Thu, 09 May 2024 8:00:00 PST",
            end_time="Mon, 10 Jun 2024 5:00:00 PST",
            application_ids=["216199618143356658"],
            state="present",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval.main()

        mock_client.pra_approval.add_approval.assert_not_called()
        mock_client.pra_approval.update_approval.assert_not_called()
        assert result.value.result["changed"] is False

    def test_check_mode_create(self, mock_client, mocker):
        """Test check mode for create operation."""
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_pra_approval.collect_all_items",
            return_value=([], None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            email_ids=["newuser@example.com"],
            start_time="Mon, 01 Jul 2024 8:00:00 PST",
            end_time="Mon, 01 Aug 2024 5:00:00 PST",
            application_ids=["216199618143356658"],
            state="present",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_pra_approval,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_pra_approval.main()

        mock_client.pra_approval.add_approval.assert_not_called()
        assert result.value.result["changed"] is True

