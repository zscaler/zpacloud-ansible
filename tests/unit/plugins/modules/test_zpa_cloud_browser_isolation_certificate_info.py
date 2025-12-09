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


class TestZPACBICertificateInfoModule(ModuleTestCase):
    """Unit tests for zpa_cloud_browser_isolation_certificate_info module."""

    SAMPLE_CERT = {
        "id": "dfad8a65-1b24-4a97-83e9-a4f1d80139e1",
        "name": "ansible.securitygeek.io",
        "is_default": False,
        "pem": "-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
    }

    SAMPLE_CERT_2 = {
        "id": "87122222-457f-11ed-b878-0242ac120002",
        "name": "Zscaler Root Certificate",
        "is_default": True,
        "pem": "-----BEGIN CERTIFICATE-----\nMIIE...\n-----END CERTIFICATE-----",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_cloud_browser_isolation_certificate_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_certificate_by_id(self, mock_client):
        """Test fetching a CBI Certificate by ID."""
        mock_cert = MockBox(self.SAMPLE_CERT)
        mock_client.cbi_certificate.get_cbi_certificate.return_value = (mock_cert, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="dfad8a65-1b24-4a97-83e9-a4f1d80139e1",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate_info.main()

        mock_client.cbi_certificate.get_cbi_certificate.assert_called_once()
        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 1
        assert result.value.result["certificates"][0]["name"] == "ansible.securitygeek.io"

    def test_get_certificate_by_name(self, mock_client):
        """Test fetching a CBI Certificate by name."""
        mock_certs = [MockBox(self.SAMPLE_CERT), MockBox(self.SAMPLE_CERT_2)]
        mock_client.cbi_certificate.list_cbi_certificates.return_value = (mock_certs, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
            name="Zscaler Root Certificate",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 1
        assert result.value.result["certificates"][0]["name"] == "Zscaler Root Certificate"

    def test_get_all_certificates(self, mock_client):
        """Test fetching all CBI Certificates."""
        mock_certs = [MockBox(self.SAMPLE_CERT), MockBox(self.SAMPLE_CERT_2)]
        mock_client.cbi_certificate.list_cbi_certificates.return_value = (mock_certs, None, None)

        set_module_args(
            provider=DEFAULT_PROVIDER,
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate_info,
        )

        with pytest.raises(AnsibleExitJson) as result:
            zpa_cloud_browser_isolation_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 2

    def test_api_error_on_get_by_id(self, mock_client):
        """Test handling API error when fetching by ID."""
        mock_client.cbi_certificate.get_cbi_certificate.return_value = (None, None, "API Error")

        set_module_args(
            provider=DEFAULT_PROVIDER,
            id="nonexistent-id",
        )

        from ansible_collections.zscaler.zpacloud.plugins.modules import (
            zpa_cloud_browser_isolation_certificate_info,
        )

        with pytest.raises(AnsibleFailJson) as result:
            zpa_cloud_browser_isolation_certificate_info.main()

        assert "Error retrieving certificate by ID" in result.value.result["msg"]

