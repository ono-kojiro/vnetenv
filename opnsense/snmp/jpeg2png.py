#!/usr/bin/env python3

import os
import sys
import re

import getopt

import json

from datetime import datetime
import dateutil.parser

from pprint import pprint

import sys
import os
import re

import glob
import subprocess
import shlex

def usage():
    print("Usage : {0} [-o output-dir] input-dir1 input-dir2 ...".format(sys.argv[0]))

def main():
    ret = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:",
            [
                "help",
                "version",
                "output=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output_dir = None
    
    for o, a in opts:
        if o == "-v":
            usage()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output-dir"):
            output_dir = a
        else:
            assert False, "unknown option"

    if output_dir is None :
        print('no output-dir option')
        ret += 1

    if ret != 0:
        sys.exit(1)

    for input_dir in args:
        items = glob.glob('{0}/*.jpg'.format(input_dir))

        for item in items:
            infile = item
            filename = os.path.basename(infile)
            basename = os.path.splitext(filename)[0]

            basename = re.sub(r' ', '_', basename)
            outfile = '{0}/{1}.png'.format(output_dir, basename)


            cmd = 'convert "{0}" "{1}"'.format(infile, outfile)
            print(cmd)
            subprocess.call(shlex.split(cmd))

    
if __name__ == "__main__":
    main()

