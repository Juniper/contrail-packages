%define         _contrailetc /etc/contrail
%define         _contrailutils /opt/contrail/utils
%define         _distropkgdir tools/packaging/common/control_files
%define         _contraildns /etc/contrail/dns

%if 0%{?_kernel_dir:1}
%define         _osVer  %(cat %{_kernel_dir}/include/linux/utsrelease.h | cut -d'"' -f2)
%else
%define         _osVer       %(uname -r)
%endif
%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif

%{echo: "Building release %{_relstr}\n"}

Name:               contrail
Version:            %{_verstr}
Release:            %{_relstr}%{?dist}
Summary:            Contrail

Group:              Applications/System
License:            ASL 2.0
URL:                www.opencontrail.org
Vendor:             OpenContrail Project.

%description
Contrail package describes all sub packages that are required to
run open contrail.

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  systemd-units
BuildRequires:  gcc-c++
BuildRequires:  devtoolset-1.1-gcc
BuildRequires:  devtoolset-1.1-gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  libstdc++-devel
BuildRequires:  zlib-devel
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  libcurl
BuildRequires:  libtool
BuildRequires:  python-devel
BuildRequires:  python-lxml
BuildRequires:  python-setuptools
BuildRequires:  unzip
BuildRequires:  vim-common
BuildRequires:  protobuf
BuildRequires:  protobuf-compiler
BuildRequires:  protobuf-devel

%prep

%install
pushd %{_sbtop}
scons --root=%{buildroot} install
scons --kernel-dir=/lib/modules/%{_osVer}/build build-kmodule --root=%{buildroot}
mkdir -p %{buildroot}/_centos/tmp
popd
pushd %{buildroot}
mkdir -p %{buildroot}/centos
cp %{_sbtop}/%{_distropkgdir}/dkms.conf.in %{buildroot}/centos/
(cd usr/src/vrouter && tar zcf %{buildroot}/_centos/tmp/contrail-vrouter-%{_verstr}.tar.gz .)
sed "s/__VERSION__/"%{_verstr}"/g" centos/dkms.conf.in > usr/src/vrouter/dkms.conf
rm  centos/dkms.conf.in
install -d -m 755 %{buildroot}/usr/src/modules/contrail-vrouter
install -p -m 755 %{buildroot}/_centos/tmp/contrail-vrouter*.tar.gz %{buildroot}/usr/src/modules/contrail-vrouter
rm %{buildroot}/_centos/tmp/contrail-vrouter*.tar.gz
rm -rf %{buildroot}/_centos
popd
#Build nova-contrail-vif
pushd %{_sbtop}
scons -U nova-contrail-vif
popd
pushd %{_sbtop}/build/noarch/nova_contrail_vif
python setup.py install --root=%{buildroot}
popd

# Install contrail utilities
install -D -m 755 %{_sbtop}/controller/src/config/utils/contrail-version %{buildroot}%{_bindir}/contrail-version
install -D -m 755 %{_sbtop}/controller/src/config/utils/contrail-status.py %{buildroot}%{_bindir}/contrail-status

#Needed for vrouter-dkms
install -d -m 755 %{buildroot}/usr/src/vrouter-%{_verstr}
pushd %{buildroot}/usr/src/vrouter
find . -print | sed 's;^;'"%{buildroot}/usr/src/vrouter-%{_verstr}/"';'| xargs install -d -m 755
rm -rf %{buildroot}/usr/src/vrouter

#Install the remaining files in /usr/share to /opt/contrail/utils
pushd %{buildroot}/usr/share/contrail
find . -print | sed 's;^;'"%{buildroot}%{_contrailutils}"';'| xargs install -d -m 755

%package vrouter
Summary:            Contrail vRouter
Group:              Applications/System

Requires: contrail-vrouter-agent >= %{_verstr}-%{_relstr}
Requires: contrail-lib >= %{_verstr}-%{_relstr}
Requires: xmltodict

%description vrouter
vrouter kernel module
The OpenContrail vRouter is a forwarding plane (of a distributed router) that runs in the hypervisor of a virtualized server. It extends the network from the physical routers and switches in a data center into a virtual overlay network hosted in the virtualized servers.
The OpenContrail vRouter is conceptually similar to existing commercial and open source vSwitches such as for example the Open vSwitch (OVS) but it also provides routing and higher layer services (hence vRouter instead of vSwitch).
The package opencontrail-vrouter-dkms provides the OpenContrail Linux kernel module.

%files vrouter
%defattr(-, root, root)
/lib/modules/*/extra/net/vrouter/vrouter.ko

%package vrouter-source
Summary:            Contrail vRouter

Group:              Applications/System

%description vrouter-source
Contrail vrouter source package
The OpenContrail vRouter is a forwarding plane (of a distributed router) that runs in the hypervisor of a virtualized server. It extends the network from the physical routers and switches in a data center into a virtual overlay network hosted in the virtualized servers. The OpenContrail vRouter is conceptually similar to existing commercial and open source vSwitches such as for example the Open vSwitch (OVS) but it also provides routing and higher layer services (hence vRouter instead of vSwitch).
 The package opencontrail-vrouter-source provides the OpenContrail Linux kernel module in source code format.

%files vrouter-source
/usr/src/modules/contrail-vrouter

%package config-openstack
Summary:            Config openstack

Group:              Applications/System

Requires:	    contrail-config >= %{_verstr}-%{_relstr}
Requires:	    python-keystoneclient
Requires:	    python-novaclient

%description config-openstack
Contrail config openstack package
This package contains the configuration management modules that interface with OpenStack.
%files config-openstack
%{python_sitelib}/svc_monitor*
%{python_sitelib}/vnc_openstack*
%{_bindir}/contrail-svc-monitor
%{_contrailetc}/svc-monitor.conf
/usr/share/contrail

%package -n python-contrail-vrouter-api
Summary:            Contrail vrouter api

Group:              Applications/System

%description -n python-contrail-vrouter-api
Contrail Virtual Router apis package

%files -n python-contrail-vrouter-api
%{python_sitelib}/contrail_vrouter_api*

%package -n python-contrail
Summary:            Contrail Python Lib

Group:              Applications/System
Obsoletes:          contrail-api-lib
Requires:	    python-importlib
Requires:	    python-bottle
Requires:	    python-gevent

%description -n python-contrail
Contrail Virtual Router utils package
The VRouter Agent API is used to inform the VRouter agent of the association between local interfaces (e.g. tap/tun or veth) and the interface uuid defined in the OpenContrail API server.

%files -n python-contrail
%{python_sitelib}/cfgm_common*
%{python_sitelib}/discoveryclient*
%{python_sitelib}/pysandesh*
%{python_sitelib}/sandesh-0.1dev*
%{python_sitelib}/sandesh_common*
%{python_sitelib}/vnc_api*
%{_contrailetc}/vnc_api_lib.ini

%package vrouter-utils
Summary:            Contrail vRouter

Group:              Applications/System

%description vrouter-utils
Contrail Virtual Router utils package
The OpenContrail vRouter is a forwarding plane (of a distributed router)that runs in the hypervisor of a virtualized server.
The package opencontrail-vrouter-utils provides command line utilities to configure and diagnose the OpenContrail Linux kernel module.

%files vrouter-utils
%{_bindir}/dropstats
%{_bindir}/flow
%{_bindir}/mirror
%{_bindir}/mpls
%{_bindir}/nh
%{_bindir}/rt
%{_bindir}/vrfstats
%{_bindir}/vif
%{_bindir}/vxlan

%package vrouter-agent

Summary:            Contrail vRouter

Group:              Applications/System

Requires:           contrail-lib >= %{_verstr}-%{_relstr}

%description vrouter-agent
Contrail Virtual Router Agent package
OpenContrail is a network virtualization solution that provides an overlay virtual-network to virtual-machines, containers or network namespaces.
This package provides the contrail-vrouter user space agent.

%files vrouter-agent
%defattr(-, root, root)
%{_bindir}/contrail-vrouter-agent
%{_contrailetc}/contrail-vrouter-agent.conf

%pre vrouter-agent
set -e
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post vrouter-agent
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

%package control
Summary:          Contrail Control
Group:            Applications/System

Requires:         contrail-lib >= %{_verstr}-%{_relstr}
Requires:         authbind

%description control
Contrail Control package
Control nodes implement the logically centralized portion of the control
plane. Not all control plane functions are logically centralized \u2013 some control plane functions are still implemented in a distributed fashion on the physical and virtual routers and switches in the network. Thecontrol nodes use the IF-MAP protocol to monitor the contents of the low-level technology data model as computed by the configuration nodes thatdescribes the desired state of the network. The control nodes use a combination of south-bound protocols to \u201cmake it so\u201d, i.e. to make the actual state of the network equal to the desired state of the network. In the initial version of the OpenContrail System these south-bound protocols include Extensible Messaging and Presence Protocol (XMPP)to control the OpenContrail vRouters as well as a combination of the Border Gateway Protocol (BGP) and the Network Configuration (Netconf) protocols to control physical routers. The control nodes also use BGP for state
 synchronization amongst each other when there are multiple instances of the control node for scale-out and high-availability reasons.
 Control nodes implement a logically centralized control plane that is
 responsible for maintaining ephemeral network state. Control nodes interact with each other and with network elements to ensure that network state is eventually consistent.

%files control
%defattr(-,root,root,-)
%{_bindir}/contrail-control
%config(noreplace) %{_contrailetc}/contrail-control.conf

%pre control
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post control
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/
# Use authbind to bind contrail-control on a reserved port,
# with contrail user privileges
if [ ! -f /etc/authbind/byport/179 ]; then
  touch /etc/authbind/byport/179
  chown contrail. /etc/authbind/byport/179
  chmod 0755 /etc/authbind/byport/179
fi

%package python-contrail-vrouter-netns

Summary:            Contrail vRouter netns

Group:              Applications/System

%description python-contrail-vrouter-netns
Contrail Virtual Router NetNS package

%files python-contrail-vrouter-netns
%defattr(-,root,root)
%{python_sitelib}/opencontrail_vrouter_netns*
%{_bindir}/opencontrail-vrouter-netns


%package lib
Summary:  Libraries used by the Contrail Virtual Router %{?_gitVer}
Group:              Applications/System
Obsoletes:          contrail-libs

%description lib
Libraries used by the Contrail Virtual Router.

%files lib
%defattr(-,root,root)
%{_libdir}/../lib/lib*.so*
 
%package config
Summary: Contrail Config
Group:              Applications/System

BuildArch: noarch
Requires: python-contrail >= %{_verstr}-%{_relstr}
Requires: python-bitarray
Requires: python-gevent
Requires: python-geventhttpclient
Requires: python-lxml
Requires: pycassa
Requires: python-thrift
Requires: python-keystone
Requires: python-psutil
Requires: python-requests
Requires: python-zope-interface
Requires: xmltodict >= 0.1
Requires: python-jsonpickle
Requires: python-amqp

%description config
Contrail Config package
Configuration nodes are responsible for the management layer. The
 configuration nodes provide a north-bound Representational State Transfer (REST) Application Programming Interface (API) that can be used to configure the system or extract operational status of the system. The instantiated services are represented by objects in a horizontally scalable database that is described by a formal service data model (more about data models later on). The configuration nodes also contain a transformation engine (sometimes referred to as a compiler) that transforms the objects in the high-level service data model into corresponding more lower-level objects in the technology data model. Whereas the high-level service data model describes what services need to be implemented, the low-level technology data model describes how those services need to be implemented.
The configuration nodes publish the contents of the low-level technology data model to the control nodes using the Interface for Metadata Access Points (IF-MAP) protocol.
Configuration nodes keep a persistent copy of the intended configuration state and translate the high-level data model into the lower level model suitable for interacting with network elements. Both these are kept in a NoSQL database.

%files config
%defattr(-,contrail,contrail,-)
%config(noreplace) %{_sysconfdir}/contrail/contrail-api.conf
%config(noreplace) %{_sysconfdir}/contrail/contrail-schema.conf
%config(noreplace) %{_sysconfdir}/contrail/contrail-discovery.conf
%defattr(-,root,root,-)
%{_bindir}/contrail-api
%{_bindir}/contrail-schema
%{_bindir}/contrail-discovery
%{_bindir}/ifmap-view
%{python_sitelib}/discovery
%{python_sitelib}/discovery-*
%{python_sitelib}/schema_transformer*
%{python_sitelib}/vnc_cfg_api_server*

%pre config
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post config
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

%package analytics
Summary:            Contrail Analytics
Group:              Applications/System

Requires:           xmltodict
Requires:           contrail-lib >= %{_verstr}-%{_relstr}
Requires:           pycassa
Requires:           redis-py
Requires:           redis >= 2.6.13-1
Requires:           python-contrail >= %{_verstr}-%{_relstr}
Requires:           python-psutil
Requires:           python-prettytable
Requires:           python-geventhttpclient
Requires:           protobuf

%description analytics
Contrail Analytics package
Analytics nodes are responsible for collecting, collating and presenting
analytics information for trouble shooting problems and for understanding network usage. Each component of the OpenContrail System generates detailed event records for every significant event in the system. These event records are sent to one of multiple instances (for scale-out) of the analytics node that collate and store the information in a horizontally scalable database using a format that is optimized for time-series analysis and queries.
the analytics nodes have mechanism to automatically trigger the collection of more detailed records when certain event occur; the goal is to be able to get to the root cause of any issue without having to reproduce it. The analytics nodes provide a north-bound analytics query REST API.
Analytics nodes collect, store, correlate, and analyze information from
 network elements, virtual or physical. This information includes statistics,logs, events, and errors.

%files analytics
# Setup directories
%defattr(-,contrail,contrail,)
%config(noreplace) %{_contrailetc}/contrail-collector.conf
%config(noreplace) %{_contrailetc}/contrail-analytics-api.conf
%config(noreplace) %{_contrailetc}/contrail-query-engine.conf
%defattr(-, root, root)
%{_bindir}/contrail-collector
%{_bindir}/contrail-query-engine
%{_bindir}/contrail-analytics-api
%{python_sitelib}/opserver*
%{_bindir}/contrail-logs
%{_bindir}/contrail-flows
%{_bindir}/contrail-stats

%pre analytics
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post analytics
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

%package dns
Summary:            Contrail Dns
Group:              Applications/System

Requires:           authbind

%description dns
Contrail dns  package
DNS provides dnsd, named, rndc deamons
Provides vrouter services

%pre dns
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post dns
set -e
mkdir -p /var/log/named /etc/contrail/dns
chown -R contrail:adm /var/log/named
chmod 0750 /var/log/named
chown -R contrail. /etc/contrail/dns
chmod 0750 /etc/contrail/dns

# Use authbind to bind amed on a reserved port,
# with contrail user privileges
if [ ! -f /etc/authbind/byport/53 ]; then
  touch /etc/authbind/byport/53
  chown contrail. /etc/authbind/byport/53
  chmod 0755 /etc/authbind/byport/53
fi

%files dns
%defattr(-,contrail,contrail,-)
%{_contraildns}
%{_contraildns}/named.conf
%{_contraildns}/rndc.conf
%{_contraildns}/dns.conf
%defattr(-, root, root)
%{_bindir}/named
%{_bindir}/rndc
%{_bindir}/dnsd

%package nova-vif
Summary:            Contrail nova vif driver
Group:              Applications/System

%description nova-vif
Contrail Nova Vif driver package

%files nova-vif
%defattr(-,root,root,-)
%{python_sitelib}/nova_contrail_vif*

%package utils
Summary: Contrail utility sctipts.
Group: Applications/System

Requires: python-lxml
Requires: python-requests
Requires: python-contrail >= %{_verstr}-%{_relstr}

%description utils
Contrail utility sctipts package

%files utils
%{_bindir}/contrail-version
%{_bindir}/contrail-status
