%define         _distropkgdir %{_sbtop}tools/packaging/rpm/%{name}
%define         _nodemgr_config %{_sbtop}controller/src/nodemgr/vrouter_nodemgr

%define         _sku     %{_skuTag}
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
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack vRouter %{?_gitVer}
Name: contrail-openstack-vrouter
Version:	    %{_verstr}

Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net/
Vendor:         Juniper Networks Inc

BuildArch: noarch

Requires: contrail-vrouter-common >= %{_verstr}-%{_relstr}

# contrail-nova-vif not required from Kilo onwards
%if %{_skuTag} == "juno"
Requires: contrail-nova-vif >= %{_verstr}-%{_relstr}
%endif

Requires: openstack-nova-compute
Requires: openstack-utils

%description
Contrail Package Requirements for Contrail Openstack vRouter

%install
install -d -m 755 %{buildroot}/etc/contrail
install -d -m 755 %{buildroot}/etc/init.d
pushd %{_sbtop}
install -D -m 755 %{_nodemgr_config}/contrail-vrouter-nodemgr.conf %{buildroot}/etc/contrail/contrail-vrouter-nodemgr.conf
install -D -m 755 %{_nodemgr_config}/contrail-vrouter-nodemgr.initd.supervisord %{buildroot}/etc/init.d/contrail-vrouter-nodemgr

%post

%preun

%postun

%files
%config(noreplace) /etc/contrail/contrail-vrouter-nodemgr.conf
/etc/init.d/contrail-vrouter-nodemgr

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

