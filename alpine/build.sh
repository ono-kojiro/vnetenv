#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir
  
template="alpine"
name="alpine"

iso="alpine-virt-3.19.1-x86_64.iso"

segs="40 50 60"

all()
{
  help
}

help()
{
  cat - << EOF
usage : $0 target1 target2 ...

target
  prepare
  
  ldap
  doas
EOF
}

install()
{
  if [ ! -e "/vm/.iso/$iso" ]; then
    sudo vm iso $HOME/Downloads/$iso
  fi

  cat - << EOF > _tmp.conf
loader="uefi"
cpu=1
memory=256M
network0_type="virtio-net"
network0_switch="br0"
disk0_type="virtio-blk"
disk0_name="disk0.img"
grub_install0="linux /boot/vmlinuz-virt initrd=/boot/initramfs-virt alpine_dev=cdrom:iso9660 modules=loop,squashfs,sd-mod,usb-storage,sr-mod"
grub_install1="initrd /boot/initramfs-virt"
grub_run0="linux /boot/vmlinuz-virt root=/dev/vda3 modules=ext4"
grub_run1="initrd /boot/initramfs-virt"
EOF

  sudo cp -f _tmp.conf /vm/.templates/${template}.conf
  sudo vm create -t ${template} -s 4g -m 256m -c 2 ${name}
  sudo vm install ${name} ${iso}

  sleep 3

  sudo vm console ${name}
}

prepare()
{
  ssh alpine apk add python3
}

hosts()
{
  ansible-inventory -i template.yml --yaml --list --output hosts.yml
}

default()
{
  tag=$1
  cmd="ansible-playbook ${ansible_opts} -i hosts.yml -t ${tag} site.yml"
  echo $cmd
  $cmd
}

clone()
{
  for seg in $segs; do
	name="alpine${seg}"
    sudo vm clone alpine ${name}
	config="/vm/${name}/${name}.conf"
	sudo sed -i '' -e "s/\"br0\"/\"br${seg}\"/" $config
  done
}

unclone()
{
  for seg in $segs; do
    sudo vm destroy -f alpine${seg}
  done
}

startall()
{
  for seg in $segs; do
    sudo vm start alpine${seg}
  done
}

stopall()
{
  for seg in $segs; do
    sudo vm stop alpine${seg}
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

while [ $# -ne 0 ]; do
  case "$1" in
    -h | --help)
      help
      exit 1
      ;;
    -o | --output)
      shift
      output=$1
      ;;
    -p | --playbook)
      shift
      playbook=$1
      ;;
    *)
      break
      ;;
  esac

  shift
done

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

