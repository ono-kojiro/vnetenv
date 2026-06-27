#!/bin/sh

echo "1..2"

ssh -F ../ssh_config server bash -s << EOF
{
  echo "[SERVER]"
  cd /tmp/
  rm -f /tmp/nc.log
  nohup nc -k -l 9999 >/tmp/nc.log 2>&1 &
  echo "nc started"
}
EOF

server="172.16.0.42"
port="9999"

ssh -F ../ssh_config client bash -s << EOF
{
  echo "[CLIENT]"
  nc -zv -w 1 ${server} ${port}
  res="\$?"
  if [ "\$res" -eq 0 ]; then
    echo "ok - nc -zv"
  else
    echo "not ok - nc -zv"
  fi
}
EOF

ssh -F ../ssh_config server bash -s << EOF
{
  echo "[SERVER]"
  pkill nc
  if [ "$?" -eq 0 ]; then
    echo "ok - pkill nc"
  else
    echo "not ok - pkill nc"
  fi
}
EOF

