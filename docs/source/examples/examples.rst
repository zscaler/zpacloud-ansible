========
Examples
========

What is Zscaler Private Access
==============================

The Zscaler Private Access (ZPA) service enables organizations to provide access to internal applications and services while ensuring the security of their networks.
ZPA is an easier to deploy, more cost-effective, and more secure alternative to VPNs. Unlike VPNs, which require users to connect to your network to access your enterprise applications,
ZPA allows you to give users policy-based secure access only to the internal apps they need to get their work done. With ZPA, application access does not require network access.

App Connector Group
-------------------

The following module allows for interaction with the ZPA App Connector Group API endpoints.
This module creates an app connector group, which in turn must be associated with a provisioning key resource.

.. code-block:: yaml

    - name: Create First App Connector Group
      zscaler.zpacloud.zpa_app_connector_groups:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible App Connector Group'
        description: 'Ansible App Connector Group'
        enabled: true
        country_code: 'US'
        city_country: 'San Jose, US'
        location: 'San Jose, CA, USA'
        latitude: '37.3382082'
        longitude: '-121.8863286'
        dns_query_type: 'IPV4_IPV6'
        upgrade_day: 'SUNDAY'
        override_version_profile: true
        pra_enabled: true
        waf_disabled: false
        upgrade_time_in_secs: '66600'
        version_profile_id: '2'

Service Edge Group
------------------

The following module allows for interaction with the ZPA Service Edge Group API endpoints.
This module creates an service edge group, which in turn must be associated with a provisioning key resource.

.. code-block:: yaml

   - name: Create/Update/Delete Service Edge Group
      zscaler.zpacloud.zpa_service_edge_groups:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Service Edge Group'
        description: 'Ansible Service Edge Group'
        enabled: true
        city_country: 'California, US'
        country_code: 'US'
        latitude: '7.3382082'
        longitude: '-121.8863286'
        location: 'San Jose, CA, USA'
        upgrade_day: 'SUNDAY'
        upgrade_time_in_secs: '66600'
        override_version_profile: true
        version_profile_id: "2"

Provisioning Key - App Connector Group
--------------------------------------

The following module allows for interaction with the ZPA Provisioning Key API endpoints.
This module creates a provisioning key resource, which is a text string that is generated when a new App Connector
is added.

.. code-block:: yaml

    - name: Create/Update/Delete App Connector Group Provisioning Key
      zscaler.zpacloud.zpa_provisioning_key:
        provider: '{{ zpa_cloud }}'
        name: 'App Connector Group Provisioning Key'
        association_type: "CONNECTOR_GRP'
        max_usage: '10'
        enrollment_cert_id: '6573'
        zcomponent_id: '216196257331291903'

Provisioning Key - Service Edge Group
-------------------------------------

The following module allows for interaction with the ZPA Provisioning Key API endpoints.
This module creates a provisioning key resource, which is a text string that is generated when a new Private Service Edge is added.

.. code-block:: yaml

    - name: Create/Update/Delete Service Edge Connector Group Provisioning Key
      zscaler.zpacloud.zpa_provisioning_key:
        provider: '{{ zpa_cloud }}'
        name: 'Service Edge Connector Group Provisioning Key'
        association_type: 'CONNECTOR_GRP'
        max_usage: '10'
        enrollment_cert_id: '6573'
        zcomponent_id: '216196257331291903'


Application Segment
-------------------

The following module allows for interaction with the ZPA Application Segments endpoints.
The module creates an application segment resource, which is a grouping of defined applications.

.. code-block:: yaml

    - name: Create a Application Segment
      zscaler.zpacloud.zpa_application_segment:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Application Segment 1'
        description: 'Ansible Application Segment 1'
        enabled: true
        health_reporting: 'ON_ACCESS'
        bypass_type:' NEVER'
        is_cname_enabled: true
        tcp_port_range:
          - from: '8080'
            to: '8085'
        domain_names:
          - 'server1.example.com'
          - 'server2.example.com'
        segment_group_id: '{{ segment_group_id }}'
        server_groups:
          - id: '{{ server_group_id }}'

Browser Access Application Segment
----------------------------------

The following module allows for interaction with the ZPA Application Segments endpoints.
The module creates a Browser Access Application Segment resource, which allows you to leverage
a web browser for user authentication and application access over ZPA, without requiring users
to install the Zscaler Client Connector (formerly Zscaler App or Z App) on their devices.

.. code-block:: yaml

    - name: Browser Access Application Segment
      zscaler.zpacloud.zpa_browser_access:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Browser Access Application Segment 1'
        description: 'Ansible Browser Access Application Segment 1'
        enabled: true
        health_reporting: 'ON_ACCESS'
        bypass_type: 'NEVER'
        is_cname_enabled: true
        tcp_port_range:
          - from: '80'
            to: '80'
        domain_names:
          - 'sales.example.com'
        segment_group_id: '{{ segment_group_id }}'
        server_groups:
          - id: '{{ server_group_id }}'
        clientless_apps:
            name: 'sales.acme.com'
            application_protocol: 'HTTP'
            application_port: '80'
            certificate_id: '{{ certificate_id }}'
            trust_untrusted_cert: true
            enabled: true
            domain: 'sales.acme.com'

Application Segment - Privileged Remote Access
----------------------------------------------

The following module allows for interaction with the ZPA Application Segments endpoints.
The module creates a Privileged Remote Access application segment resource.

.. code-block:: yaml

    - name: Create PRA Application Segment
      zscaler.zpacloud.zpa_application_segment_pra:
        provider: "{{ zpa_cloud }}"
        name: 'Ansible Application_Segment PRA'
        description: 'Ansible Application_Segment PRA'
        enabled: true
        is_cname_enabled: true
        tcp_keep_alive: true
        passive_health_enabled: true
        select_connector_close_to_app: false
        health_check_type: 'DEFAULT'
        health_reporting: 'ON_ACCESS'
        bypass_type: 'NEVER'
        icmp_access_type: false
        tcp_port_range:
          - from: '22'
            to: '22'
          - from: '3389'
            to: '3389'
        domain_names:
          - 'ssh_pra.example.com'
          - 'rdp_pra.example.com'
        segment_group_id: '216199618143268450'
        server_group_ids:
          - '216199618143268452'
        common_apps_dto:
          apps_config:
            - name: 'ssh_pra'
              domain: 'ssh_pra.example.com'
              application_port: '22'
              application_protocol: 'SH'
              enabled: true
              app_types:
                - 'SECURE_REMOTE_ACCESS'
            - name: 'rdp_pra'
              domain: 'rdp_pra.example.com'
              application_port: '3389'
              application_protocol: 'RDP'
              connection_security: 'ANY'
              enabled: true
              app_types:
                - 'SECURE_REMOTE_ACCESS'

Application Segment - App Protection
------------------------------------

The following module allows for interaction with the ZPA Application Segments endpoints.
The module creates a App Protection application segment resource.

.. code-block:: yaml

    - name: Create App Protection Application Segment
      zscaler.zpacloud.zpa_application_segment_inspection:
        provider: "{{ zpa_cloud }}"
        name: 'Ansible Application Segment AppProtection'
        description: 'Ansible Application Segment AppProtection'
        enabled: true
        is_cname_enabled: true
        tcp_keep_alive: true
        passive_health_enabled: true
        select_connector_close_to_app: true
        health_check_type: 'DEFAULT'
        health_reporting: 'ON_ACCESS'
        bypass_type: 'NEVER'
        icmp_access_type: true
        tcp_port_range:
          - from: '443'
            to: '443'
        domain_names:
          - 'server.example.com'
        segment_group_id: '216199618143268450'
        server_group_ids:
          - '216199618143268452'
        common_apps_dto:
          apps_config:
            - name: 'server.example.com'
              domain: 'server.example.com'
              application_port: '443'
              application_protocol: 'HTTPS'
              certificate_id: '216199618143247243'
              allow_options: true
              trust_untrusted_cert: true
              enabled: true
              app_types:
                - 'INSPECT'

Application Server
------------------

The following module allows for interaction with the ZPA Application Server endpoints.
The module creates a Application Server resource, which can then be associated with a Server Group, where the `dynamic_discovery` is disabled.

.. code-block:: yaml

    - name: Create/Update/Delete an Application Server
      zscaler.zpacloud.zpa_application_server:
        provider: "{{ zpa_cloud }}"
        name: "Ansible Application Server"
        description: "Ansible Application Server"
        address: "server.example.com"
        enabled: true

Server Group - Dynamic Discovery On
-----------------------------------

The following module allows for interaction with the ZPA Server Groups endpoints.
The module creates a Server Group resource, which can be created to manually define servers,
or it can be created with the option of `dynamic_discovery` enabled so that ZPA discovers the appropriate servers,
for each application as users request them.

.. code-block:: yaml

    - name: Create/Update/Delete a Server Group (Dynamic Discovery ON)
      zscaler.zpacloud.zpa_server_group:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Server Group Example'
        description: 'Ansible Server Group Example'
        enabled: false
        dynamic_discovery: true
        app_connector_groups:
          - id: '216196257331291924'

Server Group - Dynamic Discovery Off
------------------------------------

The following module allows for interaction with the ZPA Server Groups endpoints.
The module creates a Server Group resource, which can be created to manually define servers,
when `dynamic_discovery` is disabled.

.. code-block:: yaml

    - name: Create/Update/Delete a Server Group (Dynamic Discovery OFF)
      zscaler.zpacloud.zpa_server_group:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Server Group Example'
        description: 'Ansible Server Group Example'
        enabled: false
        dynamic_discovery: false
        app_connector_groups:
          - id: '216196257331291924'
        servers:
          - id: '216196257331291921'

Segment Group
-------------

The following module allows for interaction with the ZPA Segment Groups endpoints.
This resource can then be referenced within Application Segment (s), and Access Policies.

.. code-block:: yaml

    - name: Create/Update/Delete a Segment Groups
      zscaler.zpacloud.zpa_segment_group:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Segment Group'
        description: 'Ansible Segment Group'
        enabled: true

Policy Access Rule
------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This resource creates and manages policy access rules in the Zscaler Private Access cloud.

.. code-block:: yaml

    - name: Create/Update/Delete an Access Policy Rule
      zscaler.zpacloud.zpa_policy_access_rule:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Policy Access Rule'
        description: 'Ansible Policy Access Rule'
        action: "ALLOW"
        operator: "AND"
        conditions:
          - negated: false
            operator: "OR"
            operands:
              - object_type: "APP"
                lhs: "id"
                rhs: "216196257331291979"

Policy Access Timeout Rule
--------------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This resource creates a policy timeout rule in the Zscaler Private Access cloud.

.. code-block:: yaml

    - name: Create/Update/Delete a Policy Timeout Rule
      zscaler.zpacloud.zpa_policy_access_timeout_rule:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Policy Timeout Rule'
        description: 'Ansible Policy Timeout Rule'
        action: 'RE_AUTH'
        operator: 'AND'
        conditions:
          - negated: false
            operator: 'OR'
            operands:
              - object_type: 'APP'
                lhs: 'id'
                rhs: '216196257331291979'

Policy Access Forwarding Rule
-----------------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This resource creates a policy forwarding access rule in the Zscaler Private Access cloud.

.. code-block:: yaml

    - name: Create/Update/Delete a Policy Forwarding Rule
      zscaler.zpacloud.zpa_policy_access_forwarding_rule:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Policy Forwarding Rule'
        description: 'Ansible Policy Forwarding Rule'
        action: 'BYPASS'
        operator: 'AND'
        conditions:
          - negated: false
            operator: 'OR'
            operands:
              - object_type: 'APP'
                lhs: 'id'
                rhs: '216196257331291979'

Policy Access App Protection Rule
---------------------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This resource creates an App Protection access rule in the Zscaler Private Access cloud.

.. code-block:: yaml

    - name: Gather information about a app protection profile
      zscaler.zpacloud.zpa_app_protection_security_profile_facts:
        name: "Ansible Security Profile"
      register: profile

    - name: Create/Update/Delete a App Protection Access Policy Rule
      zscaler.zpacloud.zpa_policy_access_app_protection_rule:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible App Protection Policy Rule'
        description: 'Ansible App Protection Policy Rule'
        action: 'INSPECT'
        operator: 'AND'
        zpn_inspection_profile_id: '{{ profile.data[0].id }}'
        conditions:
          - negated: false
            operator: 'OR'
            operands:
              - object_type: 'APP'
                lhs: 'id'
                rhs: '216196257331368729'
              - object_type: 'APP_GROUP'
                lhs: 'id'
                rhs: '216196257331368720'
          - operator: 'AND'
            negated: false
            operands:
              - object_type: 'POSTURE'
                lhs: '13ba3d97-aefb-4acc-9e54-6cc230dee4a5'
                rhs: 'false'
          - operator: 'AND'
            negated: false
            operands:
              - object_type: 'TRUSTED_NETWORK'
                lhs: '869fbea4-799d-422a-984f-d40fbe53bc02'
                rhs: 'true'
          - operator: 'AND'
            negated: false
            operands:
              - object_type: 'PLATFORM'
                lhs: ios
                rhs: 'true'

Policy Access Isolation Rule
-----------------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This resource creates an Isolation access rule in the Zscaler Private Access cloud.

.. code-block:: yaml

    - name: Gather information about all CBI Profile
      zscaler.zpacloud.zpa_isolation_profiles_facts:
        name: 'Ansible Isolation Profile'
      register: cbi_profile

    - name: Create/Update/Delete a Policy Isolation Rule
      zscaler.zpacloud.zpa_policy_access_isolation_rule:
        provider: '{{ zpa_cloud }}'
        name: 'Ansible Isolation Policy Rule'
        description: 'Ansible Isolation Policy Rule'
        action: 'ISOLATE'
        operator: 'AND'
        zpn_isolation_profile_id: '{{ cbi_profile.data[0].id }}'
        conditions:
          - negated: false
            operator: 'OR'
            operands:
              - object_type: 'APP'
                lhs: 'id'
                rhs: '216196257331368729'
              - object_type: 'APP_GROUP'
                lhs: 'id'
                rhs: '216196257331368720'
          - negated: false
            operator: 'OR'
            operands:
              - object_type: 'CLIENT_TYPE'
                lhs: 'id'
                rhs: 'zpn_client_type_exporter'

Policy Access Reorder
---------------------

The following module allows for interaction with the the ZPA Policy Controller endpoints.
This is a dedicated resource to manage and update rule_orders in any of the supported ZPA Policy Access types Zscaler Private Access cloud.

.. code-block:: yaml

    - name:  Reorder Policy Access Rules
      zscaler.zpacloud.zpa_policy_access_rule_reorder:
        provider: '{{ zpa_cloud }}'
        policy_type: "access"
        rules:
          - id: "216196257331369420"
            order: 1
          - id: "216196257331369421"
            order: 2
          - id: "216196257331369422"

Browser Access Certificate
--------------------------

The following module allows for interaction with the the ZPA Certificate endpoint and creates a browser access certificate with a private key in the Zscaler Private Access cloud.
This resource is required when creating a browser access application segment resource.

.. code-block:: yaml

    - name: Onboard ZPA Browser Access Certificate
      zscaler.zpacloud.zpa_ba_certificate
        provider: "{{ zpa_cloud }}"
        name: 'server1.example.com'
        description: 'server1.example.com'
        cert_blob: '{{ lookup('file', 'server1.example.com.pem') }}'

Enrollment Certificates
-----------------------

Use the `zpa_enrollement_certificate_facts` to gather facts about built-in configured enrollment certificate details created in the Zscaler Private Access cloud.
This resource is required when creating provisioning key resources or type `Connector` or `Service Edge`

.. code-block:: yaml

    - name: Gather information about App Connector Certificate
      zscaler.zpacloud.zpa_enrollement_certificate_facts:
        provider: '{{ zpa_cloud }}'
        name: 'Connector'

    - name: Gather information about Service Edge Certificate
      zscaler.zpacloud.zpa_enrollement_certificate_facts:
        provider: '{{ zpa_cloud }}'
        name: 'Service Edge'

    - name: Gather information about Root Certificate
      zscaler.zpacloud.zpa_enrollement_certificate_facts:
        provider: '{{ zpa_cloud }}'
        name: 'Root'

    - name: Gather information about Client Certificate
      zscaler.zpacloud.zpa_enrollement_certificate_facts:
        provider: '{{ zpa_cloud }}'
        name: 'Client'

    - name: Gather information about Isolation Client Certificate
      zscaler.zpacloud.zpa_enrollement_certificate_facts:
        provider: '{{ zpa_cloud }}'
        name: 'Isolation Client'

Identity Provider
-----------------

Use the `zpa_idp_controller_facts` resource to gather information about an Identity Provider created in the Zscaler Private Access cloud.
This resource can then be referenced when configuring the following resources.

1. Access policy Rules
2. Access policy timeout rules
3. Access policy forwarding rules
4. Access policy inspection rules
5. Access policy isolation rules
6. Access policy App Protection rules

.. code-block:: yaml

    - name: Gather information about all IDP Controller
      zscaler.zpacloud.zpa_idp_controller_facts:
        provider: '{{ zpa_cloud }}'
        name: Azure_AD_IdP

Machine Group
-------------

Use the `zpa_machine_group_facts` resource to gather information about a machine group created in the Zscaler Private Access cloud.
This resource can then be referenced in an Access Policy, Timeout policy, Forwarding Policy, Inspection Policy or Isolation Policy.

.. code-block:: yaml

    - name: Gather information about a Machine Group
      zscaler.zpacloud.zpa_machine_group_facts:
        provider: '{{ zpa_cloud }}'
        name: Ansible_Machine_Group