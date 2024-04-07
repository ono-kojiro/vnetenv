#!/bin/sh

cat - << EOF > _tmp.conf
loader="grub"
cpu=2
memory=1024M
network0_type="virtio-net"
network0_switch="br50"
disk0_type="virtio-blk"
disk0_name="disk0.img"
grub_run_partition="2"
EOF

sudo cp -f _tmp.conf /vm/.templates/ubuntu.conf
sudo vm create -t ubuntu -s 16g -m 2048m -c 2 ubuntu50
sudo vm install ubuntu50 ubuntu-22.04.4-live-server-amd64.iso

