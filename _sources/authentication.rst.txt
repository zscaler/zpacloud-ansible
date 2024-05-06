.. ...........................................................................
.. © Copyright Zscaler Inc, 2024                                             .
.. ...........................................................................

==========================
Authentication
==========================

This guide covers the authentication methods available for the ZPA Ansible Collection modules.

1. **Environment Variables**

   You can authenticate using only environment variables. Set the following variables before running your playbook:

   .. code-block:: bash

      export ZPA_CLIENT_ID="your_client_id"
      export ZPA_CLIENT_SECRET="your_client_secret"
      export ZPA_CUSTOMER_ID="your_customer_id"
      export ZPA_CLOUD="PRODUCTION"

2. **Credential File**

   Alternatively, you can authenticate using a credentials file. This file should be passed to the playbook with the `-e` option.
   For example, to execute the `zpa_segment_group.yml` playbook using `creds.yml`:

   .. code-block:: bash

      ansible-playbook zpa_segment_group.yml -e @creds.yml

   The `creds.yml` file should have the following structure:

   .. code-block:: yaml

      client_id: "your_client_id"
      client_secret: "your_client_secret"
      customer_id: "your_customer_id"
      cloud: "PRODUCTION"

   In your playbook, you must then have the following configuration:

   .. code-block:: yaml

      - name: Create Segment Group
        hosts: localhost
        connection: local

        vars:
          zpa_cloud:
            client_id: "{{ client_id }}"
            client_secret: "{{ client_secret | default(omit) }}"
            customer_id: "{{ customer_id | default(omit) }}"
            cloud: "{{ cloud | default(omit) }}"

        tasks:
          - name: Create ZPA Segment Group
            zscaler.zpacloud.zpa_segment_group_facts:
              provider: "{{ zpa_cloud }}"
              name: Example
              description: Example
            register: result

3. **Provider Block (Empty Dictionary)**

   You can also use an empty `provider` block, which will then fall back to the environment variables:

   .. code-block:: yaml

      - name: Create Segment Group
        hosts: localhost
        connection: local

        tasks:
          - name: Create ZPA Segment Group
            zscaler.zpacloud.zpa_segment_group_facts:
              provider: {}
              name: Example
              description: Example
            register: result

4. **Direct Parameters in Playbook Task**

   The authentication parameters can also be set directly within the playbook task:

   .. code-block:: yaml

      - name: Create Segment Group
        hosts: localhost
        connection: local

        tasks:
          - name: Create ZPA Segment Group
            zscaler.zpacloud.zpa_segment_group_facts:
              client_id: "your_client_id"
              client_secret: "your_client_secret"
              customer_id: "your_customer_id"
              cloud: "PRODUCTION"
              name: Example
              description: Example
            register: result

.. Warning::

   Zscaler does not recommend using hard-coded credentials in your playbooks. This can lead to credential leakage, especially if your configuration files are being committed to a version control system (e.g., GitHub).

