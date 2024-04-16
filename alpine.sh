#!/bin/sh

template="alpine"
name="alpine0"

iso="alpine-virt-3.19.1-x86_64.iso"

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

