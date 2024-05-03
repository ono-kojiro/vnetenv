#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

template="rocky"
name="rocky31"
iso="Rocky-9.3-x86_64-minimal.iso"

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
cpu=2
memory=1024M
network0_type="virtio-net"
network0_switch="sw31"
disk0_type="virtio-blk"
disk0_name="disk0.img"
grub_install0="linux /isolinux/vmlinuz"
grub_install1="initrd /isolinux/initrd.img"
grub_install2="boot"
grub_run_partition="msdos1"
grub_run_dir="/grub2"
EOF

#grub_install0="linux /isolinux/vmlinuz LANG=ja_JP.UTF-8 KEYTABLE=jp SYSFONT=latarcyrheb-sun16 console=ttyS0"
#grub_install1="initrd /isolinux/initrd.img"

  sudo cp -f _tmp.conf /vm/.templates/${template}.conf
  sudo vm create -t ${template} -s 16g -m 1024m -c 2 ${name}
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


