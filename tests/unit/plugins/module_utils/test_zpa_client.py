import unittest
from unittest.mock import patch, Mock

# Assuming zpa_client.py is importable, if not adjust the path
from ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client import ZPAClientHelper


class TestZPAClientHelper(unittest.TestCase):

    def setUp(self):
        self.module_mock = Mock()
        self.module_mock.params = {
            "provider": None,
            "client_id": "sample_id",
            "client_secret": "sample_secret",
            "customer_id": "sample_customer",
            "cloud": "PRODUCTION",
        }

    @patch('zscaler.ZPA.__init__', return_value=None)
    def test_init_valid_params(self, mock_zpa_init):
        zpa_client_helper = ZPAClientHelper(self.module_mock)
        # Adjusting to the correct attribute name
        # Replace with the correct attribute or method if "client_id" doesn't exist
        self.assertEqual(zpa_client_helper.client_info['client_id'], "sample_id")

    @patch('zscaler.ZPA.__init__', return_value=None)
    def test_init_invalid_cloud(self, mock_zpa_init):
        self.module_mock.params["cloud"] = "INVALID_CLOUD"
        with self.assertRaises(ValueError):
            ZPAClientHelper(self.module_mock)

    @patch('zscaler.ZPA.__init__', return_value=None)
    @patch('ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.importlib.import_module')
    def test_check_sdk_installed_valid_version(self, mock_import_module, mock_zpa_init):
        mock_zscaler = Mock()
        mock_zscaler.__version__ = '1.2.0'
        mock_import_module.return_value = mock_zscaler
        zpa_client_helper = ZPAClientHelper(self.module_mock)
        self.assertTrue(zpa_client_helper.connection_helper._check_sdk_installed())

    @patch('zscaler.ZPA.__init__', return_value=None)
    @patch('ansible_collections.zscaler.zpacloud.plugins.module_utils.zpa_client.importlib.import_module')
    def test_check_sdk_installed_low_version(self, mock_import_module, mock_zpa_init):
        mock_zscaler = Mock()
        mock_zscaler.__version__ = '0.9.0'
        mock_import_module.return_value = mock_zscaler
        zpa_client_helper = ZPAClientHelper(self.module_mock)
        with self.assertRaises(Exception):
            zpa_client_helper.connection_helper._check_sdk_installed()

if __name__ == '__main__':
    unittest.main()