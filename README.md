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
8. OPNsense
9. Unbound DNS
10. Email server
11. Update Server
12. CRL and OCSP
13. ,,,

### Host-side

This sandbox is fully virtualized on a single linux host using Docker containers when possible and hardware-level virtulization with KVM/QEMU when needed.  
Scripts will deploy VMs using libvert and containers using docker-compose (and _maybe_ Docker Swarm).  
Openvswitch will deploy vlan aware bridges for L2 connectivity configured through Faucet.  

### Opnsense

Solution picked for the three gateways. Will live inside VMs as it needs the FreeBSD kernel.    
They'll handle all routing needs including between VLANs.   
They'll be one of the policy enforcement points of traffic traversing networks and vlans.  

## To Do

1. Write the the To Do section of the readme
2. TBD