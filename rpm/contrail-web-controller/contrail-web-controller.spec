%define    _contrailwebsrc   /usr/src/contrail/contrail-web-controller

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

Name:    contrail-web-controller
Version:  %{_verstr}
Release:  %{_relstr}
Summary:  Contrail Web UI %{?_gitVer}

Group:      Applications/System
License:    Commercial
URL:        http://www.juniper.net/
Vendor:     Juniper Networks Inc

BuildRequires:  nodejs = 0.10.48-1contrail.el7
Requires:  redis
Requires:  contrail-web-core >= %{_verstr}-%{_relstr}

Obsoletes:  contrail-webui >= 0

Source:    %{name}

%description
Contrail Web UI package

%prep
command -v node >/dev/null 2>&1 || {
    command -v nodejs >/dev/null 2>&1 || {
        echo >&2 "contrail-web-controller build requires node/nodejs.  Aborting.";
        exit 1;
    }
}
command -v npm >/dev/null 2>&1 || {
    echo >&2 "contrail-web-core UT requires npm. Aborting.";
    exit 1;
}

%build
pushd %{_sbtop}contrail-web-core
make package REPO=../contrail-web-controller,webController

%install
mkdir -p %{buildroot}%{_contrailwebsrc}

pushd %{_sbtop}
cp -rp contrail-web-controller/* %{buildroot}%{_contrailwebsrc}/
ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_contrailwebsrc}/*

%post
%if 0%{?rhel}
%else
/bin/systemctl daemon-reload
%endif

%preun
if [ $1 = 1 ] ; then 
  echo "Upgrading contrail-web-controller Package"
elif [ $1 = 0 ] ; then
  echo "Removing contrail-web-controller Package"
fi
exit 0

%changelog
* Fri Oct 04 2019 - zsong@juniper.net
- Upgrade nodejs to 0.10.48
* Sun May 26 2013 - bmandal@juniper.net
- first release

