#!/usr/bin/python3
import subprocess
import sys
import re
import os

import args_parser
parser = args_parser.get_parser()
args = parser.parse_args()
#print(args)

is_debug = False


def debug(s):
    if is_debug or args.debug:
      print("[DEBUG] %s" % (s))

def info(s):
    if is_debug or args.debug:
      print("[INFO] %s" % (s))

def warn(s):
    if is_debug or args.debug:
      print("[WARN] %s" % (s))


#====================================================================

import pkgname_analyzer

def remove_expiration_msg(s):
    #debug("s: " + str(s))
    l_s = s.split(sep="\n")
    #debug("before remove msg: " + ",".join(l_r4))
    for n in range(0, len(l_s)):
        #debug("n: " + str(n))
        if l_s[n].startswith("Last metadata expiration check"):
            l_s.remove(l_s[n])
            break
    return l_s

def swap_based_on_prefix(l, prefix):
    for n in range( 1, len(l) ):
        debug("current: " + l[n])
        if l[n].startswith(prefix):
            debug("[Prefix] FOUND element to swap! index: " + str(n))
            l[0], l[n] = l[n], l[0]
            break
    return l 

def swap_based_on_pkgname_and_following_digits(l, pkgname):
    for n in range( 1, len(l) ):
        debug("current: [" + str(n) + "], " + l[n])
        debug("char (is digit?): " + l[n][len(pkgname)+1])
        if l[n].startswith(pkgname) and l[n][len(pkgname)+1].isdigit():
            debug("[RUNTIME] [EXACT_NAME_MATCH] FOUND element to swap! index: " + str(n))
            l[0], l[n] = l[n], l[0]
            break
    return l

# Get full pkg name by "rpm -qa"
def get_full_pkgname_rpm_qa(partial_name, match):
    cmd = "rpm -qa | grep \"" + partial_name + "\""
    debug("[CMD] " + cmd)
    r = subprocess.getoutput(cmd)

    # rpm -qa result (multiple packages) into one list
    l_pkgs = r.split(sep="\n")
    debug("[CMD] [Return] " + " / ".join(l_pkgs))

    if l_pkgs[0] == "" or len(l_pkgs) == 0:
        return None

    # Move matching pkgname to the first index
    debug("[CMD] [Return] length: " + str(len(l_pkgs)))
    #l_pkgs = swap_based_on_prefix(l_pkgs, filter_prefix)
    l_pkgs = swap_based_on_pkgname_and_following_digits(l_pkgs, match)
    debug(l_pkgs)

    return l_pkgs[0]

# Get list of runtime dependencies
def get_runtime_deps(pkgname):
    cmd_repoquery = "repoquery --requires " + pkgname
    debug("[CMD] " + cmd_repoquery)
    r = subprocess.getoutput(cmd_repoquery)
    l_r = remove_expiration_msg(r)
    info("[Dependencies] " + ", ".join(l_r))
    return l_r

def get_3rd_party_runtime_deps(pkgname, filter_prefix):
    l_deps = get_runtime_deps(pkgname)
    l_deps_no_dup = set()
    for n in range(0, len(l_deps)):
        debug("current: " + l_deps[n])

        # Skip Case 1: Native Python
        #              ex: python(abi) = 3.9
        if l_deps[n].startswith("python("):
            info("[SKIPPING] " + l_deps[n])
            continue

        # Skip Case 2: Doesn' have matching filter_prefix
        #          ex: ld-linux-aarch64.so.1()(64bit), 
        #              ld-linux-aarch64.so.1(GLIBC_2.17)(64bit), 
        #              libc.so.6(GLIBC_2.17)(64bit), 
        #              libc.so.6(GLIBC_2.4)(64bit), 
        #              libpthread.so.0()(64bit), 
        #              rtld(GNU_HASH)
        #       match: python39-django >= 2.2
        #if l_deps[n].find(" ") < 0:
        if l_deps[n].find( filter_prefix[ :len(filter_prefix) - 1 ] ) < 0:
            info("[SKIPPING] " + l_deps[n])
            continue

        # Get dependency short package name
        if " " in l_deps[n]:
            # Case: python39-future >= 0.14.0
            dep_short_pkgname = l_deps[n][:l_deps[n].find(" ")]
        else:
            # Case: python39-setuptools
            dep_short_pkgname = l_deps[n]
        l_deps_no_dup.add(dep_short_pkgname)
    return l_deps_no_dup

def main():
    input_pkg = args.package
    if args.prefix:
        prefix = args.prefix
        prefix = prefix + "-" if prefix[-1] != "-" else prefix
    else:
        prefix = ""
    if args.filter:
        filter_prefix = args.filter
        filter_prefix = filter_prefix + "-" if filter_prefix[-1] != "-" else filter_prefix
    else:
        filter_prefix = ""

    # Construct THIRD_PARTY_LICENSE file
    # header
    thirdparty_output = subprocess.getoutput("cat " + os.path.dirname(__file__) + "/THIRD_PARTY_LICENSES_HEADER")

    # Remove prefix if found
    debug("search string: " + args.package)
    input_pkg = input_pkg[len(prefix):] if prefix and input_pkg.startswith(prefix) else input_pkg

    # Get full rpm name
    full_pkgname = get_full_pkgname_rpm_qa(partial_name=input_pkg, match=filter_prefix+input_pkg)
    info("[Found Package To Process] " + full_pkgname)
    if not full_pkgname:
        warn("no packages found: " + args.package)
        exit(0)

    # Get pkgname without version
    pkgname = pkgname_analyzer.analyze_pkgname(full_pkgname, "name")

    # Get runtime deps
    l_deps_no_dup = get_3rd_party_runtime_deps(pkgname, filter_prefix)

    # Convert Runtime Dependencies into 3rd party licenses
    info("[Final Dependency List To Process] " + ", ".join(l_deps_no_dup))
    for n,val in enumerate(l_deps_no_dup):
        dep_full_pkgname = get_full_pkgname_rpm_qa(partial_name=val, match=val)
        if not dep_full_pkgname:
            warn("no packages found for dependency name: " + dep_short_pkgname)
            exit(0)

        # 
        thirdparty_title = pkgname_analyzer.analyze_pkgname(dep_full_pkgname, "name")
        thirdparty_version = pkgname_analyzer.analyze_pkgname(dep_full_pkgname, "version")

        # Get 3rd party license string
        cmd_dnf_info = "dnf info " + thirdparty_title
        r5 = subprocess.getoutput(cmd_dnf_info)
        l_r5 = r5.split(sep="\n")
        for n in range(0, len(l_r5)):
            if l_r5[n].startswith("License"):
                thirdparty_license = l_r5[n].split(sep=":")[1].strip()
                break

        # Compose 3rd party title
        thirdparty_full_title = prefix[:len(prefix)-1] + " " + thirdparty_title.replace(filter_prefix, "") + " " + thirdparty_version.split(sep="-")[0] + " (" + thirdparty_license + ")"
        thirdparty_full_tltle_bar = "-"*len(thirdparty_full_title)
        thirdparty_output += "\n"
        thirdparty_output += thirdparty_full_tltle_bar + "\n"
        thirdparty_output += thirdparty_full_title + "\n"
        thirdparty_output += thirdparty_full_tltle_bar + "\n"
        thirdparty_output += "\n\n"

        # Lookup licenses
        cmd_license_path = "repoquery --list " + thirdparty_title + " | grep LICENSE"
        r_license_path = subprocess.getoutput(cmd_license_path)
        l_license_path = remove_expiration_msg(r_license_path)
        if not l_license_path:
            print("[ERROR] " + thirdparty_title + " doesn't have a LICENSE file!")
            thirdparty_output += "(package installed missing license file)"
        else:
            license_path = l_license_path[0]
            thirdparty_output += subprocess.getoutput("cat " + license_path)

        #if re.search('BSD', thirdparty_license, re.IGNORECASE) and "3" in thirdparty_license:
        #    thirdparty_output += subprocess.getoutput("cat licenses/BSD-3-Clause.txt")
        #elif re.search('BSD', thirdparty_license, re.IGNORECASE) and "2" in thirdparty_license:
        #    thirdparty_output += subprocess.getoutput("cat licenses/BSD-2-Clause.txt")
        #elif re.search('BSD', thirdparty_license):
        #    thirdparty_output += subprocess.getoutput("cat licenses/BSD-3-Clause.txt")
        #elif re.search('Apache', thirdparty_license, re.IGNORECASE) and "2" in thirdparty_license:
        #    thirdparty_output += subprocess.getoutput("cat licenses/Apache-2.0.txt")
        #elif re.search('Apache', thirdparty_license, re.IGNORECASE):
        #    thirdparty_output += subprocess.getoutput("cat licenses/Apache-2.0.txt")
        #elif re.search('GPL', thirdparty_license, re.IGNORECASE) and "3" in thirdparty_license:
        #    thirdparty_output += subprocess.getoutput("cat licenses/GPL-3.0-or-later.txt")
        #elif re.search('GPL', thirdparty_license, re.IGNORECASE) and "2" in thirdparty_license:
        #    thirdparty_output += subprocess.getoutput("cat licenses/GPL-2.0.txt")
        #elif re.search('PSF', thirdparty_license, re.IGNORECASE):
        #    thirdparty_output += subprocess.getoutput("cat licenses/PSF-2.0_long.txt")
        #elif re.search('Python', thirdparty_license, re.IGNORECASE) and re.search('Style', thirdparty_license, re.IGNORECASE):
        #    thirdparty_output += subprocess.getoutput("cat licenses/Python-Style.txt")
        #elif re.search('MIT', thirdparty_license, re.IGNORECASE):
        #    thirdparty_output += subprocess.getoutput("cat licenses/MIT.txt")
        #else:
        #    thirdparty_output += "(MISSING 3RD PARTY LICENSE)"

        thirdparty_output += "\n\n"
        thirdparty_output += "="*80
        thirdparty_output += "\n"

    print(thirdparty_output)

if __name__ == "__main__":
    main()
