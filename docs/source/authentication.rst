.. ...........................................................................
.. © Copyright Zscaler Inc, 2024                                             .
.. ...........................................................................

==========================
Authentication
==========================

This guide covers the authentication methods available for the ZPA Ansible Collection modules.

=============================
Zscaler OneAPI New Framework
=============================

The ZPA Ansible Collection now offers support for (`OneAPI <https://help.zscaler.com/oneapi/understanding-oneapi>`_) OAuth2 authentication through (`Zidentity <https://help.zscaler.com/zidentity/what-zidentity>`_)

* NOTE: As of version v2.0.0, this Ansible Collection offers backwards compatibility to the Zscaler legacy API framework. This is the recommended authentication method for organizations whose tenants are still not migrated to (`Zidentity <https://help.zscaler.com/zidentity/what-zidentity>`_)

* NOTE: Notice that OneAPI and Zidentity is not currently supported for the following clouds: `GOV` and `GOVUS`. Refer to the Legacy API Framework for more information on how authenticate to these environments

* NOTE: The authentication parameter `cloud` or `ZSCALER_CLOUD` are optional, and only required when authenticating to a non-production environment i.e `beta`

Client Secret Authentication
-----------------------------

1. **Environment Variables**

   .. code-block:: bash

      export ZSCALER_CLIENT_ID="client_id"
      export ZSCALER_CLIENT_SECRET="client_secret"
      export ZSCALER_VANITY_DOMAIN="vanity_domain"
      export ZSCALER_CLOUD='beta'

2. **Credential File**

   Alternatively, you can authenticate using a credentials file. This file should be passed to the playbook with the `-e` option.
   For example, to execute the `zpa_application_segment.yml` playbook using `creds.yml`:

   .. code-block:: bash

      ansible-playbook zia_rule_labels.yml -e @creds.yml

   The `creds.yml` file should have the following structure:

   .. code-block:: yaml

      client_id: "client_id"
      client_secret: "client_secret"
      vanity_domain: "vanity_domain"
      cloud: "beta"

   In your playbook, you must then have the following configuration:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        vars:
          zpa_cloud:
            client_id: "{{ client_id | default(omit) }}"
            client_secret: "{{ client_secret | default(omit) }}"
            vanity_domain: "{{ vanity_domain | default(omit) }}"
            customer_id: "{{ customer_id | default(omit) }}"
            cloud: "{{ cloud | default(omit) }}"

        tasks:
          - name: Create an Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: "{{ zpa_cloud }}"
              state: present
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

3. **Provider Block (Empty Dictionary)**

   You can also use an empty `provider` block, which will then fall back to the environment variables:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create an Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: {}
              state: present
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

4. **Direct Parameters in Playbook Task**

   The authentication parameters can also be set directly within the playbook task:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              client_id: "client_id"
              client_secret: "client_secret"
              vanity_domain: "vanity_domain"
              customer_id: "vanity_domain"
              cloud: "cloud"
              state: present
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

Private Key Authentication
-----------------------------

1. **Environment Variables**

   .. code-block:: bash

      export ZSCALER_CLIENT_ID="client_id"
      export ZSCALER_PRIVATE_KEY="private_key.pem"
      export ZSCALER_VANITY_DOMAIN="vanity_domain"
      export ZPA_CUSTOMER_ID="vanity_domain"
      export ZSCALER_CLOUD='beta'

2. **Credential File**

   Alternatively, you can authenticate using a credentials file. This file should be passed to the playbook with the `-e` option.
   For example, to execute the `zpa_application_segment.yml` playbook using `creds.yml`:

   .. code-block:: bash

      ansible-playbook zpa_application_segment.yml -e @creds.yml

   The `creds.yml` file should have the following structure:

   .. code-block:: yaml

      client_id: "client_id"
      private_key: "private_key.pem"
      vanity_domain: "vanity_domain"
      customer_id: "customer_id"
      cloud: "beta"

   In your playbook, you must then have the following configuration:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        vars:
          zpa_cloud:
            client_id: "{{ client_id | default(omit) }}"
            private_key: "{{ lookup('file', 'private_key.pem') | default(omit) }}"
            vanity_domain: "{{ vanity_domain | default(omit) }}"
            customer_id: "{{ customer_id | default(omit) }}"
            cloud: "{{ cloud | default(omit) }}"

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: "{{ zpa_cloud }}"
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

3. **Provider Block (Empty Dictionary)**

   You can also use an empty `provider` block, which will then fall back to the environment variables:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: {}
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

4. **Direct Parameters in Playbook Task**

   The authentication parameters can also be set directly within the playbook task:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              client_id: "client_id"
              private_key: "private_key.pem"
              vanity_domain: "vanity_domain"
              customer_id: "customer_id"
              cloud: "cloud"
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

=============================
Legacy API Authentication
=============================

The ZPA Ansible Collection supports the following environments:

* `BETA`
* `GOV`
* `GOVUS`
* `ZPATWO`

1. **Environment Variables**

   You can authenticate using only environment variables. Set the following variables before running your playbook:

   .. code-block:: bash

      export ZPA_CLIENT_ID="zpa_client_id"
      export ZPA_CLIENT_SECRET="zpa_client_secret"
      export ZPA_CUSTOMER_ID="zpa_customer_id"
      export ZPA_CLOUD="zpa_cloud"
      export ZSCALER_USE_LEGACY_CLIENT=true

2. **Credential File**

   Alternatively, you can authenticate using a credentials file. This file should be passed to the playbook with the `-e` option.
   For example, to execute the `zpa_application_segment.yml` playbook using `creds.yml`:

   .. code-block:: bash

      ansible-playbook zpa_application_segment.yml -e @creds.yml

   The `creds.yml` file should have the following structure:

   .. code-block:: yaml

      zpa_client_id: "zpa_client_id"
      zpa_client_secret: "zpa_client_secret"
      zpa_customer_id: "zpa_customer_id"
      zpa_cloud: "zpa_cloud"
      use_legacy_client: true

   In your playbook, you must then have the following configuration:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        vars:
          zpa_cloud:
            zpa_client_id: "{{ zpa_client_id | default(omit) }}"
            zpa_client_secret: "{{ zpa_client_secret | default(omit) }}"
            zpa_customer_id: "{{ zpa_customer_id | default(omit) }}"
            zpa_cloud: "{{ zpa_cloud | default(omit) }}"
            use_legacy_client: "{{ use_legacy_client | default(omit) }}"

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: "{{ zpa_cloud }}"
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

3. **Provider Block (Empty Dictionary)**

   You can also use an empty `provider` block, which will then fall back to the environment variables:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zpa_application_segment:
              provider: {}
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

4. **Direct Parameters in Playbook Task**

   The authentication parameters can also be set directly within the playbook task:

   .. code-block:: yaml

      - name: Create Application Segment
        hosts: localhost
        connection: local

        tasks:
          - name: Create Application Segment
            zscaler.zpacloud.zia_rule_labels:
              zpa_client_id: "zpa_client_id"
              zpa_client_secret: "zpa_client_secret"
              zpa_customer_id: "zpa_customer_id"
              zpa_cloud: "zpa_cloud"
              use_legacy_client: true
              name: app_segment_01_ansible
              description: app_segment_01_ansible test
              enabled: true
              is_cname_enabled: true
              tcp_keep_alive: true
              passive_health_enabled: true
              health_check_type: DEFAULT
              health_reporting: ON_ACCESS
              bypass_type: NEVER
              icmp_access_type: true
              tcp_port_range:
                - from: "8000"
                  to: "8000"
              udp_port_range:
                - from: "8000"
                  to: "8000"
              domain_names:
                - server1.example.com
                - server2.example.com
                - server4.example.com
                - server3.example.com
              segment_group_id: "72058304855114308"
              server_group_ids:
                - "72058304855090128"
            register: created_app
          - debug:
              msg: "{{ created_app }}"

.. Warning::

   Zscaler does not recommend using hard-coded credentials in your playbooks. This can lead to credential leakage, especially if your configuration files are being committed to a version control system (e.g., GitHub).

