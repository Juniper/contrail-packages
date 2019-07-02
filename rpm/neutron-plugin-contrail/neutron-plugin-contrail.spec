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

Name:        neutron-plugin-contrail
Version:      %{_verstr}
Release:      %{_relstr}%{?dist}
Summary:      Contrail Neutron Plugin and Extensions%{?_gitVer}

Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net/
Vendor:         Juniper Networks Inc

BuildArch: noarch

%description
Contrail Neutron Plugin and Extensions package

%prep

%build

%install
pushd %{_sbtop}openstack/neutron_plugin
%{__python} setup.py install --root=%{buildroot}
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/plugins/contrail
install -p -m 755 etc/neutron/plugins/contrail/contrail_conf.ini %{buildroot}/etc/neutron/plugins/contrail/contrail_conf.ini
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/networking_contrail*
%config(noreplace) %{_sysconfdir}/neutron

%post
rm -rf /etc/neutron/plugin.ini
ln -sf /etc/neutron/plugins/contrail/contrail_conf.ini /etc/neutron/plugin.ini
