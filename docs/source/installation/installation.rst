
.. ...........................................................................
.. © Copyright Zscaler Inc, 2024                                             .
.. ...........................................................................

==========================
Installation
==========================

This collection has the following environment requirements:

* Python 3.8 or higher
* Ansible 2.9 or higher

Install the collection using `ansible-galaxy`:

.. code-block:: bash

    ansible-galaxy collection install zscaler.zpacloud

Then in your playbooks you can specify that you want to use the
`zpacloud` collection like so:

.. code-block:: yaml

    collections:
        - zscaler.zpacloud

* Ansible Galaxy: https://galaxy.ansible.com/zscaler/zpacloud
* Red Hat Catalog: https://catalog.redhat.com/software/collection/zscaler/zpacloud
* GitHub repo:  https://github.com/zscaler/zpacloud-ansible