#!/usr/bin/env python


from subprocess import call
import sys, os, re


out = "/root/.msf4/loot/usernames.txt"


def looted_user():
    cmd = (
        "cat /root/.msf4/loot/ssh_login.txt | "
        "awk '{ print $3 }' | "
        "grep / | "
        "awk '{print substr($0,7)}' | "
        "awk -F/ '{print $1}' | grep -v .ssh | "
        "sort -u > /root/.msf4/loot/usernames.txt"
    )
    os.system(cmd)

def clarify():
    with open(out, 'r') as fin:
        data = fin.read().splitlines(True)
        with open(out, 'w') as fout:
            fout.writelines(data[3:])

def root():
    with open(out, "a") as shit:
        shit.write("root")
        shit.write("")


__all__ = ['looted_user', 'clarify', 'root']
