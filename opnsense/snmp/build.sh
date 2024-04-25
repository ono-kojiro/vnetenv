#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

remote="192.168.0.84"

addrs="192.168.40.1 192.168.50.1 192.168.60.1"

all()
{
  snmp
  json
  analysis
  dot
  png
  svg
}

snmp()
{
  mkdir -p log
  for addr in $addrs; do
    logfile="$addr.log"
    ssh $remote snmpwalk -v 2c -c public -OX $addr . > $logfile
  done
}

json()
{
  for addr in $addrs; do
    logfile="$addr.log"
	jsonfile="$addr.json"
	python3 oid2dict.py $logfile > $jsonfile
  done
}

analysis()
{
  for addr in $addrs; do
	jsonfile="$addr.json"
	ymlfile="$addr.yml"
    python3 parse.py -o $ymlfile $jsonfile
  done
}

prepare()
{
  url_base="https://www.cisco.com/content/dam/en_us/about/ac50/ac47"
  zips="doc_jpg 3015_jpeg"

  for name in $zips; do
    url="${url_base}/${name}.zip"
	if [ ! -e "${name}.zip" ]; then
	  curl -L -O -C - ${url}
    else
	  echo skip ${name}.zip
	fi
  done

  for name in $zips; do
	mkdir -p orig/${name}
	unzip -n -d orig/${name} ${name}.zip

    mkdir -p icons/${name}
	python3 jpeg2png.py -o icons/${name} orig/${name}
  done
}

dot()
{
  python3 yml2dot.py -o mygraph.dot \
    192.168.40.1.yml \
    192.168.50.1.yml \
    192.168.60.1.yml
  cat mygraph.dot
}

png()
{
  command dot -Tpng -o mygraph.png mygraph.dot
}

svg()
{
  command dot -Tsvg -o mygraph.svg mygraph.dot
}


clean()
{
  for addr in $addrs; do
    logfile="$addr.log"
	jsonfile="$addr.json"
	ymlfile="$addr.yml"
    rm -f $logfile $jsonfile $ymlfile
  done

  rm -f mygraph.dot mygraph.png
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


