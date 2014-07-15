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
Summary:            Contrail %{?_gitVer}

Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

%description
Contrail package

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  systemd-units
BuildRequires:	gcc-c++
BuildRequires:	devtoolset-1.1-gcc
BuildRequires:	devtoolset-1.1-gcc-c++
BuildRequires:	openssl-devel
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
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
#Needed for vrouter-dkms
install -d -m 755 %{buildroot}/usr/src/vrouter-%{_verstr}
pushd %{buildroot}/usr/src/vrouter
find . -print | sed 's;^;'"%{buildroot}/usr/src/vrouter-%{_verstr}/"';'| xargs install -d -m 755
rm -rf %{buildroot}/usr/src/vrouter

#Install the remaining files in /usr/share to /opt/contrail/utils
pushd %{buildroot}/usr/share/contrail
find . -print | sed 's;^;'"%{buildroot}%{_contrailutils}"';'| xargs install -d -m 755

%package vrouter
Summary:            Contrail vRouter %{?_gitVer}
Group:              Applications/System

Requires: contrail-vrouter-agent
Requires: contrail-lib
Requires: xmltodict

%description vrouter
vrouter kernel module

%files vrouter
%defattr(-, root, root)
/lib/modules/*/extra/net/vrouter/vrouter.ko

%package vrouter-source
Summary:            Contrail vRouter %{?_gitVer}

Group:              Applications/System

%description vrouter-source
Contrail vrouter source package

%files vrouter-source
/usr/src/modules/contrail-vrouter

%package config-openstack
Summary:            Config openstack %{?_gitVer}

Group:              Applications/System

Requires:	    contrail-config
Requires:	    python-keystoneclient
Requires:	    python-novaclient

%description config-openstack
Contrail config openstack package

%files config-openstack
%{python_sitelib}/svc_monitor*
%{python_sitelib}/vnc_openstack*
%{_bindir}/contrail-svc-monitor
%{_contrailetc}/svc-monitor.conf
/usr/share/contrail

%package -n python-contrail-vrouter-api
Summary:            Contrail vrouter api  %{?_gitVer}

Group:              Applications/System

%description -n python-contrail-vrouter-api
Contrail Virtual Router apis package

%files -n python-contrail-vrouter-api
%{python_sitelib}/contrail_vrouter_api*

%package -n python-contrail
Summary:            Contrail Python Lib  %{?_gitVer}

Group:              Applications/System

%description -n python-contrail
Contrail Virtual Router utils package

%files -n python-contrail
%{python_sitelib}/cfgm_common*
%{python_sitelib}/discoveryclient*
%{python_sitelib}/pysandesh*
%{python_sitelib}/sandesh-0.1dev*
%{python_sitelib}/sandesh_common*
%{python_sitelib}/vnc_api*
%{_contrailetc}/vnc_api_lib.ini

%package vrouter-utils
Summary:            Contrail vRouter %{?_gitVer}

Group:              Applications/System

%description vrouter-utils
Contrail Virtual Router utils package

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

Summary:            Contrail vRouter %{?_gitVer}

Group:              Applications/System

Requires:           contrail-lib

%description vrouter-agent
Contrail Virtual Router Agent package

%files vrouter-agent
%defattr(-, root, root)
%{_bindir}/contrail-vrouter-agent
%{_contrailetc}/contrail-vrouter-agent.conf

%post vrouter-agent
set -e

if [ "$1" = "configure" ] || [ "$1" = "reconfigure" ] ; then

  if ! getent group contrail > /dev/null 2>&1
  then
    addgroup --system contrail >/dev/null
  fi

  if ! getent passwd contrail > /dev/null 2>&1
  then
    adduser --system --home /var/lib/contrail --ingroup contrail --no-create-home --shell /bin/false contrail
  fi

  mkdir -p /var/log/contrail
  chown -R contrail:adm /var/log/contrail
  chmod 0750 /var/log/contrail
  chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
  chmod 0750 /etc/contrail/

fi

%package control
Summary:          Contrail Control %{?_gitVer}
Group:            Applications/System

Requires:         contrail-lib

%description control
Contrail Control package

%files control
%defattr(-,root,root,-)
%{_bindir}/control-node
%config(noreplace) %{_contrailetc}/control-node.conf

%post control
set -e

if [ "$1" = "configure" ] || [ "$1" = "reconfigure" ] ; then

  if ! getent group contrail > /dev/null 2>&1
  then
    addgroup --system contrail >/dev/null
  fi

  if ! getent passwd contrail > /dev/null 2>&1
  then
    adduser --system --home /var/lib/contrail --ingroup contrail --no-create-home --shell /bin/false contrail
  fi

  mkdir -p /var/log/contrail
  chown -R contrail:adm /var/log/contrail
  chmod 0750 /var/log/contrail
  chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
  chmod 0750 /etc/contrail/

fi

%package python-contrail-vrouter-netns

Summary:            Contrail vRouter netns %{?_gitVer}

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

%description lib
Libraries used by the Contrail Virtual Router.

%files lib
%defattr(-,root,root)
%{_libdir}/../lib/lib*.so*

%package config
Summary: Contrail Config %{?_gitVer}
Group:              Applications/System

BuildArch: noarch
Requires: python-contrail
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
Requires: irond
Requires: xmltodict >= 0.1
Requires: python-jsonpickle

%description config
Contrail Config package

%files config
%defattr(-,root,root,-)
%{_bindir}/contrail-api
%{_bindir}/contrail-schema
%{_bindir}/discovery-server
%{_bindir}/ifmap-view
%config(noreplace) %{_sysconfdir}/contrail/contrail-api.conf
%config(noreplace) %{_sysconfdir}/contrail/contrail-schema.conf
%config(noreplace) %{_sysconfdir}/contrail/discovery.conf
%{python_sitelib}/discovery
%{python_sitelib}/discovery-*
%{python_sitelib}/schema_transformer*
%{python_sitelib}/vnc_cfg_api_server*
#/usr/share/doc/python-vnc_cfg_api_server
#%{_sysconfdir}/contrail
#%dir %attr(0777, root, root) %{_localstatedir}/log/contrail

%post config
set -e

if [ "$1" = "configure" ] || [ "$1" = "reconfigure" ] ; then

  if ! getent group contrail > /dev/null 2>&1
  then
    addgroup --system contrail >/dev/null
  fi

  if ! getent passwd contrail > /dev/null 2>&1
  then
    adduser --system --home /var/lib/contrail --ingroup contrail --no-create-home --shell /bin/false contrail
  fi

  mkdir -p /var/log/contrail
  chown -R contrail:adm /var/log/contrail
  chmod 0750 /var/log/contrail
  chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
  chmod 0750 /etc/contrail/

fi


%package analytics
Summary:            Contrail Analytics %{?_gitVer}
Group:              Applications/System

Requires:           xmltodict
Requires:           contrail-lib
Requires:           pycassa
Requires:	    redis-py
Requires:	    redis >= 2.6.13-1 
Requires:	    python-contrail
Requires:	    python-psutil
Requires:	    python-prettytable
Requires:	    python-geventhttpclient
Requires:	    protobuf

%description analytics
Contrail Analytics package

%files analytics
# Setup directories
%defattr(-, root, root)
%{_bindir}/contrail-collector
%{_bindir}/contrail-query-engine
%{_bindir}/contrail-analytics-api
%{python_sitelib}/opserver*
%config(noreplace) %{_contrailetc}/contrail-collector.conf
%config(noreplace) %{_contrailetc}/contrail-analytics-api.conf
%config(noreplace) %{_contrailetc}/contrail-query-engine.conf
%{_bindir}/contrail-logs
%{_bindir}/contrail-flows
%{_bindir}/contrail-stats

%post analytics
set -e

if [ "$1" = "configure" ] || [ "$1" = "reconfigure" ] ; then

  if ! getent group contrail > /dev/null 2>&1
  then
    addgroup --system contrail >/dev/null
  fi

  if ! getent passwd contrail > /dev/null 2>&1
  then
    adduser --system --home /var/lib/contrail --ingroup contrail --no-create-home --shell /bin/false contrail
  fi

  mkdir -p /var/log/contrail
  chown -R contrail:adm /var/log/contrail
  chmod 0750 /var/log/contrail
  chown -R contrail:contrail /var/lib/contrail/ /etc/contrail/
  chmod 0750 /etc/contrail/

fi

%package dns 
Summary:            Contrail Dns %{?_gitVer}
Group:              Applications/System

%description dns 
Contrail dns  package

%post dns
set -e

if [ "$1" = "configure" ]; then

  # Create the "contrail" user
  if ! getent passwd contrail > /dev/null 2>&1
  then
    adduser --quiet --system --group --home /var/lib/contrail \
      --no-create-home \
      --shell /bin/false \
      --gecos "OpenContrail daemon" contrail
  fi

  # Create the "contrail" group if it is missing and set the primary group
  # of the "contrail" user to this group.
  if ! getent group contrail > /dev/null 2>&1
  then
    addgroup --quiet --system contrail
    usermod -g contrail contrail
  fi

  mkdir -p /var/log/named
  chown -R contrail:adm /var/log/named
  chmod 0750 /var/log/named
  chown -R contrail. /etc/contrail/dns
  chmod 0750 /etc/contrail/dns

  # Use authbind to bind amed on a reserved port,
  # with contrail user privileges
  touch /etc/authbind/byport/53
  chown contrail. /etc/authbind/byport/53
  chmod 0755 /etc/authbind/byport/53

fi

%files dns 
%defattr(-, root, root)
%{_bindir}/named
%{_bindir}/rndc
%{_bindir}/dnsd
%{_contraildns}
%{_contraildns}/named.conf
%{_contraildns}/rndc.conf
%{_contraildns}/dns.conf

%package nova-vif 
Summary:            Contrail nova vif driver %{?_gitVer}
Group:              Applications/System

%description nova-vif 
Contrail Nova Vif driver package

%files nova-vif
%defattr(-,root,root,-)
%{python_sitelib}/nova_contrail_vif*

