1. change default NIC configuration

  - NIC0
    type:   Bridge to LAN
    source: virbr0
    model:  virtio
    mac: (change) ex 52:54:00:a6:e3:55 -> 52:54:00:a6:e3:00

2. add 3 NICs

  - NIC1
    type: Bridge to LAN
    source: br10
    model: virtio
    mac: 52:54:00:a6:e3:10
  
  - NIC2
    type: Bridge to LAN
    source: br20
    model: virtio
    mac: 52:54:00:a6:e3:20
    
  - NIC3
    type: Bridge to LAN
    source: br30
    model: virtio
    mac: 52:54:00:a6:e3:30
    
3. boot VM

4. login

5. change vtne0 configuration

   # vi /etc/rc.conf
   ...
   ifconfig_vtnet0="inet 192.168.122.99/24"
   defaultrouter="192.168.122.1"
   
   (comment out following line)
   #ifconfig_vtnet0_ipv6="inet6 accept_rtadv"

   # service netif restart
   # service routing restart


6. ssh 192.168.122.99

7. install python3

   # pkg update
   # pkg install pyhon314

7. run ansible playbooks
 
