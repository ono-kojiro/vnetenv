#!/bin/sh

bridges="br40 br50 br60 br70 br80"

create()
{
  for bridge in $bridges; do
    sudo vm switch create -t standard $bridge
  done
}

destroy()
{
  for bridge in $bridges; do
    sudo vm switch destroy $bridge
  done
}

create

