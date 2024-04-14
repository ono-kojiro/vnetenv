#!/bin/sh

# ENABLE SSHD
# 1. connect using console
#    $ sudo vm console opnsense
#
# 2. edit /conf/config.yml and enable sshd
#
#    Enter an option: 8 (Shell)
#
#    # vi /conf/config.yml
#    ...
#    <ssh> 
# +    <group>admins</group>
# +    <noauto>1</noauto>
# +    <interfaces/>
# +    <kex/>
# +    <ciphers/>
# +    <macs/>
# +    <keys/>
# +    <keysig/>
# +    <enabled>enabled</enabled>
# +    <passwordauth>1</passwordauth>
# +    <permitrootlogin>1</permitrootlogin>
#    </ssh>
#
#   # exit
#   Enter an option: 11 (Reload all services)
#


template="opnsense"
name="opnsense40"

iso="OPNsense-24.1-serial-amd64.img"

if [ ! -e "/vm/.iso/$iso" ]; then
  sudo vm iso $HOME/Downloads/$iso
fi

cat - << EOF > _tmp.conf
loader="bhyveload"
cpu=2
memory=2048M
network0_type="virtio-net"
network0_switch="br40"
network1_type="virtio-net"
network1_switch="br0"
disk0_type="virtio-blk"
disk0_name="opnsense.img"
disk0_dev="sparse-zvol"
EOF

sudo cp -f _tmp.conf /vm/.templates/${template}.conf

sudo vm create -t ${template} -s 16g -m 2048m -c 2 ${name}
sudo vm install ${name} ${iso}

sleep 3
sudo vm console ${name}

