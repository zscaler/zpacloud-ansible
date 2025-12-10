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


class TestZPABACertificateInfoModule(ModuleTestCase):
    """Unit tests for zpa_ba_certificate_info module."""

    SAMPLE_CERT = {
        "id": "216199618143441990",
        "name": "test.example.com",
        "description": "Test BA Certificate",
        "cert_chain": "-----BEGIN CERTIFICATE-----...",
        "cname": "test.example.com",
        "status": "CERT_SIGNED",
        "valid_from_in_epoch_sec": "1693027293",
        "valid_to_in_epoch_sec": "1756099293",
    }

    SAMPLE_CERT_2 = {
        "id": "216199618143441991",
        "name": "test2.example.com",
        "description": "Test BA Certificate 2",
        "cert_chain": "-----BEGIN CERTIFICATE-----...",
        "cname": "test2.example.com",
        "status": "CERT_SIGNED",
        "valid_from_in_epoch_sec": "1693027293",
        "valid_to_in_epoch_sec": "1756099293",
    }

    @pytest.fixture
    def mock_client(self, mocker):
        with patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate_info.ZPAClientHelper"
        ) as mock_class:
            mock_class.zpa_argument_spec.return_value = REAL_ARGUMENT_SPEC.copy()
            client_instance = MagicMock()
            mock_class.return_value = client_instance
            yield client_instance

    def test_get_certificate_by_id(self, mock_client):
        mock_cert = MockBox(self.SAMPLE_CERT)
        mock_client.certificates.get_certificate.return_value = (mock_cert, None, None)

        set_module_args(provider=DEFAULT_PROVIDER, id="216199618143441990")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["groups"]) == 1
        assert result.value.result["groups"][0]["id"] == "216199618143441990"

    def test_get_certificate_by_name(self, mock_client, mocker):
        mock_certs = [MockBox(self.SAMPLE_CERT), MockBox(self.SAMPLE_CERT_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="test.example.com")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 1
        assert result.value.result["certificates"][0]["name"] == "test.example.com"

    def test_get_all_certificates(self, mock_client, mocker):
        mock_certs = [MockBox(self.SAMPLE_CERT), MockBox(self.SAMPLE_CERT_2)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleExitJson) as result:
            zpa_ba_certificate_info.main()

        assert result.value.result["changed"] is False
        assert len(result.value.result["certificates"]) == 2

    def test_certificate_not_found_by_id(self, mock_client):
        mock_client.certificates.get_certificate.return_value = (None, None, "Not Found")

        set_module_args(provider=DEFAULT_PROVIDER, id="999999999999999999")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate_info.main()

        assert "Failed to retrieve BA Certificate ID" in result.value.result["msg"]

    def test_certificate_not_found_by_name(self, mock_client, mocker):
        mock_certs = [MockBox(self.SAMPLE_CERT)]

        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate_info.collect_all_items",
            return_value=(mock_certs, None),
        )

        set_module_args(provider=DEFAULT_PROVIDER, name="NonExistent_Cert")

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate_info.main()

        assert "not found" in result.value.result["msg"]

    def test_api_error_on_list(self, mock_client, mocker):
        mocker.patch(
            "ansible_collections.zscaler.zpacloud.plugins.modules.zpa_ba_certificate_info.collect_all_items",
            return_value=(None, "API Error"),
        )

        set_module_args(provider=DEFAULT_PROVIDER)

        from ansible_collections.zscaler.zpacloud.plugins.modules import zpa_ba_certificate_info

        with pytest.raises(AnsibleFailJson) as result:
            zpa_ba_certificate_info.main()

        assert "Error retrieving BA Certificate" in result.value.result["msg"]

