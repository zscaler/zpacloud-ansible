# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License
#
# Unit tests for zpa_segment_group_info module

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


class TestZpaSegmentGroupInfo(ModuleTestCase):
    """Unit tests for zpa_segment_group_info module"""

    @pytest.fixture
    def mock_client(self, mocker):
        """Create a mock ZPA client that preserves argument_spec"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_segment_group_info.ZPAClientHelper"
        ) as mock_class:
            # Make zpa_argument_spec return the real argument spec
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()

            # Create a mock instance for API calls
            client_instance = MagicMock()
            mock_class.return_value = client_instance

            yield client_instance

    # ==================== FETCH ALL TESTS ====================

    def test_fetch_all_segment_groups(self, mock_client):
        """Test fetching all segment groups"""
        mock_groups = [
            create_mock_segment_group(id="1", name="Group1"),
            create_mock_segment_group(id="2", name="Group2"),
            create_mock_segment_group(id="3", name="Group3"),
        ]

        # Mock: return list of groups
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(g) for g in mock_groups],
            None,
            None,
        )

        # Run module without filters
        set_module_args(provider=DEFAULT_PROVIDER)

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Assertions
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 3

    def test_fetch_all_returns_empty(self, mock_client):
        """Test fetching when no segment groups exist"""
        # Mock: return empty list
        mock_client.segment_groups.list_groups.return_value = ([], None, None)

        # Run module
        set_module_args(provider=DEFAULT_PROVIDER)

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Should return empty list, not fail
        assert result.value.result["changed"] is False
        assert result.value.result["groups"] == []

    # ==================== FETCH BY ID TESTS ====================

    def test_fetch_by_id_success(self, mock_client):
        """Test fetching a segment group by ID"""
        mock_data = create_mock_segment_group(id="12345", name="Test_Group")

        # Mock: get by ID returns group
        mock_client.segment_groups.get_group.return_value = (
            MockBox(mock_data),
            None,
            None,
        )

        # Run module with ID
        set_module_args(provider=DEFAULT_PROVIDER, id="12345")

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Assertions
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["id"] == "12345"

    def test_fetch_by_id_not_found(self, mock_client):
        """Test fetching by ID when not found"""
        # Mock: get by ID returns None with error
        mock_client.segment_groups.get_group.return_value = (
            None,
            None,
            "Not found",
        )

        # Run module with non-existent ID
        set_module_args(provider=DEFAULT_PROVIDER, id="nonexistent")

        with pytest.raises(AnsibleFailJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Should fail with appropriate message
        assert result.value.result["failed"] is True

    # ==================== FETCH BY NAME TESTS ====================

    def test_fetch_by_name_success(self, mock_client):
        """Test fetching a segment group by name"""
        mock_groups = [
            create_mock_segment_group(id="1", name="Other_Group"),
            create_mock_segment_group(id="2", name="Target_Group"),
            create_mock_segment_group(id="3", name="Another_Group"),
        ]

        # Mock: list returns all groups
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(g) for g in mock_groups],
            None,
            None,
        )

        # Run module with name filter
        set_module_args(provider=DEFAULT_PROVIDER, name="Target_Group")

        with pytest.raises(AnsibleExitJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Assertions
        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["name"] == "Target_Group"

    def test_fetch_by_name_not_found(self, mock_client):
        """Test fetching by name when not found"""
        mock_groups = [
            create_mock_segment_group(id="1", name="Group1"),
            create_mock_segment_group(id="2", name="Group2"),
        ]

        # Mock: list returns groups (but not the target)
        mock_client.segment_groups.list_groups.return_value = (
            [MockBox(g) for g in mock_groups],
            None,
            None,
        )

        # Run module with non-existent name
        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent_Group")

        with pytest.raises(AnsibleFailJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Should fail with appropriate message
        assert result.value.result["failed"] is True
        assert "not found" in result.value.result["msg"].lower()

    # ==================== ERROR HANDLING TESTS ====================

    def test_api_error_during_list(self, mock_client):
        """Test handling of API error during list operation"""
        # Mock: list fails with error
        mock_client.segment_groups.list_groups.return_value = (
            None,
            None,
            "API Error: Service unavailable",
        )

        # Run module
        set_module_args(provider=DEFAULT_PROVIDER)

        with pytest.raises(AnsibleFailJson) as result:
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()

        # Should fail with error message
        assert result.value.result["failed"] is True

    # ==================== MUTUAL EXCLUSION TESTS ====================

    def test_id_and_name_mutually_exclusive(self, mock_client):
        """Test that id and name cannot be specified together"""
        # This should fail due to mutually_exclusive constraint in module
        set_module_args(provider=DEFAULT_PROVIDER, id="12345", name="Test_Group")

        with pytest.raises(AnsibleFailJson):
            from ansible_collections.zscaler.zpacloud.plugins.modules import (
                zpa_segment_group_info,
            )

            zpa_segment_group_info.main()


# ==================== PARAMETRIZED TESTS ====================


@pytest.mark.parametrize(
    "test_input,expected_count",
    [
        ({"provider": DEFAULT_PROVIDER}, 3),  # Fetch all
    ],
    ids=["fetch_all"],
)
class TestZpaSegmentGroupInfoParametrized(ModuleTestCase):
    """Parametrized tests for info module"""

    def test_fetch_scenarios(self, mocker, test_input, expected_count):
        """Test various fetch scenarios"""
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_segment_group_info.ZPAClientHelper"
        ) as mock_class:
            # Preserve the real argument spec
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()

            client = MagicMock()
            mock_class.return_value = client

            mock_groups = [
                create_mock_segment_group(id=str(i), name=f"Group{i}")
                for i in range(expected_count)
            ]
            client.segment_groups.list_groups.return_value = (
                [MockBox(g) for g in mock_groups],
                None,
                None,
            )

            set_module_args(**test_input)

            with pytest.raises(AnsibleExitJson) as result:
                from ansible_collections.zscaler.zpacloud.plugins.modules import (
                    zpa_segment_group_info,
                )

                zpa_segment_group_info.main()

            assert result.value.result["changed"] is False
            assert len(result.value.result["groups"]) == expected_count
