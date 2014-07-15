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

Name:               ifmap-python-client
Version:            0.3.2
Release:            %{_relstr}%{?dist}
Summary:            Contrail nova vif driver %{?_gitVer}

Group:              Applications/System
License:            Commercial
#URL:                http://trust.f4.hs-hannover.de
Vendor:             Juniper Networks Inc
Source0:            https://github.com/ITI/ifmap-python-client/archive/master.zip 
Patch0:            001_contrail_third_party.patch 
Patch1:            002_handle-hostname-validation.patch
Patch2:            003_ifmap_client_concurrency.patch
BuildArch: noarch
%description
ifmap python client for contrail
%prep
%setup -n ifmap-python-client-master
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
pushd %{_builddir}
pushd 
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/ifmap*
