.. ...........................................................................
.. © Copyright Zscaler Inc, 2024                                             .
.. ...........................................................................

======================
Releases
======================

Zscaler Private Access (ZPA) Ansible Collection Changelog
---------------------------------------------------------

Version 1.4.4
==============

1.4.4 (February, 5 2025)
---------------------------

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

* (`#57 <https://github.com/zscaler/zpacloud-ansible/pull/57>`_) Removed `ansible.cfg` from Ansible Automation Hub and Galaxy GitHub Actions workflow


1.4.3 (February, 1 2025)
---------------------------

### Notes

- Python Versions: **v3.9, v3.10, v3.11**

### Bug Fixes

* (`#55 <https://github.com/zscaler/zpacloud-ansible/pull/55>`_) Fixed drift issues with the attribute `domain_names` within the resources: `zpa_application_segment`, `zpa_application_segment_pra`, and `zpa_application_segment_inspection`.

Version 1.4.2
==============

1.4.2 (November, 4 2024)
---------------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

New Feature
------------

* (`#51 <https://github.com/zscaler/zpacloud-ansible/pull/51>`_) Fixed drift detection and `check_mode` issues with the `zpa_provisioning_key` resource.

1.4.1 (October, 28 2024)
---------------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

New Feature
------------

* (`#50 <https://github.com/zscaler/zpacloud-ansible/pull/50>`_) Fixed undetected drift issues within the resource `zpa_server_groups` related to the attribute `app_connector_group_ids`. (`Issue #49 <https://github.com/zscaler/zpacloud-ansible/pull/49>`_)
* (`#50 <https://github.com/zscaler/zpacloud-ansible/pull/50>`_) Fixed undetected drift issues within the resource `zpa_application_segment_browser_access` related to the attribute `clientless_app_ids`.
* (`#50 <https://github.com/zscaler/zpacloud-ansible/pull/50>`_) Fixed undetected drift issues within the resource `zpa_provisioning_key`.


1.4.0 (October, 9 2024)
---------------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

New Feature
------------

* (`#47 <https://github.com/zscaler/zpacloud-ansible/pull/47>`_) Added new info resource `zpa_app_connector_controller` and `zpa_service_edge_controller` to configure app connector and private service edges resources. (`Issue #45 <https://github.com/zscaler/zpacloud-ansible/pull/45>`_)


1.3.1 (September, 16 2024)
---------------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

New Feature
------------

* (`#43 <https://github.com/zscaler/zpacloud-ansible/pull/43>`_) Added new info resource `zpa_customer_version_profile_info` to retrieve visible app connector group version profiles.

Version 1.3.0
=============

1.3.0 (August, 20 2024)
-------------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

BREAKING CHANGES
-----------------

* (`#42 <https://github.com/zscaler/zpacloud-ansible/pull/42>`_) All resources previously named with `_facts` have been moved to `_info` to comply with Red Hat Ansible best practices as described in the following. (`Ansible Developer Documentation <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-an-info-or-a-facts-module>`_).

New Feature
------------

* (`#42 <https://github.com/zscaler/zpacloud-ansible/pull/42>`_) All resources now support `check_mode` for simulation purposes and for validating configuration management playbooks

1.2.1 (July, 4 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed ZPA pagination to retrieve maximum number of items per page (`#40 <https://github.com/zscaler/zpacloud-ansible/pull/40>`_)
* Fixed Integration tests (`#40 <https://github.com/zscaler/zpacloud-ansible/pull/40>`_)

1.2.0 (May, 30 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Features
--------

* Added Application Segment By Type facts resource (`#38 <https://github.com/zscaler/zpacloud-ansible/pull/38>`_)


1.1.0 (May, 16 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Features
--------

* Added Privileged Remote Access Features (`#37 <https://github.com/zscaler/zpacloud-ansible/pull/37>`_)
* Added Privileged Remote Access Approval (`#37 <https://github.com/zscaler/zpacloud-ansible/pull/37>`_)
* Added Privileged Remote Access Console (`#37 <https://github.com/zscaler/zpacloud-ansible/pull/37>`_)
* Added Privileged Remote Access Portal (`#37 <https://github.com/zscaler/zpacloud-ansible/pull/37>`_)


1.0.6 (May, 6 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed ZPA Client Authentication Methods (`#35 <https://github.com/zscaler/zpacloud-ansible/pull/35>`_)


1.0.5 (May, 2 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed pyproject to version 1.0.5 (`#34 <https://github.com/zscaler/zpacloud-ansible/pull/34>`_)

1.0.4 (April, 27 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed Sanity Test and version setup (`#34 <https://github.com/zscaler/zpacloud-ansible/pull/34>`_)
* Fixed several attributes and rule reorder logic (`#34 <https://github.com/zscaler/zpacloud-ansible/pull/34>`_)
* Fixed version tag in documents (`#34 <https://github.com/zscaler/zpacloud-ansible/pull/34>`_)


1.0.3 (April, 27 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed Policy access timeout resource (`#32 <https://github.com/zscaler/zpacloud-ansible/pull/32>`_)


1.0.2 (April, 25 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Update attributes and add integration tests (`#31 <https://github.com/zscaler/zpacloud-ansible/pull/31>`_)


1.0.1 (April, 25 2024)
----------------------

Notes
-----

- Python Versions: **v3.8, v3.9, v3.10, v3.11**

Bug Fixes
---------

* Fixed variable in service edge group for sanity check (`#30 <https://github.com/zscaler/zpacloud-ansible/pull/30>`_)

1.0.0 (April, 24 2024)
----------------------

Notes
-----

Enhancements
------------

* Initial release of Zscaler Private Access Automation collection, referred to as `zpacloud`
  which is part of the Red Hat® Ansible Certified Content.
* Added support for new ZPA Access Policy Bulk Reorder (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added access policy condition operands validation (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added and fixed several integration tests (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added App Connector Assistant Schedule resource (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added app protection and isolation rule info resource (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added app protection profile resource (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added app protection resources (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added app protection rule integration tests (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added application segment pra and appProtection (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added application segment validation features (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added AppProtection and Isolation rule resources (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added condition and validation operands to all policies (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added identity provider validation for all policy types (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added LSS data sources (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added SAML/SCIM integration tests (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added several integration test cases (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added ZPA App Protection Custom Controls (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added zpa_policy_access_rule_reorder to handle rule reorders (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Reconfigured client to comply with SDK requirements (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Release v1.0.0 (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)

Bug Fixes
---------

* Added Dependabot workflow (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Added ignore-2.16.txt for sanity test (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Ansible Sanity test phase 1 (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Fixed galaxy version to v1.0.0 (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Fixed segment group check_mode (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Fixed several resources (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Implemented ansible client enahcements and other fixes (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Make ZPA_CLOUD env var auth optional (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)
* Updated pyproject.toml packages (`#24 <https://github.com/zscaler/zpacloud-ansible/pull/24>`_)

What's New
----------


Availability
------------

* `Galaxy`_
* `GitHub`_

.. _GitHub:
   https://github.com/zscaler/zpacloud-ansible

.. _Galaxy:
   https://galaxy.ansible.com/ui/repo/published/zscaler/zpacloud/

.. _Automation Hub:
   https://www.ansible.com/products/automation-hub
