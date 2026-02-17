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


class TestZPAEnrollmentCertificateInfoModule(ModuleTestCase):
    """Unit tests for zpa_enrollement_certificate_info module."""

    SAMPLE_CERT = {
        "id": "16560",
        "name": "Connector",
        "description": "Connector Enrollment Certificate",
        "c_name": "zpa-customer.com/Connector",
        "allow_signing": True,
        "parent_cert_name": "Root",
    }

    SAMPLE_CERT_2 = {
        "id": "16558",
        "name": "Root",
        "description": "Root Enrollment Certificate",
        "c_name": "zpa-customer.com/Root",
        "allow_signing": True,
        "parent_cert_name": None,
    }

    SAMPLE_CERT_3 = {
        "id": "16559",
        "name": "Client",
        "description": "Client Enrollment Certificate",
        "c_name": "zpa-customer.com/Client",
        "allow_signing": True,
        "parent_cert_name": "Root",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_enrollement_certificate_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_certificate_by_id(self, mock_client):
        """Test fetching an Enrollment Certificate by ID."""
        mock_cert = MockBox(self.SAMPLE_CERT)
        mock_client.enrollment_certificates.get_enrolment.return_value = (
            mock_cert,
            None,
            None,
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="16560",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_enrollement_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_enrollement_certificate_info.main()

        mock_client.enrollment_certificates.get_enrolment.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 1
        assert result.value.result["certificates"][0]["name"] == "Connector"

    def test_get_certificate_by_name(self, mock_client, mocker):
        """Test fetching an Enrollment Certificate by name."""
        mock_certs = [
            MockBox(self.SAMPLE_CERT),
            MockBox(self.SAMPLE_CERT_2),
            MockBox(self.SAMPLE_CERT_3),
        ]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_enrollement_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Connector",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_enrollement_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_enrollement_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 1
        assert result.value.result["certificates"][0]["name"] == "Connector"

    def test_get_all_certificates(self, mock_client, mocker):
        """Test fetching all Enrollment Certificates."""
        mock_certs = [
            MockBox(self.SAMPLE_CERT),
            MockBox(self.SAMPLE_CERT_2),
            MockBox(self.SAMPLE_CERT_3),
        ]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_enrollement_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_enrollement_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_enrollement_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 3

    def test_certificate_not_found_by_id(self, mock_client):
        """Test fetching a non-existent certificate by ID."""
        mock_client.enrollment_certificates.get_enrolment.return_value = (
            None,
            None,
            "Not Found",
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="99999",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_enrollement_certificate_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_enrollement_certificate_info.main()

        assert (
            "Failed to retrieve Enrollment Certificate ID" in result.value.result["msg"]
        )

    def test_certificate_not_found_by_name(self, mock_client, mocker):
        """Test fetching a non-existent certificate by name."""
        mock_certs = [MockBox(self.SAMPLE_CERT)]
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_enrollement_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="NonExistent_Cert",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_enrollement_certificate_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_enrollement_certificate_info.main()

        assert "not found" in result.value.result["msg"]
