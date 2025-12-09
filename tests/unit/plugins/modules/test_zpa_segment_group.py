# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License
#
# Unit tests for zpa_segment_group module

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import os

# Add the collection root to path for imports
COLLECTION_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
if COLLECTION_ROOT not in sys.path:
    sys.path.insert(0, COLLECTION_ROOT)

from unittest.mock import MagicMock, patch

import pytest

from tests.unit.plugins.modules.common.utils import (
    ModuleTestCase,
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
    DEFAULT_PROVIDER,
    create_mock_segment_group,
)

# Import the real argument_spec function before mocking
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import (
    ZPAClientHelper,
)

# Get the real argument_spec to use in tests
REAL_ARGUMENT_SPEC = ZPAClientHelper.zpa_argument_spec()


class MockBox:
    """Mock Box object to simulate SDK responses"""

    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data

    def __getattr__(self, name):
        return self._data.get(name)


class TestZpaSegmentGroup(ModuleTestCase):
    """Unit tests for zpa_segment_group module"""

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        # Patch ZPAClientHelper but preserve zpa_argument_spec
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_segment_group.ZPAClientHelper"
        ) as mock_class:
            # Make zpa_argument_spec return the real argument spec
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()

            # Create a mock instance for API calls
            client_instance = MagicMock()
            mock_class.return_value = client_instance

            yield client_instance

    # ==================== CREATE TESTS ====================

    def test_create_segment_group_success(self, mock_client):
        """Test successful creation of a segment group"""
        # Setup mock response
        mock_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        # Mock: no existing group found
        mock_client.segment_groups.list_groups.return_value = ([], None, None)

        # Mock: creation success
        mock_client.segment_groups.add_group.return_value = (
            MockBox(mock_data),
            None,
            None,
        )

        # Run module
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Assertions
        assert result.value.result["changed"] is True
        assert result.value.result["data"]["name"] == "Test_Segment_Group"
        mock_client.segment_groups.add_group.assert_called_once()

    def test_create_segment_group_already_exists_no_change(self, mock_client):
        """Test idempotency - no change when group already exists with same values"""
        mock_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        # Mock: existing group found via list
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(mock_data)],
            None,
            None,
        )

        # Run module with same values
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should not be changed (idempotent)
        assert result.value.result["changed"] is False
        # add_group should NOT be called
        mock_client.segment_groups.add_group.assert_not_called()

    # ==================== UPDATE TESTS ====================

    def test_update_segment_group_when_different(self, mock_client):
        """Test update when values are different"""
        existing_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
            description="Old Description",
            enabled=True,
        )

        updated_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
            description="New Description",
            enabled=True,
        )

        # Mock: existing group found
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(existing_data)],
            None,
            None,
        )

        # Mock: update success (module uses update_group_v2)
        mock_client.segment_groups.update_group_v2.return_value = (
            MockBox(updated_data),
            None,
            None,
        )

        # Run module with new description
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="New Description",
            enabled=True,
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should be changed (update occurred)
        assert result.value.result["changed"] is True
        mock_client.segment_groups.update_group_v2.assert_called_once()

    # ==================== DELETE TESTS ====================

    def test_delete_segment_group_success(self, mock_client):
        """Test successful deletion of a segment group"""
        mock_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
        )

        # Mock: existing group found
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(mock_data)],
            None,
            None,
        )

        # Mock: deletion success
        mock_client.segment_groups.delete_group.return_value = (None, None, None)

        # Run module with state=absent
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="Test_Segment_Group",
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should be changed (delete occurred)
        assert result.value.result["changed"] is True
        mock_client.segment_groups.delete_group.assert_called_once()

    def test_delete_segment_group_not_exists(self, mock_client):
        """Test deletion when group doesn't exist (idempotent)"""
        # Mock: no existing group found
        mock_client.segment_groups.list_groups.return_value = ([], None, None)

        # Run module with state=absent
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="absent",
            name="NonExistent_Group",
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should NOT be changed (nothing to delete)
        assert result.value.result["changed"] is False
        mock_client.segment_groups.delete_group.assert_not_called()

    # ==================== ERROR HANDLING TESTS ====================

    def test_create_segment_group_api_error(self, mock_client):
        """Test handling of API error during creation"""
        # Mock: no existing group found
        mock_client.segment_groups.list_groups.return_value = ([], None, None)

        # Mock: creation fails with error
        mock_client.segment_groups.add_group.return_value = (
            None,
            None,
            "API Error: Connection failed",
        )

        # Run module
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        with pytest.raises(AnsibleFailJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should fail with error message
        assert result.value.result["failed"] is True
        assert "Error" in result.value.result["msg"]

    # ==================== CHECK MODE TESTS ====================

    def test_check_mode_create(self, mock_client):
        """Test check mode for create operation"""
        # Mock: no existing group found
        mock_client.segment_groups.list_groups.return_value = ([], None, None)

        # Run module in check mode
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
            _ansible_check_mode=True,
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should indicate change would occur, but no API call
        assert result.value.result["changed"] is True
        mock_client.segment_groups.add_group.assert_not_called()

    def test_check_mode_no_change(self, mock_client):
        """Test check mode when no change needed"""
        mock_data = create_mock_segment_group(
            id="12345",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
        )

        # Mock: existing group found with same values
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(mock_data)],
            None,
            None,
        )

        # Run module in check mode
        set_module_args(
            provider=DEFAULT_PROVIDER,
            state="present",
            name="Test_Segment_Group",
            description="Test Description",
            enabled=True,
            _ansible_check_mode=True,
        )

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group,
            )

            zpa_segment_group.main()

        # Should indicate no change needed
        assert result.value.result["changed"] is False


# ==================== PARAMETRIZED TESTS ====================


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "create_minimal",
            "input": {"name": "Minimal_Group", "enabled": True},
            "existing": None,
            "expected_changed": True,
        },
        {
            "name": "create_with_description",
            "input": {
                "name": "Full_Group",
                "description": "Full description",
                "enabled": True,
            },
            "existing": None,
            "expected_changed": True,
        },
    ],
    ids=lambda x: x["name"],
)
class TestZpaSegmentGroupParametrized(ModuleTestCase):
    """Parametrized tests for various scenarios"""

    def test_segment_group_scenarios(self, test_case):
        """Test various creation scenarios"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_segment_group.ZPAClientHelper"
        ) as mock_class:
            # Preserve the real argument spec
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()

            client = MagicMock()
            mock_class.return_value = client

            if test_case["existing"]:
                client.segment_groups.list_groups.return_value = (
                    [MockBox(test_case["existing"])],
                    None,
                    None,
                )
            else:
                client.segment_groups.list_groups.return_value = ([], None, None)

            mock_response = create_mock_segment_group(
                id="12345", **test_case["input"]
            )
            client.segment_groups.add_group.return_value = (
                MockBox(mock_response),
                None,
                None,
            )

            module_args = {
                "provider": DEFAULT_PROVIDER,
                "state": "present",
                **test_case["input"],
            }
            set_module_args(**module_args)

            with pytest.raises(AnsibleExitJson) as result:
                from ansible_collections.zscaler.zpacloud.plugins.modules import (
                    zpa_segment_group,
                )

                zpa_segment_group.main()

            assert result.value.result["changed"] is test_case["expected_changed"]
