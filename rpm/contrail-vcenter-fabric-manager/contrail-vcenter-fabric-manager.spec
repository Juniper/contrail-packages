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

Name:       contrail-vcenter-fabric-manager
Version:    %{_verstr}
Release:    %{_relstr}%{?dist}
Summary:    Contrail vCenter Fabric Manager

Group:      Applications/System
License:    Commercial
URL:        http://www.juniper.net/
Vendor:     Juniper Networks Inc

BuildArch: noarch
BuildRequires: python-setuptools
BuildRequires: scons

Requires: python-contrail
Requires: python-gevent
<<<<<<< HEAD   (1fdf79 Adding kafka-python version change fix, made for master AND )
Requires: PyYAML
Requires: python2-pyvmomi
=======
Requires: python2-pyvmomi = 6.5-1.el7
>>>>>>> CHANGE (12ae43 Pin some packages to not break build by new packages uploade)
Requires: python-kazoo
Requires: python-bitarray
Requires: python-pycassa
Requires: python-attrdict

%description
Contrail vCenter Fabric Manager package

%prep

%build

%install
pushd %{_sbtop}
scons --opt=%{_sconsOpt} --root=%{buildroot} cvfm-install
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/cvfm*
%{python_sitelib}/contrail_vcenter_fabric_manager*
%exclude %{python_sitelib}/tests*

%post
mkdir -p /etc/contrail/contrail-vcenter-fabric-manager
