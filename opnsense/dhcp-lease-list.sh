#!/bin/sh

hosts="opnsense10 opnsense20 opnsense30"

{
  for host in $hosts; do
    ssh $host cat /var/dhcpd/var/db/dhcpd.leases
  done
} > addrs.log


