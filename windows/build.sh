#!/bin/sh

name="windows10"

iso_path="$HOME/Downloads/Win10-22H2_Japanese_x64.iso"
iso=`basename $iso_path`
if [ ! -e "/vm/.iso/$iso" ]; then
  sudo vm iso $iso_path
fi

install()
{
  cat - << EOF > _tmp.conf
loader="uefi"
graphics="yes"
graphics_wait="yes"
xhci_mouse="yes"
cpu=2
memory=4G

# put up to 8 disks on a single ahci controller.
# without this, adding a disk pushes the following network devices onto higher slot numbers,
# which causes windows to see them as a new interface
ahci_device_limit="8"

# ideally this should be changed to virtio-net and drivers installed in the guest
# e1000 works out-of-the-box
network0_type="e1000"
network0_switch="public"
disk0_type="ahci-hd"
disk0_name="disk0.img"

# windows expects the host to expose localtime by default, not UTC
utctime="no"
EOF

  sudo cp -f _tmp.conf /vm/.templates/windows.conf
  sudo vm create -t windows -s 32g -m 4g -c 2 $name
  sudo vm install $name $iso
}

stop()
{
  sudo vm stop $name
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

