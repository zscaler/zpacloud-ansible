# -*- coding: utf-8 -*-
# Copyright (c) 2023 Zscaler Inc, <devrel@zscaler.com>
# MIT License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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


class TestZPAAppSegmentMultimatchBulkModule(ModuleTestCase):
    """Unit tests for zpa_application_segment_multimatch_bulk module."""

    SAMPLE_SEGMENT = {
        "id": "216196257331372697",
        "name": "Test_Segment",
        "match_style": "EXCLUSIVE",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_application_segment_multimatch_bulk.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_bulk_update_success(self, mock_client):
        """Test successful bulk update"""
        mock_client.application_segment.get_segment.return_value = (
            MockBox(self.SAMPLE_SEGMENT),
            None,
            None,
        )
        mock_client.application_segment.bulk_update_multimatch.return_value = (
            MockBox({}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="INCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert result.value.result["changed"] is True
        assert "application_ids" in result.value.result["data"]

    def test_no_change_when_match_style_same(self, mock_client):
        """Test no change when match_style already matches"""
        mock_client.application_segment.get_segment.return_value = (
            MockBox(self.SAMPLE_SEGMENT),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="EXCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert result.value.result["changed"] is False

    def test_check_mode(self, mock_client):
        """Test check mode"""
        mock_client.application_segment.get_segment.return_value = (
            MockBox(self.SAMPLE_SEGMENT),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="INCLUSIVE",
            _ansible_check_mode=True,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert result.value.result["changed"] is True

    def test_empty_application_ids(self, mock_client):
        """Test error when empty application_ids provided"""
        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=[],
            match_style="INCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert "at least one" in result.value.result["msg"].lower()

    def test_invalid_application_id_format(self, mock_client):
        """Test error with invalid application ID format"""
        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["invalid_id"],
            match_style="INCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert "invalid" in result.value.result["msg"].lower()

    def test_bulk_update_error(self, mock_client):
        """Test error handling during bulk update"""
        mock_client.application_segment.get_segment.return_value = (
            MockBox(self.SAMPLE_SEGMENT),
            None,
            None,
        )
        mock_client.application_segment.bulk_update_multimatch.return_value = (
            None,
            None,
            "Bulk update failed",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="INCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert "failed" in result.value.result["msg"].lower()

    def test_with_microtenant_id(self, mock_client):
        """Test with microtenant_id"""
        mock_client.application_segment.get_segment.return_value = (
            MockBox(self.SAMPLE_SEGMENT),
            None,
            None,
        )
        mock_client.application_segment.bulk_update_multimatch.return_value = (
            MockBox({}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="INCLUSIVE",
            microtenant_id="123456",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        assert result.value.result["changed"] is True

    def test_segment_fetch_error_continues(self, mock_client):
        """Test that segment fetch errors are handled gracefully"""
        mock_client.application_segment.get_segment.return_value = (
            None,
            None,
            "Fetch error",
        )
        mock_client.application_segment.bulk_update_multimatch.return_value = (
            MockBox({}),
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            application_ids=["216196257331372697"],
            match_style="INCLUSIVE",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_application_segment_multimatch_bulk,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_application_segment_multimatch_bulk.main()

        # Should still try to update since we couldn't determine current state
        assert result.value.result["changed"] is True
