%define         _contrailetc /etc/contrail
%define         _contrailcontrol /opt/contrail/control-node
%define         _supervisordir /etc/contrail/supervisord_control_files
%define         _distropkgdir %{_sbtop}tools/packages/common/control_files
%define         _nodemgr_config %{_sbtop}controller/src/nodemgr/control_nodemgr

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack Control %{?_gitVer}
Name: contrail-openstack-control
Version:	    %{_verstr}
Group:              Applications/System
License:            Commercial
URL:                http://www.juniper.net/
Vendor:             Juniper Networks Inc

BuildArch: noarch

Requires: contrail-control >= %{_verstr}-%{_relstr}
Requires: contrail-lib >= %{_verstr}-%{_relstr}
Requires: contrail-dns >= %{_verstr}-%{_relstr}
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: contrail-nodemgr >= %{_verstr}-%{_relstr}
Requires: python-contrail >= %{_verstr}-%{_relstr}

%description
Contrail Package Requirements for Control Node

%install
# Setup directories
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailcontrol}
install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}/etc/init.d

pushd %{_builddir}/..

install -p -m 755 %{_nodemgr_config}/contrail-control-nodemgr.ini %{buildroot}%{_supervisordir}/contrail-control-nodemgr.ini
install -D -m 755 %{_nodemgr_config}/contrail-control-nodemgr.conf %{buildroot}/etc/contrail/contrail-control-nodemgr.conf
install -D -m 755 %{_nodemgr_config}/contrail-control-nodemgr.initd.supervisord %{buildroot}/etc/init.d/contrail-control-nodemgr

%files
%defattr(-,root,root,-)
%{_supervisordir}
%defattr(-,contrail,contrail,-)
%config(noreplace) %{_supervisordir}/contrail-control-nodemgr.ini
%config(noreplace) /etc/contrail/contrail-control-nodemgr.conf
/etc/init.d/contrail-control-nodemgr

%post
if [ -x /bin/systemctl ]; then
   /bin/systemctl --system daemon-reload
fi

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

