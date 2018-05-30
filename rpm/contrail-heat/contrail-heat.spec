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

Name:        contrail-heat
Version:    %{_verstr}
Release:    %{_relstr}%{?dist}
Summary:    Contrail Heat Resources and Templates%{?_gitVer}

Group:      Applications/System
License:    Commercial
URL:        http://www.juniper.net/
Vendor:     Juniper Networks Inc

BuildArch: noarch
BuildRequires: python-setuptools

%description
Contrail Heat Resources and Templates package

%prep

%build

%install
pushd %{_sbtop}/openstack/contrail-heat
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/contrail_heat*

%post
