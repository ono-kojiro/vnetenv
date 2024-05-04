#!/usr/bin/python

import sys
import re

import getopt
import yaml

from pprint import pprint
import json

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def str2dict(data, oid, typ, val) :
    # ex. RFC1213-MIB::atIfIndex[2][1.192.168.1.254]
    #
    # tokens is ['RFC1213-MIB', 'atIfIndex', '2', '1.192.168.1.254', '']
    tokens = re.split(r'::|\]\[|\[|\]', oid)

    for token in tokens :
        if token == '' :
           continue

        if not token in data:
            # remove double quotes
            m = re.search(r'^"(.*)"$', token)
            if m :
                token = m.group(1)

            # create sub tree
            data[token] = {}

        # update the pointer
        data = data[token]

    # store the value
    data['typ'] = typ
    data['val'] = val

def parse(fp, data):
    while True:
        line = fp.readline()
        if not line:
            break

        # remove line code
        line = re.sub(r'\r?\n?$', '', line)

        #
        # ex. 'RFC1213-MIB::atIfIndex[2][1.192.168.1.254] = INTEGER: 2'
        #
        #   oid: RFC1213-MIB::atIfIndex[2][1.192.168.1.254]
        #   typ: INTEGER
        #   val: 2
        #
        oid = None
        val = None
        typ = None
        m = re.search(r'^(.+) = ((.+): )?(.+)?', line)
        if m :
            oid = m.group(1)
            typ = m.group(3)
            val = m.group(4)
        else :
            continue

        if val is None :
            val = ""

        # remove double quotes of val
        m = re.search(r'^"(.+)"$', val)
        if m :
            val = m.group(1)

        # store
        str2dict(data, oid, typ, val)


def main():
    ret = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:",
            [
                "help",
                "version",
                "output="
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    
    for o, a in opts:
        if o == "-v":
            usage()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unknown option"
    
    if output is not None:
        fp = open(output, mode="w", encoding="utf-8")
    else :
        fp = sys.stdout

    if ret != 0:
        sys.exit(1)
   
    data = {}

    count = 0
    for filepath in args:
        fp_in = open(filepath, mode="r", encoding="utf-8")
        parse(fp_in, data)
        fp_in.close()

    #yaml.dump(data,
    #    fp,
    #    allow_unicode=True,
    #    default_flow_style=False,
    #    sort_keys=True,
    #)

    fp.write(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )
    )

    fp.write('\n')

    if output is not None:
        fp.close()

if __name__ == "__main__":
    main()

