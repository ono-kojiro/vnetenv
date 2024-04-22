#!/usr/bin/python

import sys

import getopt
import json

from pprint import pprint
from jsonpath_ng import jsonpath, parse

def usage():
  print("Usage : {0}".format(sys.argv[0]))
        
def read_json(filepath):
  fp_in = open(filepath, mode='r', encoding='utf-8')
  data = json.load(fp_in)
  fp_in.close()
  return data

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
    
    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else:
        fp = sys.stdout
    
    if ret != 0:
        sys.exit(1)
    
    records = {}

    exprs = [
        parse('$..ifName'),
        parse('$..ifPhysAddress'),
        parse('$..ipNetToPhysicalPhysAddress'),
    ]

    keywords = [
        'ifName',
        'ifPhysAddress',
        'ipNetToPhysicalPhysAddress',
    ]

    for filepath in args:
        data = read_json(filepath)
        
        for keyword in keywords :
            expr = parse('$..' + keyword)

            for m in expr.find(data):
                records[keyword] = m.value

    fp.write(
        json.dumps(
            records,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    fp.write('\n')
    
    if output is not None :
        fp.close()
    
if __name__ == "__main__":
    main()
