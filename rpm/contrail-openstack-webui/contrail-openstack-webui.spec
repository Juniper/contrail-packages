%define         _distropkgdir %{_sbtop}tools/packages/rpm/%{name}
%define         _contrailetc            /etc/contrail
%define         _contrailwebsrc         /usr/src/contrail/contrail-webui
%if 0%{?fedora} >= 17
%define         _servicedir             /usr/lib/systemd/system
%endif
%define         _nodemodules            node_modules/
%define         _config                 contrail-web-core/config
%define         _contrailuitoolsdir     src/tools
%define         _supervisordir /etc/contrail/supervisord_webui_files

%if 0%{?_buildTag:1}
%define         _relstr      %{_buildTag}
%else
%define         _relstr      %(date -u +%y%m%d%H%M)
%endif
%{echo: "Building release %{_relstr}\n"}
%if 0%{?_srcVer:1}
%define         _verstr      %{_srcVer}
%else
%define         _verstr      1
%endif
Release:	    %{_relstr}%{?dist}
Summary: Contrail Openstack Webui %{?_gitVer}
Name: contrail-openstack-webui
Version:	    %{_verstr}

Group:          Applications/System
License:        Commercial
URL:            http://www.juniper.net/
Vendor:         Juniper Networks Inc

BuildArch: noarch

Requires: python-contrail >= %{_verstr}-%{_relstr}
Requires: contrail-web-core >= %{_verstr}-%{_relstr}
Requires: contrail-web-controller >= %{_verstr}-%{_relstr}
Requires: contrail-setup >= %{_verstr}-%{_relstr}
Requires: contrail-utils >= %{_verstr}-%{_relstr}
Requires: opscenter

%description
Contrail Package Requirements for WebUI

%install
pushd %{_builddir}/..
install -d -m 755 %{buildroot}%{_contrailetc}
install -p -m 755 %{_distropkgdir}/supervisord_webui.conf %{buildroot}%{_contrailetc}/supervisord_webui.conf

%post
f [ "$1" = "1" ]; then
  i=0
  while : ; do
      sudo service opscenterd status
      if [ $? -eq 0 ] ; then
          break
      fi
      i=$(($i+1))
      if [ $i -gt 10 ] ; then
          echo "Error: postinst contrail-openstack-webui, expected opscenterd to be running"
          break
      fi
      sleep 3
  done
  sudo service opscenterd stop
  i=0
  while : ; do
      ps auxw | grep -Eq "opscenter\.pid" 2>/dev/null
      if [ $? -ne 0 ] ; then
          break
      fi
      i=$(($i+1))
      if [ $i -gt 5 ] ; then
          kill `ps auxw | grep -E "opscenter\.pid" | grep -v grep | awk '{print $2}'` > /dev/null 2>&1
          break
      fi
      sleep 2
  done
fi
chkconfig opscenterd off

%files
%defattr(-,root,root)
%config(noreplace) %{_contrailetc}/supervisord_webui.conf
#%config(noreplace) %{_initddir}/supervisor-webui.conf
 
%changelog
* Tue Aug  6 2013 <ndramesh@juniper.net>
* Initial build.

