#!/usr/bin/env python
''' Pull List of contrail packages for each distribution and
    Sku from Pacakager's config files and create package list file
'''

import sys
import os
import platform
import argparse
from ConfigParser import SafeConfigParser

def parse_args(args):
    '''Parse CLI args and return the parser'''
    pkg_types = {'centos': 'rpm', 'redhat': 'rpm', 'fedora': 'rpm', 'ubuntu': 'deb'}
    parser = argparse.ArgumentParser(description='Package List file Generator')
    platform_dist = map(str.lower, platform.linux_distribution())
    parser.add_argument('-d', '--dist',
                        action='store',
                        dest='dist',
                        metavar='Distribution',
                        default="".join(platform_dist[0:2]).replace('.', '').replace(' ', ''),
                        help='Specify Distribution, eg: ubuntu, centos, fedora')
    parser.add_argument('-s', '--sku',
                        action='store',
                        dest='sku',
                        metavar='SKU',
                        required=True,
                        help='Specify SKU of the build')
    if len(args) == 0:
        print 'ERROR: No Arguments supplied. Please see Usage...'
        print '-' * 78, '\n'
        parser.print_help()
        sys.exit(2)
    ns, files = parser.parse_known_args(args)
    if len(files) == 0:
        pkg_os = filter(lambda pkg: ns.dist.startswith(pkg), pkg_types.keys())
        files = [os.path.abspath('%s_list.txt' % pkg_types[pkg_os[0]])]
    return ns, files[0]

def get_conf_file(sku, dist):
    '''Derive config file path from sku and dist'''
    cmd = 'repo info contrail-packages | grep "Mount path" | cut -f3 -d " "'
    repo_top_cmd = os.popen(cmd)
    repo_top = repo_top_cmd.read().strip('\n')
    conf_file = os.path.join(repo_top, 'rpm', 'contrail-setup', 'package_configs',
                             dist, sku, 'contrail_packages.cfg')
    if not os.path.isfile(conf_file):
        raise RuntimeError('Config file (%s) do not exists...' %conf_file)
    return conf_file

def get_pkg_list(config_file):
    '''Retrieve packages list from the config file and return a list of packages'''
    pkg_list = []
    parser = SafeConfigParser()
    read_files = parser.read(config_file)
    if config_file not in read_files:
        raise RuntimeError('Either Config file (%s) is not present or not in'\
                           ' valid format' %config_file)
    for section in parser.sections():
        pkginfo = dict(parser.items(section))
        pkgs = map(str.strip, pkginfo['pkgs'].split(','))
        pkg_list.extend(filter(None, pkgs))
    return pkg_list

def create_pkg_file(outfile, pkgs):
    '''Write a packges list file'''
    with open(outfile, 'w') as fid:
        fid.write('\n'.join(pkgs))
        fid.flush()
    print 'File (%s) has been created with packages list' %outfile

def main():
    '''High level function to call other functions'''
    cli, outfile = parse_args(sys.argv[1:])
    config_file = get_conf_file(cli.sku, cli.dist)
    pkgs = get_pkg_list(config_file)
    create_pkg_file(outfile, pkgs)

if __name__ == '__main__':
    main()
