1. INSTALL

Install without network configuration

  network0_type="e1000"
  network0_switch="xxx"
  disk0_type="ahci-hd"
  disk0_name="disk0.img"

After installation, shutdown.

2. MOUNT ISO

Copy virtio iso file to vm directory.
Edit config and add "ahci-cd" disk

  disk1_type="ahci-cd"
  disk1_name="virtio-win-0.1.117.iso"

3. START VM

Start vm and install virtio driver
After installing virtio driver, shutdown.

4. CHANGE NETWORK TYPE AND UNMOUNT ISO

  network0_type="virtio-net"
  network0_switch="xxx"

  #disk1_type="ahci-cd"
  #disk1_name="virtio-win-0.1.117.iso"

