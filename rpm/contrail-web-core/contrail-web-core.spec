%define     _distropkgdir       %{_sbtop}tools/packages/rpm/%{name}
%define    _contrailetc     /etc/contrail
%define    _contrailwebsrc   /usr/src/contrail/contrail-web-core
%if 0%{?fedora} >= 17
%define    _servicedir      %{_libdir}/systemd/system
%endif
%define    _nodemodules    node_modules/
%define    _config          %{_sbtop}contrail-web-core/config
%define    _contrailuitoolsdir  src/tools
%define    _websslpath        /etc/pki/ca-trust/source/anchors/contrail_webui_ssl/
%define    _sslsub          /C=US/ST=CA/L=Sunnyvale/O=JuniperNetworks/OU=JuniperCA/CN=ContrailCA

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

Name:    contrail-web-core
Version:  %{_verstr}
Release:  %{_relstr}
Summary:  Contrail Web UI %{?_gitVer}

Group:     Applications/System
License:   Commercial
URL:       http://www.juniper.net/
Vendor:    Juniper Networks Inc

Requires:  redis
BuildRequires:  nodejs >= nodejs-0.10.35-1contrail
Requires:  nodejs >= nodejs-0.10.35-1contrail
Requires:  openssl

Obsoletes:  contrail-webui >= 0

Source:    %{name}

%description
Contrail Web UI package

%prep
command -v node >/dev/null 2>&1 || {
    command -v nodejs >/dev/null 2>&1 || {
        echo >&2 "contrail-web-core build requires node/nodejs.  Aborting.";
        exit 1;
    }
}
command -v npm >/dev/null 2>&1 || {
    echo >&2 "contrail-web-core UT requires npm. Aborting.";
    exit 1;
}

%build
pushd %{_sbtop}contrail-web-core
make package REPO=../contrail-web-core

%install
rm -rf %{buildroot}%{_contrailwebsrc}
%if 0%{?fedora} >= 17
rm -rf %{buildroot}%{_servicedir}
%endif
%if 0%{?rhel}
install -d -m 755 %{buildroot}%{_initddir}
%endif
rm -rf %{buildroot}%{_libdir}/node_modules
rm -rf %{buildroot}%{_contrailetc}

mkdir -p %{buildroot}%{_contrailwebsrc}
%if 0%{?fedora} >= 17
mkdir -p %{buildroot}%{_servicedir}
%endif
mkdir -p %{buildroot}%{_libdir}/node_modules
mkdir -p %{buildroot}%{_contrailetc}

pushd %{_sbtop}
cp -r -p contrail-web-core/* %{buildroot}%{_contrailwebsrc}/

install -p -m 755 %{_distropkgdir}/contrailWebServer.sh %{buildroot}%{_contrailwebsrc}/
install -p -m 755 %{_distropkgdir}/contrailWebMiddleware.sh %{buildroot}%{_contrailwebsrc}/
cp -r -p %{buildroot}%{_contrailwebsrc}/%{_nodemodules}/* %{buildroot}%{_libdir}/node_modules
rm -rf  %{buildroot}%{_contrailwebsrc}/node_modules
ln -s %{_libdir}/node_modules %{buildroot}%{_contrailwebsrc}/node_modules
rm %{buildroot}%{_contrailwebsrc}/config/config.global.js
cp -p %{_config}/config.global.js %{buildroot}%{_contrailetc}/
ln -s %{_contrailetc}/config.global.js %{buildroot}%{_contrailwebsrc}/config/config.global.js
perl -pi -e '{ s/opencontrail-logo/juniper-networks-logo/g; }' %{buildroot}%{_contrailetc}/config.global.js
perl -pi -e '{ s/opencontrail-favicon/juniper-networks-favicon/g; }' %{buildroot}%{_contrailetc}/config.global.js
rm %{buildroot}%{_contrailwebsrc}/config/userAuth.js
cp -p %{_config}/userAuth.js %{buildroot}%{_contrailetc}/contrail-webui-userauth.js
ln -s %{_contrailetc}/contrail-webui-userauth.js %{buildroot}%{_contrailwebsrc}/config/userAuth.js

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_contrailwebsrc}/*
%if 0%{?fedora} >= 17
%{_servicedir}/*
%endif
%if 0%{?rhel}
%{_initddir}/*
%endif
%{_libdir}/*
%config(noreplace) %{_contrailetc}/config.global.js
%config(noreplace) %{_contrailetc}/contrail-webui-userauth.js

%pre
if [ ! -e %{_websslpath} ]; then
  mkdir -p %{_websslpath}
  openssl req -new -newkey rsa:2048 -nodes -out %{_websslpath}/certrequest.csr -keyout %{_websslpath}/cs-key.pem -subj %{_sslsub}
  openssl x509 -req -days 730 -in %{_websslpath}/certrequest.csr -signkey %{_websslpath}/cs-key.pem -out %{_websslpath}/cs-cert.pem
fi

%post
%if 0%{?rhel}
%else
/bin/systemctl daemon-reload
%endif

%preun
if [ $1 = 1 ] ; then 
  echo "Upgrading contrail-webui Package"
elif [ $1 = 0 ] ; then
  echo "Removing contrail-webui Package"
fi
exit 0

%changelog
* Wed Jan 30 2013 - bmandal@contrailsystems.com
- Added log file in package.
* Fri Jan 18 2013 - bmandal@contrailsystems.com
- first release

