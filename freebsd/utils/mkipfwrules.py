#!/usr/bin/env python3

import re

template = 'ipfw-workstation.txt'
fp = open(template, mode='r', encoding='utf-8')

print('#!/bin/sh')
print('')
print('ipfw -q -f flush')
print('')
#ipfw -q add 100 allow tcp from any to any 22 in

rules = [
    '10000 allow tcp from any to any 22 in'
]

while True:
    line = fp.readline()
    if not line:
        break

    line = re.sub(r'\r?\n?$', '', line)

    print('ipfw -q add {0}'.format(line))

print('')

for rule in rules:
    print('ipfw -q add {0}'.format(rule))

fp.close()

