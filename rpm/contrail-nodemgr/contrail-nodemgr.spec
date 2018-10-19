%define         _contrailetc /etc/contrail
%define         _contrailcontrol /opt/contrail/control-node
%define         _distropkgdir %{_sbtop}tools/packages/rpm/%{name}

%if 0%{?fedora} >= 17
%define         _servicedir  %{_libdir}/systemd/system
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

%if 0%{?_opt:1}
%define         _sconsOpt      %{_opt}
%else
%define         _sconsOpt      debug
%endif

%bcond_without debuginfo

Name:             contrail-nodemgr
Version:          %{_verstr}
Release:          %{_relstr}%{?dist}
Summary:          Contrail Nodemgr %{?_gitVer}

Group:            Applications/System
License:          Commercial
URL:              http://www.juniper.net/
Vendor:           Juniper Networks Inc

Requires:         contrail-lib >= %{_verstr}-%{_relstr}
Requires:         xmltodict >= 0.7.0
Requires:        python-bottle >= 0.11.6
Requires:        python-contrail >= %{_verstr}-%{_relstr}
Requires:        ntp
Requires:         python-psutil
Requires:         PyYAML
Requires:        python2-pyroute2 >= 0.4.21

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:         python-importlib
%endif

BuildRequires: bison
BuildRequires: boost-devel
BuildRequires: flex
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: python2-pip

%description
Contrail Nodemgr package

%if %{with debuginfo}
%debug_package
%endif

%prep

%build
pushd %{_sbtop}/controller
scons --opt=%{_sconsOpt} -U control-node:node_mgr
scons --opt=%{_sconsOpt} -U vrouter:node_mgr
scons --opt=%{_sconsOpt} -U opserver:node_mgr
scons --opt=%{_sconsOpt} -U database:node_mgr
scons --opt=%{_sconsOpt} -U src:nodemgr

if [ $? -ne 0 ] ; then
  echo "build failed"
  exit -1
fi
popd

%install

# Setup directories

pushd %{_sbtop}

#install files
install -d -m 755 %{buildroot}%{_bindir}

# install pysandesh files
%define _build_dist %{_sbtop}/build/%{_sconsOpt}
install -d -m 755 %{buildroot}

popd
mkdir -p build/python_dist
pushd build/python_dist

tar zxf %{_build_dist}/control-node/dist/Control-Node-0.1dev.tar.gz
pushd Control-Node-0.1dev
%{__python} setup.py install --root=%{buildroot}
install -d -m 755 %{buildroot}/usr/share/doc/python-Control-Node
if [ -d doc ]; then
  cp -R doc/* %{buildroot}/usr/share/doc/python-Control-Node
fi
popd

tar zxf %{_build_dist}/vnsw/agent/uve/dist/vrouter-0.1dev.tar.gz
pushd vrouter-0.1dev
%{__python} setup.py install --root=%{buildroot}
install -d -m 755 %{buildroot}/usr/share/doc/python-vrouter
if [ -d doc ]; then
  cp -R doc/* %{buildroot}/usr/share/doc/python-vrouter
fi
popd

tar zxf %{_build_dist}/opserver/node_mgr/dist/node_mgr-0.1dev.tar.gz
pushd node_mgr-0.1dev
%{__python} setup.py install --root=%{buildroot}
popd

tar zxf %{_build_dist}/nodemgr/dist/nodemgr-0.1dev.tar.gz
pushd nodemgr-0.1dev
%{__python} setup.py install --root=%{buildroot}
popd

tar zxvf %{_build_dist}/analytics/database/dist/database-0.1dev.tar.gz
pushd database-0.1dev
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{_bindir}/contrail-nodemgr
%{python_sitelib}/Control_Node*
%{python_sitelib}/control_node*
%{python_sitelib}/vrouter
%{python_sitelib}/vrouter-*
%{python_sitelib}/node_mgr-*
%{python_sitelib}/database
%{python_sitelib}/database-*
%{python_sitelib}/analytics
%{python_sitelib}/nodemgr
%{python_sitelib}/nodemgr-*

%post
if [ -x /bin/systemctl ]; then
/bin/systemctl --system daemon-reload
fi

%changelog
