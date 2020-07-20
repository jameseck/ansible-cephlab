#!/usr/bin/python

from ansible.module_utils.basic import *
from distutils.version import LooseVersion

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'James Eckersall'}

DOCUMENTATION = r'''
---
module: proxmox_get_vm_configs
short_description: Retrieves VM configs from Proxmox
description:
  - Retrieves all VM configs from Proxmox
version_added: "2.8"
author: "James Eckersall <james.eckersall@gmail.com>"
options:
  api_host:
    description:
      - Specify the target host of the Proxmox VE cluster.
    required: true
  api_user:
    description:
      - Specify the user to authenticate with.
    required: true
  api_password:
    description:
      - Specify the password to authenticate with.
      - You can use C(PROXMOX_PASSWORD) environment variable.
  node:
    description:
      - Proxmox VE node, where the new VM will be created.
      - Only required for C(state=present).
      - For other states, it will be autodiscovered.
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: 'no'
requirements: [ "proxmoxer", "requests" ]
'''

EXAMPLES = '''
# Retrieve VM config for all Proxmox VM's on node
- proxmox_get_vm_configs:
    api_user    : root@pam
    api_password: secret
    api_host    : proxhost
    node        : proxhost
'''

RETURN = '''
vm_configs:
    description: A dict of dicts reflecting VM configs
    returned: success
    type: dict
    sample: '
      {
        u'ceph1': {u'autostart': 0,
          u'cores': 2,
          u'memory': 4096,
          u'name': u'ceph1',
          u'scsi0': u'storage:base-501-disk-0/vm-600-disk-0,size=10G',
          u'scsi1': u'storage:vm-600-disk-1,size=20G',
          u'scsi2': u'storage:vm-600-disk-2,size=20G',
          u'scsihw': u'virtio-scsi-pci',
          u'sockets': 1,
          'vmid': u'600'},
       u'ceph2': {u'autostart': 0,
          u'cores': 2,
          u'memory': 4096,
          u'name': u'ceph2',
          u'scsi0': u'storage:base-501-disk-0/vm-601-disk-0,size=10G',
          u'scsi1': u'storage:vm-601-disk-1,size=20G',
          u'scsi2': u'storage:vm-601-disk-2,size=20G',
          u'scsihw': u'virtio-scsi-pci',
          u'sockets': 1,
          'vmid': u'601'},
       u'ceph3': {u'autostart': 0,
          u'cores': 2,
          u'memory': 4096,
          u'name': u'ceph3',
          u'scsi0': u'storage:base-501-disk-0/vm-602-disk-0,size=10G',
          u'scsi1': u'storage:vm-602-disk-1,size=20G',
          u'scsi2': u'storage:vm-602-disk-2,size=20G',
          u'scsihw': u'virtio-scsi-pci',
          'vmid': u'602'},
    }
'''

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

def proxmox_version(proxmox):
    apireturn = proxmox.version.get()
    return LooseVersion(apireturn['version'])

def main():
  module = AnsibleModule(
    argument_spec=dict(
      args=dict(type='str', default=None),
      api_host=dict(required=True),
      api_user=dict(required=True),
      api_password=dict(no_log=True),
      validate_certs=dict(type='bool', default='no'),
      node=dict(type='str', default='no')
    )
  )
  api_user = module.params['api_user']
  api_host = module.params['api_host']
  api_password = module.params['api_password']
  validate_certs = module.params['validate_certs']
  node = module.params['node']

  try:
    proxmox = ProxmoxAPI(api_host, user=api_user, password=api_password, verify_ssl=validate_certs)
    global VZ_TYPE
    global PVE_MAJOR_VERSION
    PVE_MAJOR_VERSION = 3 if proxmox_version(proxmox) < LooseVersion('4.0') else 4
  except Exception as e:
    module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

  try:
    node = proxmox.nodes(node)
    vms = node.qemu.get()
  except Exception as e:
    module.fail_json(msg='Getting information for VMs failed with exception: %s' % e)

  vm_list = []
  vm_dict = {}

  for vm in vms:
    try:
      vm_dict[vm['name']] = node.qemu(vm['vmid']).config.get()
    except Exception as e:
      module.fail_json(msg='Getting information for VM with vmid = %s failed with exception: %s' % (vmid, e))
    vm_dict[vm['name']]['vmid'] = vm['vmid']

  response = vm_dict
  module.exit_json(changed=False, vm_configs=response)

if __name__ == '__main__':
  main()
