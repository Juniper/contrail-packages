%define     _contrailetc  /etc/contrail
%define     _distropkgdir %{_sbtop}tools/packages/rpm/%{name}

%if 0%{?_buildTag:1}
%define     _relstr %{_buildTag}
%else
%define     _relstr %(date -u +%y%m%d%H%M)
%endif

%if 0%{?_srcVer:1}
%define     _verstr %{_srcVer}
%else
%define     _verstr 1
%endif

%if 0%{?_opt:1}
%define         _sconsOpt      %{_opt}
%else
%define         _sconsOpt      debug
%endif

%if 0%{?_kVers:1}
%define         _kvers      %{_kVers}
%else
%define         _kvers      3.10.0-327.10.1.el7.x86_64
%endif

%if 0%{?_enableMellanox:1}
%define         _enableMlx %{_enableMellanox}
%else
%define         _enableMlx FALSE
%endif

%define         _kernel_dir /lib/modules/%{_kVers}/build


%bcond_without debuginfo

Name:       contrail-vrouter-dpdk
Version:    %{_verstr}
Release:    %{_relstr}%{?dist}
Summary:    Contrail vrouter DPDK %{?_gitVer}

Group:      Applications/System
License:    Commercial
URL:        http://www.juniper.net/
Vendor:     Juniper Networks Inc

BuildRequires: boost-devel
BuildRequires: liburcu-devel
# kernel is required for /lib/modules content
%if 0%{?rhel}
BuildRequires: kernel = 3.10.0-957.21.3.el7
BuildRequires: kernel-devel = 3.10.0-957.21.3.el7
%else
BuildRequires: kernel = 3.10.0-957.27.2.el7
BuildRequires: kernel-devel = 3.10.0-957.27.2.el7
%endif
BuildRequires: numactl-devel
BuildRequires: libnl3-devel
BuildRequires: scons
BuildRequires: gcc
BuildRequires: flex
BuildRequires: bison
BuildRequires: gcc-c++
BuildRequires: libpcap
BuildRequires: libpcap-devel
%if 0%{?centos}
BuildRequires: python2-pip
%endif
Requires: liburcu2
Requires: userspace-rcu = 0.10.0-1.el7
Requires: libnl3
Requires: numactl-libs
Requires: contrail-vrouter-utils >= %{_verstr}-%{_relstr}
%if %{_enableMlx} == "TRUE"
BuildRequires: rdma-core-devel = 45mlnx1-1.45101
Requires: rdma-core = 45mlnx1-1.45101
Requires: libibverbs = 45mlnx1-1.45101
%define         _sconsAddOpts      enableMellanox
%else
%define         _sconsAddOpts      none
%endif


%description
Provides contrail-vrouter-dpdk binary

%if %{with debuginfo}
%debug_package
%endif

%prep
# Cleanup
pushd %{_sbtop}
RTE_KERNELDIR=%{_kernel_dir} scons -c \
    --opt=%{_sconsOpt} \
    --kernel-dir=%{_kernel_dir} \
    --root=%{_builddir} \
    --add-opts=%{_sconsAddOpts} \
    vrouter/dpdk
popd

%build
pushd %{_sbtop}
RTE_KERNELDIR=%{_kernel_dir} scons \
    --opt=%{_sconsOpt} \
    --kernel-dir=%{_kernel_dir} \
    --root=%{_builddir} \
    --add-opts=%{_sconsAddOpts} \
    vrouter/dpdk
popd

%install
# Install Directories
install -d -m 755 %{buildroot}/%{_bindir}
install -p -m 755 %{_sbtop}/build/%{_sconsOpt}/vrouter/dpdk/contrail-vrouter-dpdk %{buildroot}/%{_bindir}/contrail-vrouter-dpdk

%files
%defattr(-,root,root,-)
%{_bindir}/contrail-vrouter-dpdk


%changelog
* Thu Feb 16 2017 Nagendra Maynattamai <npchandran@juniper.net> 4.1.1-2.1contrail1
- Initial Build. Rebuilt with patches for Opencontrail
