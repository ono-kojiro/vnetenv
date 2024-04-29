#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

remote="192.168.0.84"
addrs="192.168.10.1 192.168.20.1 192.168.30.1"

database="database.db"
sqlfile="database.sql"


help()
{
  cat - << EOF
usage: sh build.sh <target>

target:
  snmp
  json
  analysis
  dot
  png
  svg
EOF
}

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
	cmd="python3 oid2dict.py -o $jsonfile $logfile"
    echo $cmd
    $cmd
  done
}

analysis()
{
  for addr in $addrs; do
	jsonfile="$addr.json"
	ymlfile="$addr.yml"
    cmd="python3 parse.py -o $ymlfile $jsonfile"
    echo $cmd
    $cmd
  done
}

db()
{
  jsonfiles=""
  for addr in $addrs; do
	jsonfiles="${jsonfiles} $addr.json"
  done

  rm -f ${database}

  cmd="python3 json2db.py -o ${database} ${jsonfiles}"
  echo $cmd
  $cmd
  sqlite3 ${database} ".dump" > ${sqlfile}
  cat ${sqlfile}
}

test()
{
  echo "INFO: agent_view"
  sqlite3 ${database} "select * from agent_view;"

  echo "INFO: host_view"
  sqlite3 ${database} "select * from host_view;"
  
  echo "INFO: conn_view"
  sqlite3 ${database} "select * from conn_view;"
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
  ymlfiles=""
  for addr in $addrs; do
    ymlfiles="$ymlfiles ${addr}.yml"
  done
  
  cmd="python3 yml2dot.py -o mygraph.dot $ymlfiles"
  echo $cmd
  $cmd
  #cat mygraph.dot
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


