#!/bin/bash

running_kver=$(uname -r) 
if [[ -d "/lib/modules/${running_kver}/build" ]]; then
  # Running kernel's sources are available
  kvers=${running_kver}
else
  # Let's use newest installed version of kernel-devel
  kvers=$(rpm -q kernel-devel --queryformat="%{buildtime}\t%{name}-%{version}-%{release}-%{arch}\n" | sort -nr | head -1 | cut -f2)
fi

echo ${kvers}

