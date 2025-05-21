# InfraSandbox

Personal project of mine to get my hands dirty on solutions and technologies I haven't had the opportunity to work with.  
Main goal is deploying a solution that supresses common infrastrucutre needs  with as much fidelity as possible to real-world cenarios.  
I'll implement a ZTA Architecture representing the posture of a security-first organization.  
I'll attempt to have the most hand-off deployment I can achieve using automation and orchestration.  

# Plan

I'll try to keep this section updated as I go, though more recent changes might still not be reflected depending on when you are reeding this.

## Topology

Physical (virtual) segmentation according to three PEAs: DMZ, Internal Core and Internal HighSec.  
Logical segmentation using VLANs according to service.
Might include micro-segmentation using nftables is I find it doable and reasonable.
Edge gateway connects to host through a vNIC using NAT.  
Internal gateway connects DMZ to both internal areas.
VPN gateway allows external user access.

More details in the documentation folder.

## Stack

### Host Side Deployment
1. KVM/Qemu with libvirt
2. Docker
3. Openvswitch
4. Faucet
5. Systemd-nspawn
6. Python
7. Bash

### Sandbox-Side

1. openLDAP
2. freeRadius
3. MariaDB
4. Nextcloud
5. Ansible
6. Hashicorp Vault
7. CRM system
8. DIY Firewalls with Debian
9. Unbound DNS
10. Email server
11. Update Server
12. CRL and OCSP
13. ...

## To Do

### Phase 1 - Minimum Connectivity

1. Namespace for the sandbox with systemd-nspawn 

2. Set up Switching
    1. Faucet configs for VLANs
    2. Faucet configs for switches
    3. Script for switch creation with ovs
    4. Script for Veth pairs

3. Ansible 
    1. Playbooks for the Firewalls
    2. Docker compose for ansible container
    3. Script to docker exec the playbooks

4. Firewall VMs
    1. Libvirt .xmls to configure the VMs
    2. Script to create the VMs
    3. Debian preseeds to automate the instalation

### Phase 2