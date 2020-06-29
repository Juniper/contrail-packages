#!/bin/bash

my_file="$(readlink -e "$0")"
my_dir="$(dirname $my_file)"

source /etc/os-release
KERNEL_REPOSITORIES_RHEL8=${KERNEL_REPOSITORIES_RHEL8:-"--disablerepo=* --enablerepo=BaseOS"}
kvers=$($my_dir/get_kvers.sh)

for kver in $kvers; do
    k_mmp_ver=$(echo "$kver" | awk -F '-' '{print $1}')
    packages=$(cat $my_dir/../kernel_dependencies.info | grep ^$k_mmp_ver | awk -F ":" '{print $2}')
    if [[ "$ID" == "rhel" && "$k_mmp_ver" == "4.18.0" ]]; then
        extra_repos="${KERNEL_REPOSITORIES_RHEL8}"
    else
        extra_repos=''
    fi
    for package in $packages; do
        if ! rpm -q ${package}-${kver} 2>&1 > /dev/null ; then
            sudo rpm -ivh --nodeps --noscripts $(repoquery $extra_repos --location ${package}-${kver})
        fi
    done
done
