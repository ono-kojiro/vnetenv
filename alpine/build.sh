#!/bin/sh

top_dir="$(cd "$(dirname "$0")" > /dev/null 2>&1 && pwd)"
cd $top_dir

name=alpine
disk=`pwd`/${name}.qcow2
iso="$HOME/Downloads/OS/alpine-virt-3.18.4-x86_64.iso"
#iso="$HOME/Downloads/OS/alpine-extended-3.18.4-x86_64.iso"

all()
{
  help
}

help()
{
  cat - << EOF
usage : $0 target1 target2 ...

target
  prepare
  
  ldap
  doas
EOF
}

prepare()
{
  ssh alpine apk add python3
}

hosts()
{
  ansible-inventory -i template.yml --yaml --list --output hosts.yml
}

default()
{
  tag=$1
  cmd="ansible-playbook ${ansible_opts} -i hosts.yml -t ${tag} site.yml"
  echo $cmd
  $cmd
}

clone()
{
  segs="40 50 60"
  for seg in $segs; do
	name="alpine${seg}"
    sudo vm clone alpine ${name}
	config="/vm/${name}/${name}.conf"
	sudo sed -i '' -e "s/\"br0\"/\"br${seg}\"/" $config
  done
}

unclone()
{
  segs="40 50 60"
  for seg in $segs; do
    sudo vm destroy -f alpine${seg}
  done
}



hosts

while [ $# -ne 0 ]; do
  case "$1" in
    -h | --help)
      help
      exit 1
      ;;
    -o | --output)
      shift
      output=$1
      ;;
    -p | --playbook)
      shift
      playbook=$1
      ;;
    *)
      break
      ;;
  esac

  shift
done

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

