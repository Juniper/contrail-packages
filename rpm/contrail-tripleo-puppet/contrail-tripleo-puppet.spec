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

%define         _installdir  /usr/share/contrail-tripleo-puppet/

%{echo: "Building release %{_relstr}\n"}

Name:           contrail-tripleo-puppet
Version:        %{_verstr}
Release:        %{_relstr}%{?dist}
Summary:        contrail tripleo puppet modules for tripleo composable roles deployment%{?_gitVer}
Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net
Vendor:         Juniper Networks Inc

BuildArch:      noarch
    
%description
Contrail tripleo puppet modules for tripleo composable roles deployment
    
%install
rm -rf %{buildroot}%{_installdir}
install -d -m 0755 %{buildroot}%{_installdir}
cp -rp  %{_sbtop}openstack/contrail-tripleo-puppet/* %{buildroot}%{_installdir}

%files
%defattr(-, root, root)
%{_installdir}*

%changelog

