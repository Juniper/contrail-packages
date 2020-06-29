#!/bin/bash

my_file="$(readlink -e "$0")"
my_dir="$(dirname $my_file)"


if [[ "${MULTI_KERNEL_BUILD,,}" == 'true' ]]; then
    if [[ "${LINUX_DISTR}" =~ 'ubi' ]] ; then
        os_suffix='.ubi'
    else
        source /etc/os-release
        [[ "$ID" == 'rhel' ]] && os_suffix=".rhel"
    fi
    kvers=$(cat $my_dir/../kernel_version${os_suffix}.info | sed '/^#/d')
else
    running_kver=$(uname -r)
    if [[ -d "/lib/modules/${running_kver}/build" ]]; then
        # Running kernel's sources are available
        kvers=${running_kver}
    else
        # Let's use newest installed version of kernel-devel
        kvers=$(rpm -q kernel-devel --queryformat="%{buildtime}\t%{VERSION}-%{RELEASE}.%{ARCH}\n" | sort -nr | head -1 | cut -f2)
    fi
fi

echo ${kvers}
