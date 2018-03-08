%define         _contrailetc /etc/contrail
%define         _contrailanalytics /opt/contrail/analytics
%define         _contrailutils /opt/contrail/utils
%define         _supervisordir /etc/contrail/supervisord_analytics_files
%define         _distropkgdir %{_sbtop}tools/packages/common/control_files
%define         _nodemgr_config %{_sbtop}controller/src/nodemgr/analytics_nodemgr

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
Name:           contrail-openstack-analytics
Summary:        Contrail Openstack Analytics %{?_gitVer}
Version:	    %{_verstr}
Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net/
Vendor:         Juniper Networks Inc

BuildArch:      noarch

Requires:       contrail-analytics >= %{_verstr}-%{_relstr}
Requires:       contrail-setup >= %{_verstr}-%{_relstr}
Requires:       contrail-utils >= %{_verstr}-%{_relstr}
Requires:       contrail-nodemgr >= %{_verstr}-%{_relstr}
Requires:       python-contrail >= %{_verstr}-%{_relstr}
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       python-importlib
%endif

%description
Contrail Package Requirements for Analytics

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailanalytics}
install -d -m 755 %{buildroot}%{_supervisordir}
install -d -m 755 %{buildroot}%{_initddir}

#install wrapper scripts for supervisord
pushd %{_builddir}/..
#install .ini files for supervisord
install -p -m 755 %{_nodemgr_config}/contrail-analytics-nodemgr.ini %{buildroot}%{_supervisordir}/contrail-analytics-nodemgr.ini
install -D -m 755 %{_nodemgr_config}/contrail-analytics-nodemgr.conf %{buildroot}/etc/contrail/contrail-analytics-nodemgr.conf
install -D -m 755 %{_nodemgr_config}/contrail-analytics-nodemgr.initd.supervisord %{buildroot}/etc/init.d/contrail-analytics-nodemgr

for f in $(find %{buildroot} -type f -exec grep -l '^#!%{__python}' {} \; ); do
    sed 's/^#!.*python/#!\/usr\/bin\/python/g' $f > ${f}.b
    mv ${f}.b ${f}
done

%post

%files
%defattr(-, root, root)
%config(noreplace) %{_supervisordir}/contrail-analytics-nodemgr.ini
%config(noreplace) /etc/contrail/contrail-analytics-nodemgr.conf
/etc/init.d/contrail-analytics-nodemgr

%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.
