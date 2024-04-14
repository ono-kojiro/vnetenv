#!/bin/sh

template="netbsd"
name="netbsd0"

iso="NetBSD-10.0-amd64.iso"

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
sudo vm create -t ${template} -s 4g -m 1024m -c 2 ${name}
sudo vm install ${name} ${iso}

sleep 3

sudo vm console ${name}

