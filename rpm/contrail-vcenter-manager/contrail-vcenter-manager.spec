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

Name:		  contrail-vcenter-manager
Version:	  %{_verstr}
Release:	  %{_relstr}%{?dist}
Summary:	  Contrail vCenter Manager

Group:      Applications/System
License:    Commercial
URL:        http://www.juniper.net/
Vendor:     Juniper Networks Inc

BuildArch: noarch
BuildRequires: python-setuptools

Requires: python-contrail-vrouter-api
Requires: python-contrail
Requires: python-gevent
Requires: PyYAML
Requires: python2-pyvmomi
Requires: python-ipaddress

%description
Contrail vCenter Manager package

%install
pushd %{_sbtop}/vcenter-manager
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/cvm*
%{python_sitelib}/contrail_vcenter_manager*
%exclude %{python_sitelib}/tests*

%post
