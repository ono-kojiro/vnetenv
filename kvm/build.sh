#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
cd $top_dir

flags=""

bridges="wan lan1 lan2 lan3"

help()
{
  usage
}

usage()
{
  cat << EOS
usage : $0 [options] target1 target2 ...
EOS

}

all()
{
  deploy
}

hosts()
{
  ansible-inventory -i template.yml --list --yaml > hosts.yml
}

prepare()
{
  sudo dnf -y install ansible-core
}

clean()
{
  ansible-playbook -i hosts.yml clean.yml
}

deploy()
{
  ansible-playbook $flags -i hosts.yml site.yml
}

create_bridge()
{
  for item in $bridges; do
    sudo nmcli con add type bridge \
      ifname $item \
      conn.id $item \
      ipv4.method disabled \
      ipv6.method disabled
  done
}

delete_bridge()
{
  for item in $bridges; do
    sudo nmcli con del $item
  done
}

default()
{
  tag=$1
  ansible-playbook $flags -i hosts.yml -t $tag site.yml
}

hosts

args=""
while [ $# -ne 0 ]; do
  case $1 in
    -h )
      usage
      exit 1
      ;;
    -v )
      verbose=1
      ;;
	-* )
	  flags="$flags $1"
	  ;;
    * )
      args="$args $1"
      ;;
  esac
  
  shift
done

if [ -z "$args" ]; then
  help
  exit 1
fi

for arg in $args; do
  num=`LANG=C type $arg | grep 'function' | wc -l`
  if [ $num -ne 0 ]; then
    $arg
  else
    #echo "ERROR : $arg is not shell function"
    #exit 1
    default $arg
  fi
done

