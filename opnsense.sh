#!/bin/sh

sudo vm iso OPNsense-24.1-serial-amd64.img

cat - << EOF > _tmp.conf
loader="bhyveload"
cpu=2
memory=2048M
network0_type="virtio-net"
network0_switch="br40"
network1_type="virtio-net"
network1_switch="public"
disk0_type="virtio-blk"
disk0_name="disk0"
disk0_dev="sparse-zvol"
EOF

sudo cp -f _tmp.conf /vm/.templates/opnsense.conf

sudo vm create -t opnsense -s 16g -m 2048m -c 2 opnsense40
sudo vm install opnsense40 OPNsense-24.1-serial-amd64.img

