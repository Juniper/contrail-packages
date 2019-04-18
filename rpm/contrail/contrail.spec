%define         _unpackaged_files_terminate_build 0
%define         _contrailetc /etc/contrail
%define         _contrailutils /opt/contrail/utils
%define         _fabricansible /opt/contrail/fabric_ansible_playbooks
%define         _distropkgdir %{_sbtop}tools/packages/rpm/%{name}
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
%if 0%{?_kVers:1}
%define         _kvers      %{_kVers}
%else
%define         _kvers      3.10.0-327.10.1.el7.x86_64
%endif
%if 0%{?_opt:1}
%define         _sconsOpt      %{_opt}
%else
%define         _sconsOpt      debug
%endif

%global _dwz_low_mem_die_limit 0

%bcond_without debuginfo

Name:           contrail
Version:        %{_verstr}
Release:        %{_relstr}%{?dist}
Summary:        Contrail

Group:          Applications/System
License:        ASL 2.0
URL:            www.opencontrail.org
Vendor:         OpenContrail Project.

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bison
BuildRequires: boost-devel
BuildRequires: cassandra-cpp-driver
BuildRequires: cassandra-cpp-driver-devel
BuildRequires: cmake
BuildRequires: cyrus-sasl-devel
BuildRequires: flex
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: grok
BuildRequires: grok-devel
BuildRequires: kernel-devel
BuildRequires: libcurl-devel
BuildRequires: librdkafka-devel < 0.11.5
BuildRequires: libstdc++-devel
BuildRequires: libtool
BuildRequires: libxml2-devel
BuildRequires: libzookeeper-devel
BuildRequires: lz4-devel
BuildRequires: make
BuildRequires: openssl
BuildRequires: openssl-devel
BuildRequires: protobuf
BuildRequires: protobuf-compiler
BuildRequires: protobuf-devel
BuildRequires: python-devel
BuildRequires: python-fixtures
BuildRequires: python-lxml
BuildRequires: python-requests
BuildRequires: python-setuptools
BuildRequires: python-sphinx
BuildRequires: scons
BuildRequires: systemd-units
BuildRequires: tbb-devel
BuildRequires: tokyocabinet-devel
BuildRequires: unzip
BuildRequires: vim-common
BuildRequires: zlib-devel
BuildRequires: libcmocka-devel

%description
Contrail package describes all sub packages that are required to
run open contrail.

%if %{with debuginfo}
%debug_package
%endif

%prep

%build

%install
pushd %{_sbtop}
scons --opt=%{_sconsOpt} --root=%{buildroot} --without-dpdk install
for kver in %{_kvers}; do
    echo "Kver = ${kver}"
    set +e
    ls /lib/modules/${kver}/build
    exit_code=$?
    set -e
    if [ $exit_code == 0 ]; then
        sed 's/{kver}/%{_kver}/g' %{_distropkgdir}/dkms.conf.in.tmpl > %{_distropkgdir}/dkms.conf.in
        scons --opt=%{_sconsOpt} --kernel-dir=/lib/modules/${kver}/build build-kmodule --root=%{buildroot}
    else
        echo "WARNING: kernel-devel-$kver is not installed, Skipping building vrouter for $kver"
    fi
done
mkdir -p %{buildroot}/_centos/tmp
popd
pushd %{buildroot}
mkdir -p %{buildroot}/centos
cp %{_distropkgdir}/dkms.conf.in %{buildroot}/centos/
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
scons --opt=%{_sconsOpt} -U nova-contrail-vif
popd
pushd %{_sbtop}/build/noarch/nova_contrail_vif
python setup.py install --root=%{buildroot}
popd

# contrail-docs
# Move schema specific files to opserver
for mod_dir in %{buildroot}/usr/share/doc/contrail-docs/html/messages/*; do \
    if [ -d $mod_dir ]; then \
        for python_dir in %{buildroot}%{python_sitelib}; do \
            install -d -m 0755 -p $python_dir/opserver/stats_schema/`basename $mod_dir`; \
            for statsfile in %{buildroot}/usr/share/doc/contrail-docs/html/messages/`basename $mod_dir`/*_stats_tables.json; do \
                install -p -m 644 -t $python_dir/opserver/stats_schema/`basename $mod_dir`/ $statsfile; \
                rm -f $statsfile; \
            done \
        done \
    fi \
done

# Index files
python %{_sbtop}/tools/packages/utils/generate_doc_index.py %{buildroot}/usr/share/doc/contrail-docs/html/messages
# contrail-cli
install -d -m 0755 %{buildroot}/etc/bash_completion.d
python %{_sbtop}/tools/packages/utils/generate_cli_commands.py %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli %{buildroot}
pushd %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli/contrail_cli; python setup.py install --root=%{buildroot}; popd
pushd %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli/contrail_analytics_cli; python setup.py install --root=%{buildroot}; popd
pushd %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli/contrail_config_cli; python setup.py install --root=%{buildroot}; popd
pushd %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli/contrail_control_cli; python setup.py install --root=%{buildroot}; popd
pushd %{_sbtop}/build/%{_sconsOpt}/utils/contrail-cli/contrail_vrouter_cli; python setup.py install --root=%{buildroot}; popd

#Needed for agent container env
# install vrouter.ko at /opt/contrail/vrouter-kernel-modules to use with containers
for vrouter_ko in $(ls -1 %{buildroot}/lib/modules/*/extra/net/vrouter/vrouter.ko); do
  build_root=$(echo %{buildroot})
  kernel_ver=$(echo ${vrouter_ko#${build_root}/lib/modules/} | awk -F / '{print $1}')
  install -d -m 755 %{buildroot}/%{_contrailutils}/../vrouter-kernel-modules/$kernel_ver/
  install -p -m 755 $vrouter_ko %{buildroot}/%{_contrailutils}/../vrouter-kernel-modules/$kernel_ver/vrouter.ko
done

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

# Install section of contrail-utils package - START
install -d -m 755 %{buildroot}/usr/share/contrail-utils
# copy files present in /usr/share/contrail to /usr/share/contrail-utils
# LP 1668338
pushd %{buildroot}/usr/share/contrail/
find . -maxdepth 1 -type f -exec cp {} %{buildroot}/usr/share/contrail-utils/ \;
popd
# Create symlink to utils script at /usr/bin
pushd %{buildroot}/usr/bin
for scriptpath in %{buildroot}/usr/share/contrail-utils/*; do
  scriptname=$(basename $scriptpath)
  scriptname_no_ext=${scriptname%.*}
  # avoid conflicting with coreutils package for file /usr/bin/chmod
  # LP #1668332
  if [[ $scriptname_no_ext == "chmod" ]]; then
    continue
  fi
  if [ ! -f $scriptname_no_ext ]; then
    ln -s ../share/contrail-utils/$scriptname $scriptname_no_ext
    echo /usr/bin/$scriptname_no_ext >> %{buildroot}/contrail-utils-bin-includes.txt
  else
    echo "WARNING: Skipping ( $scriptname_no_ext ) as a regular file of same name exists in /usr/bin/"
  fi
done
popd
# Install section of contrail-utils package - END

# Install section of contrail-test package - Start
cp -a %{_sbtop}/third_party/contrail-test %{buildroot}/contrail-test
rm -rf %{buildroot}/contrail-test/.git*
# Install section of contrail-test package - End

# Install section of contrail-fabric-utils package - Start
rm -rf %{_sbtop}/third_party/fabric-utils/contrail_fabric_utils-0.1dev
rm -rf %{_sbtop}/third_party/fabric-utils/contrail_fabric_utils.egg-info
pushd %{_sbtop}/third_party/fabric-utils
%{__python} setup.py sdist
tar zxf dist/contrail_fabric_utils-0.1dev.tar.gz
cd contrail_fabric_utils-0.1dev
%{__python} setup.py install --root=%{buildroot}
mkdir -p %{buildroot}%{_contrailutils}/
cp README %{buildroot}%{_contrailutils}/README.fabric
cp -R %{buildroot}%{python_sitelib}/contrail_fabric_utils/fabfile %{buildroot}%{_contrailutils}/fabfile
popd
# Install section of contrail-fabric-utils package - End

# Install section of contrail-config package - Start
install -d -m 755 %{buildroot}%{_fabricansible}
install -p -m 755 %{buildroot}/usr/bin/fabric_ansible_playbooks*.tar.gz %{buildroot}%{_fabricansible}/
# Install section of contrail-config package - End

# Install section of contrail-manifest package - Start
%if 0%{?_manifestFile:1}
mkdir -p %{buildroot}/opt/contrail/
cp %{_manifestFile} %{buildroot}/opt/contrail/manifest.xml
%endif
# Install section of contrail-manifest package - End

%files

%package vrouter
Summary:            Contrail vRouter
Group:              Applications/System

Requires:           contrail-vrouter-agent >= %{_verstr}-%{_relstr}
Requires:           contrail-lib >= %{_verstr}-%{_relstr}
Requires:           xmltodict >= 0.7.0

%description vrouter
vrouter kernel module

The OpenContrail vRouter is a forwarding plane (of a distributed router) that
runs in the hypervisor of a virtualized server. It extends the network from the
physical routers and switches in a data center into a virtual overlay network
hosted in the virtualized servers.

The OpenContrail vRouter is conceptually similar to existing commercial and
open source vSwitches such as for example the Open vSwitch (OVS) but it also
provides routing and higher layer services (hence vRouter instead of vSwitch).

The package opencontrail-vrouter-dkms provides the OpenContrail Linux kernel
module.

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
/opt/contrail/vrouter-kernel-modules/*/vrouter.ko

%package vrouter-source
Summary:            Contrail vRouter

Group:              Applications/System

%description vrouter-source
Contrail vrouter source package

The OpenContrail vRouter is a forwarding plane (of a distributed router) that
runs in the hypervisor of a virtualized server. It extends the network from the
physical routers and switches in a data center into a virtual overlay network
hosted in the virtualized servers. The OpenContrail vRouter is conceptually
similar to existing commercial and open source vSwitches such as for example
the Open vSwitch (OVS) but it also provides routing and higher layer services
(hence vRouter instead of vSwitch).

The package opencontrail-vrouter-source provides the OpenContrail Linux kernel
module in source code format.

%files vrouter-source
/usr/src/modules/contrail-vrouter

%package config-openstack
Summary:            Config openstack

Group:              Applications/System

Requires:           contrail-config >= %{_verstr}-%{_relstr}
Requires:           python-keystoneclient
Requires:           python-novaclient
Requires:           python-ironic-inspector-client
Requires:           python-ironicclient
Requires:           ipmitool

%description config-openstack
Contrail config openstack package
This package contains the configuration management modules that interface with OpenStack.
%files config-openstack
%{python_sitelib}/svc_monitor*
%{python_sitelib}/vnc_openstack*
%{_bindir}/contrail-svc-monitor
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

Group:             Applications/System
Obsoletes:         contrail-api-lib <= 0.0.1
Requires:          python-kombu
Requires:          python-bottle >= 0.11.6
%if 0%{?rhel} >= 7
Requires:          python-gevent >= 1.0
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
Requires:          python-sqlalchemy
Requires:          python-crypto
Requires:          python-fysom

%description -n python-contrail
Contrail Virtual Router utils package

The VRouter Agent API is used to inform the VRouter agent of the association
between local interfaces (e.g. tap/tun or veth) and the interface uuid defined
in the OpenContrail API server.

%files -n python-contrail
%{python_sitelib}/cfgm_common*
%{python_sitelib}/libpartition*
%{python_sitelib}/pysandesh*
%{python_sitelib}/sandesh-0.1*dev*
%{python_sitelib}/sandesh_common*
%{python_sitelib}/vnc_api*
%{python_sitelib}/contrail_api_client*
%{python_sitelib}/ContrailCli*
%config(noreplace) %{_contrailetc}/vnc_api_lib.ini
/etc/bash_completion.d/bashrc_contrail_cli

%package vrouter-utils
Summary:            Contrail vRouter

Group:              Applications/System

Requires:           tcpdump

%description vrouter-utils
Contrail Virtual Router utils package

The OpenContrail vRouter is a forwarding plane (of a distributed router)that
runs in the hypervisor of a virtualized server.

The package opencontrail-vrouter-utils provides command line utilities to
configure and diagnose the OpenContrail Linux kernel module.

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
Requires:           python-paramiko
Requires:           python2-passlib

%description vrouter-agent
Contrail Virtual Router Agent package

OpenContrail is a network virtualization solution that provides an overlay
virtual-network to virtual-machines, containers or network namespaces. This
package provides the contrail-vrouter user space agent.

%files vrouter-agent
%defattr(-, root, root)
%{_bindir}/contrail-vrouter-agent*
%{_bindir}/contrail-tor-agent*
%{_bindir}/vrouter-port-control
%{_bindir}/contrail-compute-setup
%{_bindir}/contrail-toragent-setup
%{_bindir}/contrail-toragent-cleanup
%{_bindir}/contrail-vrouter-agent-health-check.py
%{_bindir}/contrail_crypt_tunnel_client.py
%{python_sitelib}/contrail_vrouter_provisioning*
%{python_sitelib}/ContrailVrouterCli*

%pre vrouter-agent
set -e
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post vrouter-agent
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
mkdir -p /var/lib/contrail/dhcp/
mkdir -p /var/lib/contrail/backup
mkdir -p /etc/contrail/ssl/certs/ /etc/contrail/ssl/private/
chown contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/ /etc/contrail/ssl/
chown -R contrail:contrail /etc/contrail/ssl/certs/ /etc/contrail/ssl/private/
chmod 0750 /etc/contrail/ /etc/contrail/ssl/ /etc/contrail/ssl/certs/
chmod 0700 /etc/contrail/ssl/private/
chmod 0750 /var/lib/contrail/dhcp/
chmod 0750 /var/lib/contrail/backup/

%package control
Summary:          Contrail Control
Group:            Applications/System

Requires:         contrail-lib >= %{_verstr}-%{_relstr}
Requires:         authbind

%description control
Contrail Control package

Control nodes implement the logically centralized portion of the control plane.
Not all control plane functions are logically centralized \u2013 some control
plane functions are still implemented in a distributed fashion on the physical
and virtual routers and switches in the network.

The control nodes use the IF-MAP protocol to monitor the contents of the
low-level technology data model as computed by the configuration nodes
thatdescribes the desired state of the network. The control nodes use a
combination of south-bound protocols to \u201cmake it so\u201d, i.e. to make
the actual state of the network equal to the desired state of the network.

In the initial version of the OpenContrail System these south-bound protocols
include Extensible Messaging and Presence Protocol (XMPP)to control the
OpenContrail vRouters as well as a combination of the Border Gateway Protocol
(BGP) and the Network Configuration (Netconf) protocols to control physical
routers. The control nodes also use BGP for state synchronization amongst each
other when there are multiple instances of the control node for scale-out and
high-availability reasons.

Control nodes implement a logically centralized control plane that is
responsible for maintaining ephemeral network state. Control nodes interact
with each other and with network elements to ensure that network state is
eventually consistent.

%files control
%defattr(-,root,root,-)
%{_bindir}/contrail-control*
%{python_sitelib}/ContrailControlCli*

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

%package -n python-opencontrail-vrouter-netns

Summary:            OpenContrail vRouter netns

Group:              Applications/System

%if 0%{?rhel} > 6
Requires:           python-websocket-client >= 0.32.0
Requires:           python2-docker
%else
Requires:           python-docker-py
%endif

Requires:           python-unittest2
Requires:           iproute >= 3.1.0
Requires:           python-requests >= 2.5.1
Requires:           python-eventlet < 0.19.0
Requires:           python-enum34
Requires:           python-keystoneclient
Requires:           python-barbicanclient
Requires:           python-pyOpenSSL

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
Obsoletes:          contrail-libs <= 0.0.1

%description lib
Libraries used by the Contrail Virtual Router.

%files lib
%defattr(-,root,root)
%{_libdir}/../lib/lib*.so*

%package config
Summary: Contrail Config
Group:              Applications/System

BuildArch: noarch
Requires:           python-contrail >= %{_verstr}-%{_relstr}
Requires:           python-bitarray >= 0.8.0
%if 0%{?rhel} >= 7
Requires: python-gevent >= 1.0
%endif
%if 0%{?rhel} <= 6
Requires:          python-gevent
%endif
Requires:           python-geventhttpclient
Requires:           python-lxml >= 2.3.2
Requires:           python-pycassa
Requires:           python-thrift >= 0.9.1
Requires:           python-psutil >= 0.6.0
Requires:           python-requests
Requires:           python-zope-interface
Requires:           xmltodict >= 0.7.0
Requires:           python-jsonpickle
Requires:           python-amqp
Requires:           python-kazoo >= 2.3.0
Requires:           python-ncclient >= 0.3.2
Requires:           ansible < 2.5.0
%if 0%{?rhel}
Requires:           python-pysnmp
%else
Requires:           python2-pysnmp
%endif
Requires:           python-keystoneclient
Requires:           python-keystonemiddleware
Requires:           python-swiftclient
Requires:           python2-jmespath
Requires:           python-subprocess32 >= 3.2.6
Requires:           python2-jsonschema >= 2.5.1
Requires:           openssh-clients
Requires:           python-attrdict
Requires:           python-pyhash
%if 0%{?rhel} > 6
Requires:           python2-docker
%else
Requires:           python-docker-py
%endif

%description config
Contrail Config package

Configuration nodes are responsible for the management layer. The configuration
nodes provide a north-bound Representational State Transfer (REST) Application
Programming Interface (API) that can be used to configure the system or extract
operational status of the system. The instantiated services are represented by
objects in a horizontally scalable database that is described by a formal
service data model (more about data models later on).

The configuration nodes also contain a transformation engine (sometimes
referred to as a compiler) that transforms the objects in the high-level
service data model into corresponding more lower-level objects in the
technology data model. Whereas the high-level service data model describes what
services need to be implemented, the low-level technology data model describes
how those services need to be implemented.

The configuration nodes publish the contents of the low-level technology data
model to the control nodes using the Interface for Metadata Access Points
(IF-MAP) protocol. Configuration nodes keep a persistent copy of the intended
configuration state and translate the high-level data model into the lower
level model suitable for interacting with network elements. Both these are kept
in a NoSQL database.

%files config
%defattr(-,contrail,contrail,-)
%defattr(-,root,root,-)
%{_bindir}/contrail-api*
%{_bindir}/contrail-schema*
%{_bindir}/contrail-device-manager*
%{_bindir}/contrail-issu-pre-sync
%{_bindir}/contrail-issu-post-sync
%{_bindir}/contrail-issu-run-sync
%{_bindir}/contrail-issu-zk-sync
%{_fabricansible}/*.tar.gz
%{python_sitelib}/schema_transformer*
%{python_sitelib}/vnc_cfg_api_server*
%{python_sitelib}/contrail_api_server*
%{python_sitelib}/ContrailConfigCli*
%{python_sitelib}/device_manager*
%{python_sitelib}/job_manager*
%{python_sitelib}/device_api*
%{python_sitelib}/abstract_device_api*
%{python_sitelib}/contrail_issu*
%if 0%{?rhel} > 6
%docdir /usr/share/doc/contrail-config/
/usr/share/doc/contrail-config/
%endif

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
tar -xvzf %{_fabricansible}/*.tar.gz -C %{_fabricansible}
mv %{_fabricansible}/fabric_ansible_playbooks-0.1dev/* %{_fabricansible}/
rmdir  %{_fabricansible}/fabric_ansible_playbooks-0.1dev/
cat %{_fabricansible}/ansible.cfg > /etc/ansible/ansible.cfg

%package analytics
Summary:            Contrail Analytics
Group:              Applications/System

Requires:           xmltodict >= 0.7.0
Requires:           contrail-lib >= %{_verstr}-%{_relstr}
Requires:           python-pycassa
Requires:           python-redis >= 2.10.0
Requires:           redis >= 2.6.13-1
Requires:           python-contrail >= %{_verstr}-%{_relstr}
Requires:           python-psutil >= 0.6.0
Requires:           python-prettytable
Requires:           python-geventhttpclient
Requires:           protobuf
Requires:           cassandra-cpp-driver
Requires:           libzookeeper
Requires:           net-snmp-python
Requires:           librdkafka1 < 0.11.5
Requires:           python-kafka >= 1.0.1
Requires:           python-stevedore
Requires:           python-kazoo >= 2.3.0
Requires:           python-sseclient
Requires:           python-amqp
Requires:           grok
%if 0%{?rhel} >= 7
Requires:           python-cassandra-driver >= 3.0.0
%endif

%description analytics
Contrail Analytics package
Analytics nodes are responsible for collecting, collating and presenting
analytics information for trouble shooting problems and for understanding
network usage. Each component of the OpenContrail System generates detailed
event records for every significant event in the system. These event records
are sent to one of multiple instances (for scale-out) of the analytics node
that collate and store the information in a horizontally scalable database
using a format that is optimized for time-series analysis and queries. the
analytics nodes have mechanism to automatically trigger the collection of more
detailed records when certain event occur; the goal is to be able to get to the
root cause of any issue without having to reproduce it. The analytics nodes
provide a north-bound analytics query REST API. Analytics nodes collect, store,
correlate, and analyze information from network elements, virtual or physical.
This information includes statistics,logs, events, and errors.

%files analytics
# Setup directories
%defattr(-,contrail,contrail,)
%defattr(-, root, root)
%{_bindir}/contrail-collector*
%{_bindir}/contrail-query-engine*
%{_bindir}/contrail-analytics-api*
%{_bindir}/contrail-alarm-gen*
%{python_sitelib}/opserver*
%{python_sitelib}/contrail_snmp_collector*
%{python_sitelib}/contrail_topology*
%{python_sitelib}/ContrailAnalyticsCli*
%{_bindir}/contrail-logs
%{_bindir}/contrail-flows
%{_bindir}/contrail-sessions
%{_bindir}/contrail-db
%{_bindir}/contrail-stats
%{_bindir}/contrail-alarm-notify
%{_bindir}/contrail-logs-api-audit
%{_bindir}/contrail-snmp-*
%{_bindir}/contrail-topology
/usr/share/doc/contrail-analytics-api
/usr/share/mibs/netsnmp
/etc/contrail/snmp.conf

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
DNS provides contrail-dns, contrail-named, contrail-rndc and
contrail-rndc-confgen daemons
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
mkdir -p /var/log/contrail /etc/contrail/dns
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
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
%config(noreplace) %{_contraildns}/applynamedconfig.py
%{_contraildns}/COPYRIGHT
%defattr(-, root, root)
%{_bindir}/contrail-named*
%{_bindir}/contrail-rndc
%{_bindir}/contrail-rndc-confgen
%{_bindir}/contrail-dns*
%if 0%{?rhel} > 6
%docdir %{python2_sitelib}/doc/*
%endif

%package nova-vif
Summary:            Contrail nova vif driver
Group:              Applications/System

%description nova-vif
Contrail Nova Vif driver package

%files nova-vif
%defattr(-,root,root,-)
%{python_sitelib}/nova_contrail_vif*
%{python_sitelib}/vif_plug_vrouter
%{python_sitelib}/vif_plug_contrail_vrouter

%package utils
Summary: Contrail utility sctipts.
Group: Applications/System

Requires:           lsof
Requires:           python-lxml >= 2.3.2
Requires:           python-requests
Requires:           python-contrail >= %{_verstr}-%{_relstr}

%description utils
Contrail utility sctipts package

%files -f %{buildroot}/contrail-utils-bin-includes.txt utils
%defattr(-, root, root)
/usr/share/contrail-utils/*

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

%package fabric-utils
Summary: Contrail Fabric Utilities
Group: Applications/System
Requires: python-yaml
Requires: python-Fabric
Requires: python-netaddr

%description fabric-utils
Contrail Fabric Utilities for cluster management

%files fabric-utils
%defattr(-, root, root)
%{python_sitelib}/contrail_fabric_utils
%{python_sitelib}/contrail_fabric_utils-*.egg-info
%doc %{_contrailutils}/README.fabric
%{_contrailutils}/fabfile

%package test
Summary: Contrail Test
Group: Applications/System

%description test
Source code of Contrail Test and Test CI

%files test
%defattr(-, root, root)
/contrail-test

%package kube-manager
Summary:            Kubernetes network manager

Group:              Applications/System

Requires:    python-contrail >= %{_verstr}-%{_relstr}
Requires:    python-gevent
Requires:    python-requests

%description kube-manager
Contrail kubernetes network manager package
This package contains the kubernetes network management modules.
%files kube-manager
%{python_sitelib}/kube_manager*
%{_bindir}/contrail-kube-manager

%pre kube-manager
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post kube-manager
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

%package mesos-manager
Summary:            Mesos network manager

Group:              Applications/System

Requires:           python-contrail >= %{_verstr}-%{_relstr}
Requires:           python-gevent
Requires:           python-requests

%description mesos-manager
Contrail Mesos network manager package
This package contains the mesos network management modules.
%files mesos-manager
%{python_sitelib}/mesos_manager*
%{_bindir}/contrail-mesos-manager

%pre mesos-manager
set -e
# Create the "contrail" user
getent group contrail >/dev/null || groupadd -r contrail
getent passwd contrail >/dev/null || \
  useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
  -c "OpenContail daemon" contrail

%post mesos-manager
set -e
mkdir -p /var/log/contrail /var/lib/contrail/ /etc/contrail/
chown -R contrail:adm /var/log/contrail
chmod 0750 /var/log/contrail
chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
chmod 0750 /etc/contrail/

%package kube-cni
Summary:            Kubernetes cni plugin

Group:              Applications/System

%description kube-cni
Contrail kubernetes cni plugin package
This package contains the kubernetes cni plugin modules.
%files kube-cni
%{python_sitelib}/kube_cni*
%{_bindir}/contrail-kube-cni

%package cni
Summary:            Mesos/Kubernetes cni plugin

Group:              Applications/System

%description cni
Contrail mesos/kubernetes cni plugin package
This package contains the mesos/kubernetes cni plugin modules.
%files cni
%{python_sitelib}/cni*
%{_bindir}/contrail-cni

%package k8s-cni
Summary:            Kubernetes cni plugin

Group:              Applications/System

%description k8s-cni
Contrail kubernetes cni plugin package
This package contains the kubernetes cni plugin modules.
%files k8s-cni
%{_bindir}/contrail-k8s-cni

%package mesos-cni
Summary:            Mesos cni plugin

Group:              Applications/System

%description mesos-cni
Contrail mesos cni plugin package
This package contains the mesos cni plugin modules.
%files mesos-cni
%{_bindir}/contrail-mesos-cni

%if 0%{?_manifestFile:1}

%package manifest
BuildArch:          noarch
Summary:            Android repo manifest.xml

Group:              Applications/System

%description manifest
Manifest.xml
Used for Android repo code checkout of OpenContrail

%files manifest
/opt/contrail/manifest.xml

%endif
