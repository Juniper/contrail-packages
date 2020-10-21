%define         _unpackaged_files_terminate_build 0
%define         _contrailetc /etc/contrail
%define         _contrailutils /opt/contrail/utils
%define         _distropkgdir tools/packaging/common/control_files
%define         _contraildns /etc/contrail/dns
%define         _distrorpmpkgdir tools/packages/rpm/contrail

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
%if 0%{?_kVers:1}
%define         _kvers      %{_kVers}
%else
%define         _kvers      3.10.0-862.el7.x86_64 3.10.0-957.el7.x86_64 3.10.0-1127.19.1.el7.x86_64 3.10.0-1127.10.1.el7.x86_64
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
BuildRequires:  net-snmp-python
BuildRequires:  cassandra-cpp-driver
BuildRequires:  cassandra-cpp-driver-devel
BuildRequires:  libzookeeper-devel
BuildRequires:  librdkafka-devel >= 0.9.0

%prep

%install
pushd %{_sbtop}
scons --root=%{buildroot} install
for kver in %{_kvers}; do
    echo "Kver = ${kver}"
    set +e
    ls /lib/modules/${kver}/build
    exit_code=$?
    set -e
    if [ $exit_code == 0 ]; then
        scons --kernel-dir=/lib/modules/${kver}/build build-kmodule --root=%{buildroot}
    else
        echo "WARNING: kernel-devel-$kver is not installed, Skipping building vrouter for $kver"
    fi
done
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

# contrail-docs
# Index files
python %{_sbtop}/tools/packages/utils/generate_doc_index.py %{buildroot}/usr/share/doc/contrail-docs/html/messages

# Install supervisor files
pushd %{_builddir}/..
install -p -m 755 %{_distrorpmpkgdir}/supervisor-control.initd  %{buildroot}/etc/init.d/supervisor-control
install -p -m 755 %{_distrorpmpkgdir}/supervisor-config.initd  %{buildroot}/etc/init.d/supervisor-config
install -p -m 755 %{_distrorpmpkgdir}/supervisor-analytics.initd  %{buildroot}/etc/init.d/supervisor-analytics
install -p -m 755 %{_distrorpmpkgdir}/supervisor-vrouter.initd  %{buildroot}/etc/init.d/supervisor-vrouter
popd

# Install contrail utilities
install -D -m 755 %{_sbtop}/controller/src/config/utils/contrail-version %{buildroot}%{_bindir}/contrail-version
install -D -m 755 %{_sbtop}/controller/src/config/utils/contrail-status.py %{buildroot}%{_bindir}/contrail-status
install -D -m 755 %{_sbtop}/controller/src/analytics/database/utils/contrail-cassandra-status.py %{buildroot}%{_bindir}/contrail-cassandra-status
install -D -m 755 %{_sbtop}/controller/src/analytics/database/utils/contrail-cassandra-repair.py %{buildroot}%{_bindir}/contrail-cassandra-repair
install -D -m 755 %{_sbtop}/controller/src/config/utils/contrail-diff-docs.py %{buildroot}%{_bindir}/contrail-diff-docs

#Needed for vrouter-dkms
install -d -m 755 %{buildroot}/usr/src/vrouter-%{_verstr}
pushd %{buildroot}/usr/src/vrouter
find . -print | sed 's;^;'"%{buildroot}/usr/src/vrouter-%{_verstr}/"';'| xargs install -d -m 755
rm -rf %{buildroot}/usr/src/vrouter

#Install the remaining files in /usr/share to /opt/contrail/utils
pushd %{buildroot}/usr/share/contrail
find . -print | sed 's;^;'"%{buildroot}%{_contrailutils}"';'| xargs install -d -m 755

#Needed for Lbaas
install -d -m 755 %{buildroot}/etc/sudoers.d/
echo 'Defaults:root !requiretty' >> %{buildroot}/contrail-lbaas
install -m 755 %{buildroot}/contrail-lbaas  %{buildroot}/etc/sudoers.d/contrail-lbaas
rm -rf %{buildroot}/contrail-lbaas

%package vrouter
Summary:            Contrail vRouter
Group:              Applications/System

Requires: contrail-vrouter-agent >= %{_verstr}-%{_relstr}
Requires: contrail-lib >= %{_verstr}-%{_relstr}
Requires: xmltodict >= 0.7.0

%description vrouter
vrouter kernel module
The OpenContrail vRouter is a forwarding plane (of a distributed router) that runs in the hypervisor of a virtualized server. It extends the network from the physical routers and switches in a data center into a virtual overlay network hosted in the virtualized servers.
The OpenContrail vRouter is conceptually similar to existing commercial and open source vSwitches such as for example the Open vSwitch (OVS) but it also provides routing and higher layer services (hence vRouter instead of vSwitch).
The package opencontrail-vrouter-dkms provides the OpenContrail Linux kernel module.

%preun vrouter
# Execute only during uninstall, skip during upgrade
if [ $1 == 0 ]; then
    if [ -L /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko ]; then
        echo "Removing symbolic link /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko"
        rm -f /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko
    fi
else
    echo "Skip removing /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko for upgrade"
fi
exit 0

%post vrouter
act_kver=$(uname -r)
kver=$(uname -r | cut -d "-" -f1)
vrouter_actual_path=$(ls -1rt /lib/modules/${kver}*/extra/net/vrouter/vrouter.ko | tail -1)

if [ -f "/lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko" ]; then
    depmod -a
    echo "Installed vrouter at /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko"
elif [ -f "$vrouter_actual_path" ]; then
    echo "Create symbolic link to $vrouter_actual_path at /lib/modules/$(uname -r)/extra/net/vrouter/vrouter.ko"
    mkdir -p /lib/modules/$(uname -r)/extra/net/vrouter/
    ln -s "$vrouter_actual_path" /lib/modules/$(uname -r)/extra/net/vrouter/
    if [ $? != 0 ]; then
        echo "ERROR: Unable to create symlink to $vrouter_actual_path"
        exit 126
    fi
    depmod -a
else
    echo "ERROR: vrouter module is not supported in current kernel version $(uname -r)"
    exit 1
fi
exit 0

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
%config(noreplace) %{_contrailetc}/contrail-svc-monitor.conf
%config(noreplace) /etc/contrail/supervisord_config_files/contrail-svc-monitor.ini
/usr/share/contrail
/etc/init.d/contrail-svc-monitor

%post config-openstack
chmod +x /etc/init.d/contrail-svc-monitor

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
Requires:       python-kombu
Requires:	    python-bottle >= 0.11.6
%if 0%{?rhel} >= 7
Requires:	    python-gevent >= 1.0
%endif
%if 0%{?rhel} <= 6
Requires:          python-gevent
%endif
%if 0%{?rhel}
Requires:          consistent_hash
%else
Requires:          python-consistent_hash
%endif
%if 0%{?rhel} <= 6
Requires:          python-importlib
%endif

%description -n python-contrail
Contrail Virtual Router utils package
The VRouter Agent API is used to inform the VRouter agent of the association between local interfaces (e.g. tap/tun or veth) and the interface uuid defined in the OpenContrail API server.

%files -n python-contrail
%{python_sitelib}/cfgm_common*
%{python_sitelib}/discoveryclient*
%{python_sitelib}/libpartition*
%{python_sitelib}/pysandesh*
%{python_sitelib}/sandesh-0.1dev*
%{python_sitelib}/sandesh_common*
%{python_sitelib}/vnc_api*
%config(noreplace) %{_contrailetc}/vnc_api_lib.ini

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
%{_bindir}/vrouter
%{_bindir}/vrmemstats
%{_bindir}/qosmap
%{_bindir}/vifdump

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
%{_bindir}/contrail-tor-agent
%{_bindir}/vrouter-port-control
%{_bindir}/contrail-vrouter-agent-health-check.py
%config(noreplace) %{_contrailetc}/contrail-vrouter-agent.conf
%config(noreplace) %{_contrailetc}/supervisord_vrouter.conf
/etc/init.d/contrail-vrouter-agent
%config(noreplace) /etc/contrail/supervisord_vrouter_files/contrail-vrouter-agent.ini
/etc/init.d/supervisor-vrouter

%pre vrouter-agent
set -e
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post vrouter-agent
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
mkdir -p /var/lib/contrail/dhcp/
mkdir -p /etc/contrail/ssl/certs/ /etc/contrail/ssl/private/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/ /etc/contrail/ssl/
chown -R contrail:contrail /etc/contrail/ssl/certs/ /etc/contrail/ssl/private/
chmod 0750 /etc/contrail/ /etc/contrail/ssl/ /etc/contrail/ssl/certs/
chmod 0700 /etc/contrail/ssl/private/
chmod 0750 /var/lib/contrail/dhcp/
chmod +x /etc/init.d/contrail-vrouter-agent
chmod +x /etc/init.d/supervisor-vrouter

# change file permissions during upgrade
if [ -f /var/log/contrail/contrail-vrouter-nodemgr-stdout.log ]; then
  chown contrail:contrail /var/log/contrail/process_statecontrail-vrouter.json
  chown contrail:contrail /var/log/contrail/contrail-vrouter-nodemgr-stderr.log
  chown contrail:contrail /var/log/contrail/contrail-vrouter-nodemgr-stdout.log
fi

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
%config(noreplace) /etc/contrail/supervisord_control.conf
%config(noreplace) /etc/contrail/supervisord_control_files/contrail-control.ini
/etc/contrail/supervisord_control_files/contrail-control.rules
/etc/init.d/contrail-control
/etc/init.d/supervisor-control

%pre control
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post control
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

# change file permissions during upgrade
if [ -f /var/log/contrail/contrail-control-nodemgr-stdout.log ]; then
  chown contrail:contrail /var/log/contrail/process_statecontrail-control.json
  chown contrail:contrail /var/log/contrail/contrail-control-nodemgr-stderr.log
  chown contrail:contrail /var/log/contrail/contrail-control-nodemgr-stdout.log
fi

# Use authbind to bind contrail-control on a reserved port,
# with contrail user privileges
if [ ! -f /etc/authbind/byport/179 ]; then
  touch /etc/authbind/byport/179
  chown contrail. /etc/authbind/byport/179
  chmod 0755 /etc/authbind/byport/179
fi
chmod +x /etc/init.d/supervisor-control
chmod +x /etc/init.d/contrail-control

%package -n python-opencontrail-vrouter-netns

Summary:            OpenContrail vRouter netns

Group:              Applications/System

%if 0%{?rhel} > 6
Requires:           python-websocket-client >= 0.32.0
Requires:           python-docker-py >= 1.4.0
%else
Requires:           python-docker-py
%endif

Requires:           python-unittest2
Requires:           iproute >= 3.1.0
Requires:           python-requests >= 2.5.1

%description -n python-opencontrail-vrouter-netns
Contrail Virtual Router NetNS package

%files -n python-opencontrail-vrouter-netns
%defattr(-,root,root)
%{python_sitelib}/opencontrail_vrouter_*
%{_bindir}/opencontrail-vrouter-*
/etc/sudoers.d/contrail-lbaas


%package lib
Summary:  Libraries used by the Contrail Virtual Router %{?_gitVer}
Group:              Applications/System
Obsoletes:          contrail-libs
Obsoletes:          libtbb2

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
Requires: python-bitarray >= 0.8.0
%if 0%{?rhel} >= 7
Requires:	    python-gevent >= 1.0
%endif
%if 0%{?rhel} <= 6
Requires:          python-gevent
%endif
Requires: python-geventhttpclient
Requires: python-lxml >= 2.3.2
Requires: python-pycassa
Requires: python-thrift >= 0.9.1
Requires: python-keystone
Requires: python-psutil >= 0.6.0
Requires: python-requests
Requires: python-zope-interface
Requires: xmltodict >= 0.7.0
Requires: python-jsonpickle
Requires: python-amqp
Requires: python-kazoo >= 2.2.1
Requires: python-ncclient >= 0.3.2

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
%config(noreplace) %{_sysconfdir}/contrail/contrail-device-manager.conf
%defattr(-,root,root,-)
%{_bindir}/contrail-api
%{_bindir}/contrail-schema
%{_bindir}/contrail-discovery
%{_bindir}/contrail-device-manager
%{_bindir}/ifmap-view
%{_bindir}/contrail-issu-pre-sync
%{_bindir}/contrail-issu-post-sync
%{_bindir}/contrail-issu-run-sync
%{_bindir}/contrail-issu-zk-sync
%{python_sitelib}/discovery
%{python_sitelib}/discovery-*
%{python_sitelib}/schema_transformer*
%{python_sitelib}/vnc_cfg_api_server*
%{python_sitelib}/device_manager*
%{python_sitelib}/device_api*
%{python_sitelib}/contrail_issu*
%if 0%{?rhel} > 6
%docdir /usr/share/doc/contrail-config/*
%endif
/etc/contrail/supervisord_config.conf
/etc/contrail/supervisord_config_files/contrail-api.ini
/etc/contrail/supervisord_config_files/contrail-config.rules
/etc/contrail/supervisord_config_files/contrail-discovery.ini
/etc/contrail/supervisord_config_files/contrail-schema.ini
/etc/contrail/supervisord_config_files/contrail-device-manager.ini
/etc/init.d/contrail-discovery
/etc/init.d/contrail-schema
/etc/init.d/contrail-device-manager
/etc/init.d/contrail-api
/etc/init.d/supervisor-config

%pre config
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post config
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/
chmod +x /etc/init.d/contrail-api
chmod +x /etc/init.d/contrail-schema
chmod +x /etc/init.d/contrail-device-manager
chmod +x /etc/init.d/contrail-discovery
chmod +x /etc/init.d/supervisor-config
chown contrail:contrail /usr/bin/contrail-cassandra-status
chown contrail:contrail /usr/bin/contrail-cassandra-repair

if [ -f /var/log/cassandra/status.log]; then
    mv /var/log/cassandra/status-up /var/log/contrail/cassandra-status-up
    chown contrail:contrail /var/log/contrail/cassandra-status-up
    mv /var/log/cassandra/status.log /var/log/contrail/cassandra-status.log
    chown contrail:contrail /var/log/contrail/cassandra-status.log
fi

# change file permissions during upgrade
if [ -f /var/log/contrail/contrail-config-nodemgr-stdout.log ]; then
  chown contrail:contrail /var/log/contrail/process_statecontrail-config.json
  chown contrail:contrail /var/log/contrail/contrail-config-nodemgr-stderr.log
  chown contrail:contrail /var/log/contrail/contrail-config-nodemgr-stdout.log
fi

%package analytics
Summary:            Contrail Analytics
Group:              Applications/System

Requires:           xmltodict >= 0.7.0
Requires:           contrail-lib >= %{_verstr}-%{_relstr}
Requires:           python-pycassa
Requires:           python-redis >= 2.10.3
Requires:           redis >= 2.6.13-1
Requires:           python-contrail >= %{_verstr}-%{_relstr}
Requires:           python-psutil >= 0.6.0
Requires:           python-prettytable
Requires:           python-geventhttpclient
Requires:           protobuf
Requires:           cassandra-cpp-driver
Requires:           libzookeeper
Requires:           net-snmp-python
Requires:           librdkafka1
Requires:           python-kafka >= 1.0.1, python-kafka <= 1.0.2
Requires:           python-stevedore
Requires:           python-kazoo >= 2.2.1
Requires:           python-sseclient
Requires:           python-amqp
%if 0%{?rhel} >= 7
Requires:           python-cassandra-driver >= 3.0.0
%endif

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
%config(noreplace) %{_contrailetc}/contrail-snmp-collector.conf
%config(noreplace) %{_contrailetc}/contrail-topology.conf
%config(noreplace) %{_contrailetc}/contrail-alarm-gen.conf
%defattr(-, root, root)
%{_bindir}/contrail-collector
%{_bindir}/contrail-query-engine
%{_bindir}/contrail-analytics-api
%{_bindir}/contrail-alarm-gen
%{python_sitelib}/opserver*
%{python_sitelib}/contrail_snmp_collector*
%{python_sitelib}/contrail_topology*
%{_bindir}/contrail-logs
%{_bindir}/contrail-flows
%{_bindir}/contrail-db
%{_bindir}/contrail-stats
%{_bindir}/contrail-alarm-notify
%{_bindir}/contrail-logs-api-audit
%{_bindir}/contrail-snmp-*
%{_bindir}/contrail-topology
/usr/share/doc/contrail-analytics-api
%config(noreplace) /etc/contrail/supervisord_analytics.conf
%config(noreplace) /etc/contrail/supervisord_analytics_files/contrail-analytics-api.ini
%config(noreplace) /etc/contrail/supervisord_analytics_files/contrail-alarm-gen.ini
/etc/contrail/supervisord_analytics_files/contrail-analytics.rules
%config(noreplace) /etc/contrail/supervisord_analytics_files/contrail-collector.ini
%config(noreplace) /etc/contrail/supervisord_analytics_files/contrail-query-engine.ini
%config(noreplace) %{_contrailetc}/supervisord_analytics_files/contrail-snmp-collector.ini
%config(noreplace) %{_contrailetc}/supervisord_analytics_files/contrail-topology.ini
/etc/init.d/contrail-analytics-api
/etc/init.d/contrail-alarm-gen
/etc/init.d/contrail-collector
/etc/init.d/contrail-query-engine
/etc/init.d/supervisor-analytics
/etc/init.d/contrail-snmp-collector
/etc/init.d/contrail-topology
/usr/share/mibs/netsnmp
/etc/contrail/snmp.conf

%pre analytics
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post analytics
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/
chmod +x /etc/init.d/supervisor-analytics
chmod +x /etc/init.d/contrail-analytics-api
chmod +x /etc/init.d/contrail-alarm-gen
chmod +x /etc/init.d/contrail-collector
chmod +x /etc/init.d/contrail-query-engine
chmod +x /etc/init.d/contrail-snmp-collector
chmod +x /etc/init.d/contrail-topology

# change file permissions during upgrade
if [ -f /var/log/contrail/contrail-analytics-nodemgr-stdout.log ]; then
  chown contrail:contrail /var/log/contrail/process_statecontrail-analytics.json
  chown contrail:contrail /var/log/contrail/contrail-analytics-nodemgr-stderr.log
  chown contrail:contrail /var/log/contrail/contrail-analytics-nodemgr-stdout.log
fi

%package dns
Summary:            Contrail Dns
Group:              Applications/System

Requires:           authbind

%description dns
Contrail dns  package
DNS provides contrail-dns, contrail-named, contrail-rndc and
contrail-rndc-confgen daemons
Provides vrouter services

%pre dns
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContrail daemon" contrail

%post dns
set -e
mkdir -p /var/log/contrail /etc/contrail/dns
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail. /etc/contrail/dns
chmod 0750 /etc/contrail/dns
chmod +x /etc/init.d/contrail-dns
chmod +x /etc/init.d/contrail-named

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
%config(noreplace) %{_contraildns}/contrail-named.conf
%config(noreplace) %{_contraildns}/contrail-rndc.conf
%config(noreplace) %{_contraildns}/applynamedconfig.py
%config(noreplace) %{_contrailetc}/contrail-dns.conf
%{_contraildns}/COPYRIGHT
%defattr(-, root, root)
%{_bindir}/contrail-named
%{_bindir}/contrail-rndc
%{_bindir}/contrail-rndc-confgen
%{_bindir}/contrail-dns
%if 0%{?rhel} > 6
%docdir /usr/lib/python2.7/site-packages/doc/*
%endif
%config(noreplace) /etc/contrail/supervisord_control_files/contrail-dns.ini
%config(noreplace) /etc/contrail/supervisord_control_files/contrail-named.ini
/etc/init.d/contrail-dns
/etc/init.d/contrail-named

%package nova-vif
Summary:            Contrail nova vif driver
Group:              Applications/System

%description nova-vif
Contrail Nova Vif driver package

%files nova-vif
%defattr(-,root,root,-)
%{python_sitelib}/nova_contrail_vif*
%{python_sitelib}/vif_plug_vrouter

%package utils
Summary: Contrail utility sctipts.
Group: Applications/System

Requires: lsof
Requires: python-lxml >= 2.3.2
Requires: python-requests
Requires: python-contrail >= %{_verstr}-%{_relstr}

%description utils
Contrail utility sctipts package

%files utils
%{_bindir}/contrail-version
%{_bindir}/contrail-status
%{_bindir}/contrail-cassandra-status
%{_bindir}/contrail-cassandra-repair

%package docs
Summary: Documentation for OpenContrail
Group: Applications/System

%description docs
OpenContrail is a network virtualization solution that provides an overlay
virtual-network to virtual-machines, containers or network namespaces.

This package contains the documentation for messages generated by OpenContrail
modules/daemons.

%files docs
%doc /usr/share/doc/contrail-docs/html/*
