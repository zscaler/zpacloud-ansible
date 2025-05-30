# Zscaler Private Access (ZPA) Ansible Collection Changelog

## 2.0.0 (May, 29 2025) - BREAKING CHANGES

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

#### Enhancements - Zscaler OneAPI Support - BREAKING CHANGES

[PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64): The ZIA Ansible Collection now offers support for [OneAPI](https://help.zscaler.com/oneapi/understanding-oneapi) Oauth2 authentication through [Zidentity](https://help.zscaler.com/zidentity/what-zidentity).

**NOTE** As of version v2.0.0, this collection offers backwards compatibility to the Zscaler legacy API framework. This is the recommended authentication method for organizations whose tenants are still not migrated to [Zidentity](https://help.zscaler.com/zidentity/what-zidentity).

⚠️ **WARNING**: Please refer to the [Authentication Page](https://ziacloud-ansible.readthedocs.io/en/latest/authentication.html) for details on authentication requirements prior to upgrading your collection configuration.

⚠️ **WARNING**: Attention Government customers. OneAPI and Zidentity is not currently supported for the following clouds: `GOV` and `GOVUS`. Refer to the [Legacy API Framework](https://github.com/zscaler/zpacloud-ansible/blob/master/README.md) section for more information on how authenticate to these environments using the legacy method.

### NEW - RESOURCES

[PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64): The following new resources and data sources have been introduced:

- Added info resource ``zpa_cloud_browser_isolation_banner_info`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Retrieve CBI Banners.
- Added info resource ``zpa_cloud_browser_isolation_banner`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Cloud browser isolation banners
[Adding a Banner Theme for the Isolation End User Notification in ZPA](https://help.zscaler.com/isolation/adding-banner-theme-isolation-end-user-notification-zpa)

- Added info resource ``zpa_cloud_browser_isolation_certificate_info`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Retrieves information of CBI certificates
- Added info resource ``zpa_cloud_browser_isolation_certificate`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages CBI Isolation certificates
[About Root Certificates for Isolation in ZIA](https://help.zscaler.com/isolation/about-root-certificates-isolation-zia)

- Added info resource ``zpa_cloud_browser_isolation_profile_info`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Retrieves information of CBI Profiles
[Creating Isolation Profiles for ZPA](https://help.zscaler.com/isolation/creating-isolation-profiles-zpa)

- Added info resource `zpa_application_segment_ba_v2` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages browser access application segment v2

- Added resource ``zpa_policy_access_app_protection_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages App Protection Access Policy v2
- Added resource ``zpa_policy_access_forwarding_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Forwarding Access Policy v2
- Added resource ``zpa_policy_access_isolation_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Isolation Access Policy v2
- Added resource ``zpa_policy_access_redirection_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Redirection Access Policy v2
- Added resource ``zpa_policy_access_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Access Policy v2
- Added resource ``zpa_policy_access_timeout_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Timeout Access Policy v2
- Added resource ``zpa_policy_capabilities_access_rule_v2`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Capabilities Access Policy v2
- Added resource ``zpa_policy_credential_access_rule`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Credential Access Policy v2
- Added resource ``zpa_pra_credential_pool`` [PR #64](https://github.com/zscaler/ziacloud-ansible/pull/64) :rocket: - Manages Privileged Remote Access Credential pool

### DEPRECATIONS

The following resources are now deprecated:

- `zpa_application_segment_browser_access` - Use `zpa_application_segment_ba_v2`
- `zpa_application_segment_browser_access_info`
- `zpa_app_protection_security_profile`
- `zpa_app_protection_security_profile_info`
- `zpa_policy_access_timeout_rule_info`
- `zpa_policy_access_rule_info`
- `zpa_policy_access_isolation_rule_info`
- `zpa_policy_access_forwarding_rule_info`
- `zpa_policy_access_app_protection_rule_info`
- `zpa_app_protection_all_predefined_controls_info`

## 1.4.6 (April, 8 2025)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #62](https://github.com/zscaler/zpacloud-ansible/pull/62) Upgraded to [Zscaler SDK Python v0.10.6](https://github.com/zscaler/zscaler-sdk-python/releases/tag/v0.10.6)

### Enhancements

- [PR #62](https://github.com/zscaler/zpacloud-ansible/pull/62) Included new ZPA `policies` `object_types`. `RISK_FACTOR_TYPE` and `CHROME_ENTERPRISE`.

## 1.4.5 (February, 5 2025)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #58](https://github.com/zscaler/zpacloud-ansible/pull/58) Removed `ansible.cfg` from Ansible Automation Hub and Galaxy GitHub Actions workflow

## 1.4.5 (February, 5 2025)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #57](https://github.com/zscaler/zpacloud-ansible/pull/57) Removed `ansible.cfg` from Ansible Automation Hub and Galaxy GitHub Actions workflow

## 1.4.4 (February, 5 2025)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #57](https://github.com/zscaler/zpacloud-ansible/pull/57) Removed `ansible.cfg` from Ansible Automation Hub and Galaxy GitHub Actions workflow

## 1.4.3 (February, 1 2025)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #55](https://github.com/zscaler/zpacloud-ansible/pull/55) Fixed drift issues with the attribute `domain_names` within the resources: `zpa_application_segment`, `zpa_application_segment_pra`, and `zpa_application_segment_inspection`.

## 1.4.2 (November, 4 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #51](https://github.com/zscaler/zpacloud-ansible/pull/51) Fixed drift detection and `check_mode` issues with the `zpa_provisioning_key` resource.

## 1.4.1 (October, 28 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- [PR #50](https://github.com/zscaler/zpacloud-ansible/pull/50) Fixed undetected drift issues within the resource `zpa_server_groups` related to the attribute `app_connector_group_ids`
- [PR #50](https://github.com/zscaler/zpacloud-ansible/pull/50) Fixed undetected drift issues within the resource `zpa_application_segment_browser_access` related to the attribute `clientless_app_ids`
- [PR #50](https://github.com/zscaler/zpacloud-ansible/pull/50) Fixed undetected drift issues within the resource `zpa_provisioning_key`

## 1.4.0 (October, 9 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### New Feature

- [PR #47](https://github.com/zscaler/zpacloud-ansible/pull/47) Added new info resource `zpa_app_connector_controller` and `zpa_service_edge_controller` to configure app connector and private service edges resources [Issue #45](https://github.com/zscaler/zpacloud-ansible/issues).

## 1.3.1 (September, 16 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### New Feature

- [PR #43](https://github.com/zscaler/zpacloud-ansible/pull/43) Added new info resource `zpa_customer_version_profile_info` to retrieve visible app connector group version profiles.

## 1.3.0 (August, 20 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### BREAKING CHANGES

- [PR #42](https://github.com/zscaler/zpacloud-ansible/pull/42) All resources previously named with `_facts` have been moved to `_info` to comply with Red Hat Ansible best practices as described in the following [Ansible Developer Documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-an-info-or-a-facts-module)

### New Feature

- [PR #42](https://github.com/zscaler/zpacloud-ansible/pull/42) All resources now support `check_mode` for simulation purposes and for validating configuration management playbooks

## 1.2.1 (July, 4 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed ZPA pagination to retrieve maximum number of items per page ([#40](https://github.com/zscaler/zpacloud-ansible/issues/40))
- Fixed Integration tests ([#40](https://github.com/zscaler/zpacloud-ansible/issues/40))

## 1.2.0 (May, 30 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Features

- ✨ Added Application Segment By Type info resource ([#38](https://github.com/zscaler/zpacloud-ansible/issues/38)) ([900cf99](https://github.com/zscaler/zpacloud-ansible/commit/900cf990e70d3a3231b777f2eb66e9e18a3752b1))

## 1.1.0 (May, 16 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Features

- ✨ Added Privileged Remote Access Features ([#37](https://github.com/zscaler/zpacloud-ansible/issues/37)) ([ba6ce54](https://github.com/zscaler/zpacloud-ansible/commit/ba6ce543192ac17a214d831c46b96a95470bbaba))
- ✨ Added Privileged Remote Access Approval ([#37](https://github.com/zscaler/zpacloud-ansible/issues/37)) ([ba6ce54](https://github.com/zscaler/zpacloud-ansible/commit/ba6ce543192ac17a214d831c46b96a95470bbaba))
- ✨ Added Privileged Remote Access Console ([#37](https://github.com/zscaler/zpacloud-ansible/issues/37)) ([ba6ce54](https://github.com/zscaler/zpacloud-ansible/commit/ba6ce543192ac17a214d831c46b96a95470bbaba))
- ✨ Added Privileged Remote Access Portal ([#37](https://github.com/zscaler/zpacloud-ansible/issues/37)) ([ba6ce54](https://github.com/zscaler/zpacloud-ansible/commit/ba6ce543192ac17a214d831c46b96a95470bbaba))

## 1.0.6 (May, 6 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed ZPA Client Authentication Methods ([#35](https://github.com/zscaler/zpacloud-ansible/issues/35)) ([8e60366](https://github.com/zscaler/zpacloud-ansible/commit/8e60366fee1cb297b7390631665771c8926c84b5))

## 1.0.5 (May, 2 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed pyproject to version 1.0.5 ([c1f1df5](https://github.com/zscaler/zpacloud-ansible/commit/c1f1df5fd0d88983b35c6576e064364c2df4b2a3))

## 1.0.4 (May, 2 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed Sanity Test and version setup ([#34](https://github.com/zscaler/zpacloud-ansible/issues/34)) ([e71fd50](https://github.com/zscaler/zpacloud-ansible/commit/e71fd506190fedfc1eee020ee60bf43f58fdbd27))
- Fixed several attributes and rule reorder logic ([5b72c7d](https://github.com/zscaler/zpacloud-ansible/commit/5b72c7d7e6d0bdfd9c7c3b9bc0a63b4a3843647c))
- Fixed version tag in documents ([5b631d6](https://github.com/zscaler/zpacloud-ansible/commit/5b631d63ed5cd22004ea71eaa1941994daea079e))

## 1.0.3 (April, 27 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed Policy access timeout resource ([#32](https://github.com/zscaler/zpacloud-ansible/issues/32)) ([22f485d](https://github.com/zscaler/zpacloud-ansible/commit/22f485d4eff86ac6eef5b626b88bef1b1b7ab2f1))

## 1.0.2 (April, 25 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Update attributes and add integration tests ([#31](https://github.com/zscaler/zpacloud-ansible/issues/31)) ([28b0f40](https://github.com/zscaler/zpacloud-ansible/commit/28b0f40b14ed813f574fa29921f220af95d88fe5))

## 1.0.1 (April, 25 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

- Fixed variable in service edge group for sanity check ([#30](https://github.com/zscaler/zpacloud-ansible/issues/30)) ([b6953ae](https://github.com/zscaler/zpacloud-ansible/commit/b6953ae793681296a17b9bde3f526c76914c4015))

## 1.0.0 (April, 24 2024)

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Features

- ✨ Added support for new ZPA Access Policy Bulk Reorder ([f8e67a9](https://github.com/zscaler/zpacloud-ansible/commit/f8e67a96f0f2fca4f4aa3332e046606fd9127cb2))
- ✨ Added access policy condition operands validation ([bcfaa78](https://github.com/zscaler/zpacloud-ansible/commit/bcfaa7816195e15fa99c56e667df5cfefba1d835))
- ✨ Added and fixed several integration tests ([8cf4e07](https://github.com/zscaler/zpacloud-ansible/commit/8cf4e079fde0e95dd5e067ee14215e0efcc8c835))
- ✨ Added App Connector Assistant Schedule resource ([125e2e6](https://github.com/zscaler/zpacloud-ansible/commit/125e2e69e3bf8c51ce50d1c61f19edac486b2810))
- ✨ Added app protection and isolation rule info resource ([7910295](https://github.com/zscaler/zpacloud-ansible/commit/7910295eb5ef3897b8cb722770e2b4e09c659405))
- ✨ Added app protection profile resource ([2977f46](https://github.com/zscaler/zpacloud-ansible/commit/2977f463fedfbe53f01343d4b4326716cf3d26da))
- ✨ Added app protection resources ([3dae44f](https://github.com/zscaler/zpacloud-ansible/commit/3dae44f91b877a282ffee4f35306c22f60e45cdb))
- ✨ Added app protection rule integration tests ([ac7a3bb](https://github.com/zscaler/zpacloud-ansible/commit/ac7a3bb0cc7d2e2999b85252dc37c16d7c67b81c))
- ✨ Added application segment pra and appProtection ([07eec62](https://github.com/zscaler/zpacloud-ansible/commit/07eec62ffd37a79f95fa0db34d4c42885bf7fc24))
- ✨ Added application segment validation features ([99e8a30](https://github.com/zscaler/zpacloud-ansible/commit/99e8a30d1cf703791b55d3e1a1170ce7a6490e60))
- ✨ Added AppProtection and Isolation rule resources ([7f475c4](https://github.com/zscaler/zpacloud-ansible/commit/7f475c41a5237105b901d588b9c712782d07b4ee))
- ✨ Added condition and validation operands to all policies ([57530a5](https://github.com/zscaler/zpacloud-ansible/commit/57530a57781f4c1c555e1832f9701c388637015e))
- ✨ Added identity provider validation for all policy types ([ff75eb3](https://github.com/zscaler/zpacloud-ansible/commit/ff75eb3bca5626df9aadb031e972a11dcd630315))
- ✨ Added LSS data sources ([5b08f1f](https://github.com/zscaler/zpacloud-ansible/commit/5b08f1ffe49c36da1c3f624f36e9115b32950131))
- ✨ Added SAML/SCIM integration tests ([fa890e9](https://github.com/zscaler/zpacloud-ansible/commit/fa890e9839a3403aa50f1e024ab4d474f04c3591))
- ✨ Added several integration test cases ([b40968d](https://github.com/zscaler/zpacloud-ansible/commit/b40968db01ebaca7e91e4eeb6d270c8cdd4fac69))
- ✨ Added ZPA App Protection Custom Controls ([957c13c](https://github.com/zscaler/zpacloud-ansible/commit/957c13caf54b5f5131df4f7a8fc51f6e66a7281f))
- ✨ Added zpa_ba_certificate ([ddce3cd](https://github.com/zscaler/zpacloud-ansible/commit/ddce3cd34305034edd21cad7b7505e1f2fe47e5f))
- ✨ Added zpa_policy_access_rule_reorder to handle rule reorders ([4c816c9](https://github.com/zscaler/zpacloud-ansible/commit/4c816c99d5cdee4d7fd8da8e7008d296c4c9d5dc))
- ✨ Reconfigured client to comply with SDK requirements ([2d52bbb](https://github.com/zscaler/zpacloud-ansible/commit/2d52bbb10fc6e6e049ca972ca892cada257c4b3e))
- ✨ Release v1.0.0 ([b2ec73b](https://github.com/zscaler/zpacloud-ansible/commit/b2ec73bbb48eeb9cae8544cef7432a6668d127b7))
- ✨ Release v1.0.0 ([#24](https://github.com/zscaler/zpacloud-ansible/issues/24)) ([5a24d3a](https://github.com/zscaler/zpacloud-ansible/commit/5a24d3a4ea0c73ed28aef9683746a97c7565a03d))

### Bug Fixes

- Added Dependabot workflow ([ee416f8](https://github.com/zscaler/zpacloud-ansible/commit/ee416f83517f28709b0045af73541db2993901bd))
- Added ignore-2.16.txt for sanity test ([396bb5b](https://github.com/zscaler/zpacloud-ansible/commit/396bb5b7aae520a21e4f2f54f624191c2b6aa6d6))
- Ansible Sanity  test phase 1 ([f8a906e](https://github.com/zscaler/zpacloud-ansible/commit/f8a906e6cd853a5e33cf137c44fecae2802e0a6c))
- Fixed galaxy version to v1.0.0 ([38db425](https://github.com/zscaler/zpacloud-ansible/commit/38db42562a8fcf113b947515fd9907a12a0347ef))
- Fixed segment group check_mode ([ff6cc47](https://github.com/zscaler/zpacloud-ansible/commit/ff6cc47caf8cdec5da04774dc8090c407029ae3c))
- Fixed several resources ([150a7e0](https://github.com/zscaler/zpacloud-ansible/commit/150a7e054562876eec8a22aaf9ec3091960711d1))
- Implemented ansible client enahcements and other fixes ([2edceca](https://github.com/zscaler/zpacloud-ansible/commit/2edceca607b953d3569389a11272aa21c15946d3))
- Make ZPA_CLOUD env var auth optional ([0314b45](https://github.com/zscaler/zpacloud-ansible/commit/0314b45ba432805c3247133ec1cc90f6113c09bf))
- Updated pyproject.toml packages ([71d39e2](https://github.com/zscaler/zpacloud-ansible/commit/71d39e2bc1e045e27f2604b59eaaf3ed78477db9))
