#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
cd $top_dir

hosts()
{
  ansible-inventory -i template.yml --list --yaml > hosts.yml
}

help()
{
  echo "usage : $0 [options] target1 target2 ..."
cat - << EOS
  target:
    deploy
EOS
}

all()
{
  deploy
}

default()
{
  arg=$1
  ansible-playbook -K -i hosts.yml ${arg}.yml
}


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
    * )
      args="$args $1"
      ;;
  esac
  
  shift
done

# generate hosts.yml
hosts

if [ -z "$args" ]; then
  help
fi

for arg in $args; do
  LANG=C type $arg 2>&1 | grep 'function' > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    $arg
  else
    default $arg
  fi
done

