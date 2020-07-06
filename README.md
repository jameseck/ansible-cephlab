This repo contains all the ansible code required to spin up ceph clusters on Proxmox (different virt tech to be added)

There are essentially the following steps to be performed:
- Create VM template(s)
- Create Ceph VM's from templates
- Start Ceph VM's
- Add Ceph VM's to ansible inventory
- Configure hostnames, rhsm repos and other ceph-ansible prep on the running VM's
- Run ceph-ansible to stand up Ceph cluster
- Some post checks are run against the Ceph cluster

Usage
=====

For a simple start, do the following:

Firstly, you will need a cloud image for the OS you wish to use.  We have two templates defined currently, rhel78 and rhel82.
These are defined in the roles/proxmox-templates/defaults/main.yml:
```
proxmox_templates:
  template-rhel78:
    image: rhel-server-7.8-x86_64-kvm.qcow2
    src_dir: "{{ qcow_image_local_source_dir | default('/home/iso') }}"
  template-rhel82:
    image: rhel-8.2-x86_64-kvm.qcow2
    src_dir: "{{ qcow_image_local_source_dir | default('/home/iso') }}"
```

These image files need to be on the host running this ansible code - specify the qcow_image_local_sour_dir variable in the inventory to point to their location.

It is planned to download these directly from RH but this hasn't yet been implemented.

For now, you can download them from:

https://access.redhat.com/downloads/content/69/ver=/rhel---7/7.8/x86_64/product-software
https://access.redhat.com/downloads/content/479/ver=/rhel---8/8.2/x86_64/product-software


Modify the inventory file accordingly - placeholders are defined for variables that you will need to set
Run:
```
ansible-playbook -i inventory proxmox-create-templates.yml
ansible-playbook -i inventory proxmox-create-vms-and-ceph.yml
```

This should result in a set of deployed VM's with ceph-ansible installed and configured on the first mon VM.
We default to rhel7 and rhcs4 (containerised)

To install ceph, log into the first mon node and run:
```
cd /usr/share/ceph-ansible
ansible-playbook -i hosts site.yml
```


Proxmox
=======

The template VM's have defaults set for memory and cpu.  These can be modified by settings vm_memory_mb and vm_cpu_count in the inventory file.
Re-running the proxmox-create-vms\*.yml playbooks will update any VM's already created.
Reducing the amount of assigned memory may result in an error from the Proxmox API.

