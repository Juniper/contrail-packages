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

%define         _build_dist        %{_sbtop}build/debug
%define         _contrailetc       /etc/contrail
%define         _binusr            /usr/bin/
%define         _ironic_notif_mgr  %{_sbtop}controller/src/config/ironic-notification-manager

Name:           ironic-notification-manager
Version:        %{_verstr}
Release:        %{_relstr}%{?dist}
Summary:        BMS Notfication daemon for Contrail Analytics%{?_gitVer}
Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net
Vendor:         Juniper Networks Inc

BuildArch:      noarch

Requires: python-ironicclient
Requires: python-keystoneclient >= 0.2.0
Requires: python-gevent
Requires: python-geventhttpclient
Requires: python-netaddr
Requires: python-kombu
Requires: python-contrail >= %{_verstr}-%{_relstr}

%description
BMS Notification daemon to interface between Openstack Ironic and Contrail Analytics

%prep
rm -rf %{_sbtop}build/debug/config/ironic-notification-manager/

%build
pushd %{_sbtop}controller
scons -U src/config/ironic-notification-manager
popd

%install
# Setup directories
rm -rf %{buildroot}%{_installdir}
install -d -m 755 %{buildroot}/etc/
install -d -m 755 %{buildroot}%{_contrailetc}
install -d -m 755 %{buildroot}%{_contrailetc}/supervisord_config_files/
install -d -m 755 %{buildroot}/usr/
install -d -m 755 %{buildroot}%{_binusr}
install -d -m 755 %{buildroot}%{python_sitelib}
install -d -m 755 %{buildroot}%{python_sitelib}/ironic-notification-manager/

# install files

pushd %{_sbtop}build/debug/config/ironic-notification-manager/
tar zxf dist/ironic-notification-manager-0.1dev.tar.gz
cd ironic-notification-manager-0.1dev
%{__python} setup.py install --root=%{buildroot}  %{?_venvtr}
popd

pushd %{_sbtop}
install -p -m 755 %{_ironic_notif_mgr}/ironic-notification-manager.conf %{buildroot}%{_contrailetc}/ironic-notification-manager.conf
install -p -m 755 %{_ironic_notif_mgr}/ironic-notification-manager.ini %{buildroot}%{_contrailetc}/supervisord_config_files/ironic-notification-manager.ini
popd

%files
%defattr(-,root,root,-)
%{_contrailetc}/ironic-notification-manager.conf
%{_contrailetc}/supervisord_config_files/ironic-notification-manager.ini
%{_binusr}/ironic-notification-manager
%{python_sitelib}/ironic_notification_manager
%{python_sitelib}/ironic_notification_manager-*
