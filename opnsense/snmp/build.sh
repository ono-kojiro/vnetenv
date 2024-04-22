#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

addrs="192.168.40.1 192.168.50.1 192.168.60.1"

all()
{
  snmp
  json
  analysis
}

snmp()
{
  mkdir -p log
  for addr in $addrs; do
    logfile="$addr.log"
    snmpwalk -v 2c -c public -OX $addr . > $logfile

	jsonfile="$addr.json"
	python3 ../oid2dict.py $logfile > $jsonfile
  done
}

json()
{
  for addr in $addrs; do
    logfile="$addr.log"
	jsonfile="$addr.json"
	python3 ../oid2dict.py $logfile > $jsonfile
  done
}

analysis()
{
  python3 ../parse.py -o output.json \
    192.168.40.1.json \
	192.168.50.1.json \
	192.168.60.1.json
  cat output.json
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


