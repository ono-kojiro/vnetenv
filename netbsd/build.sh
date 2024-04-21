#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

template="netbsd"
name="netbsd"
iso="NetBSD-10.0-amd64.iso"

segs="40 50 60"

name=netbsd

all()
{
  help
}

help()
{
  cat - << EOF
usage : $0 target1 target2 ...

    target
      install
EOF
}

install()
{
  if [ ! -e "/vm/.iso/$iso" ]; then
    sudo vm iso $HOME/Downloads/$iso
  fi

  cat - << EOF > _tmp.conf
loader="grub"
cpu=1
memory=256M
network0_type="virtio-net"
network0_switch="br0"
disk0_type="virtio-blk"
disk0_name="netbsd.img"
grub_install0="knetbsd -h -r cd0a /netbsd"
grub_run0="knetbsd -h -r dk0 /netbsd"
EOF

  sudo cp -f _tmp.conf /vm/.templates/${template}.conf
  sudo vm create -t ${template} -s 4g -m 128m -c 2 ${name}
  sudo vm install ${name} ${iso}

  sleep 3

  sudo vm console ${name}
}

hosts()
{
  ansible-inventory -i template.yml --yaml --list --output hosts.yml
}

prepare()
{
  ssh netbsd pkgin install python311
}

default()
{
  tag=$1
  ansible-playbook -i hosts.yml -t ${tag} site.yml
}

clone()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    sudo vm clone ${name} ${vmname}
	config="/vm/${vmname}/${vmname}.conf"
	sudo sed -i '' -e "s/\"br0\"/\"br${seg}\"/" $config
  done
}

unclone()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    sudo vm destroy -f ${vmname}
  done
}

startall()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    sudo vm start ${vmname}
  done
}

stopall()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    sudo vm stop ${vmname}
  done
}

enableall()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    line=`cat /etc/rc.conf | grep vm_list | grep -v "^#"`
	value=`echo "$line" | awk -F'=' '{ print $2 }' | tr -d '"'`
	
	# add spaces and check
	echo "' $value '" | grep " $vmname "
	if [ $? -ne 0 ]; then
      new_value="$value $vmname"
	  echo "INFO: enable $vmname"
	  sudo sysrc vm_list="$new_value"
	else
	  echo "INFO: $vmname is already enabled"
	fi
  done
}

disableall()
{
  for seg in $segs; do
	vmname="${name}${seg}"
    line=`cat /etc/rc.conf | grep vm_list | grep -v "^#"`
	value=`echo "$line" | awk -F'=' '{ print $2 }' | tr -d '"'`
	
	# add spaces and check
	echo "' $value '" | grep " $vmname "
	if [ $? -eq 0 ]; then
	  # remove vmname
	  new_value=`echo " $value " | sed -e "s/ $vmname / /" | tr -s " "`
	  new_value=`echo $new_value | sed -e "s/^[ ]*//" | sed -e "s/[ ]*$//"`
	  echo "INFO: disable $vmname"
	  sudo sysrc vm_list="$new_value"
	else
	  echo "INFO: $vmname is already disabled"
	fi
  done
}


hosts

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


