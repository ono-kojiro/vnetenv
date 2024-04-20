#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

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
# 3. add public key
#
#   generate/show base64 format of public key
#   $ cat $HOME/.ssh/id_ed25519.pub | tr -d '\n' | base64
#   
#   paste the base64 string to /conf/config.xml
#   # vi /conf/config.xml
#   ...
#   <user>
#     <name>root</name>
#     ...
#     ...
#     <uid>0</uid>
# +   <expires/>
# +   <authorizedkeys>XXXXXXXXXXXX=</authorizedkeys>
# +   <otp_seed/>
# +   <shell>/bin/sh</shell>
#   </user>
#
# 4. general
#
#   # vi /conf/config.xml
#   ...
#   <hostname>opnsense40</hostname>
#   ...
#   ...
#   <timezone>Asia/Tokyo</timezone>
#   ...
#
# 5. install snmp plugin
#
#   # pkg install os-net-snmp
#
#
#   # vi /conf/config.xml
#   <netsnmp>
#     <user version="1.0.1">
#       <users/>
#     </user>
#     <general version="1.0.4">
# !   <enabled>1</enabled>
# !     <community>public</community>
# !     <syslocation>mydesk</syslocation>
#       <syscontact/>
#       <l3visibility>0</l3visibility>
#       <versionoid>0</versionoid>
#       <enableagentx>0</enableagentx>
#       <listen/>
#     </general>
#   </netsnmp>

template="opnsense"
name="opnsense"

iso="OPNsense-24.1-serial-amd64.img"

install()
{
  if [ ! -e "/vm/.iso/$iso" ]; then
    sudo vm iso $HOME/Downloads/$iso
  fi

  cat - << EOF > _tmp.conf
loader="bhyveload"
cpu=2
memory=2048M
network0_type="virtio-net"
network0_switch="br0"
disk0_type="virtio-blk"
disk0_name="disk0.img"
EOF

  sudo cp -f _tmp.conf /vm/.templates/${template}.conf

  sudo vm create -t ${template} -s g -m 2048m -c 2 ${name}
  sudo vm install ${name} ${iso}

  sleep 3
  sudo vm console ${name}
}

hosts()
{
  ansible-inventory -i template.yml --yaml --list --output hosts.yml
}

default()
{
  tag=$1
  ansible-playbook -i hosts.yml -t ${tag} site.yml
}

if [ $# -eq 0 ]; then
  all
fi

for target in "$@"; do
  LANG=C type "$target" 2>&1 | grep 'function' > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    $target
  else
    default $target
  fi
done


