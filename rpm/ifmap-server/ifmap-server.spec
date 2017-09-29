# 3contrail seems to be present in the cache for centos65 but spec file doesnt show it. Hence
# using 4contrail. Make sure to update tho sequence if generating new rpm for ifmap-server
%define         _relstr 7contrail
Name:               ifmap-server 
Version:            0.3.2 
Release:            %{_relstr}%{?dist}
Summary:            ifmap-server

Group:              Applications/System
License:            Commercial
#URL:                http://trust.f4.hs-hannover.de
Vendor:             Juniper Networks Inc
Source0:            http://trust.f4.hs-hannover.de/download/iron/archive/irond-0.3.2-src.zip 
Patch0:		    001_build_xml_use_common.patch
Patch1:		    002_ifmap_0.3.2.patch
Patch2:		    003_ifmap_split_results.patch
Patch3:		    004_ifmap_split_config.patch
Patch4:             005_ifmap_centos_property.patch	
Patch5:             005_ifmap_fix_utf_8_encoded_xml.patch
Patch6:             006_poll_results_buffer.patch
Patch7:             007_ifmap_leak_fixes.patch
Patch8:             008_ifmap_script_add.patch
Patch9:             009_ifmap_script_change.patch
Patch10:            010_manifest_mf.patch
Patch11:            011_ifmap_bug_1688227.patch
BuildArch: noarch
BuildRequires: log4j 
BuildRequires: apache-commons-codec 
BuildRequires: ant
BuildRequires: hc-httpcore

Requires: jre >= 1.6
Requires: slf4j
Requires: apache-commons-codec
Requires: log4j
Requires: hc-httpcore

%description
ifmap-server  

%prep
#copy the irond.tar.gz file to ifmap-server.tar.gz file
(cd $RPM_BUILD_DIR; unzip $RPM_SOURCE_DIR/irond-0.3.2-src.zip)
mkdir -p $RPM_BUILD_DIR/ifmap-server-0.3.2
ls $RPM_BUILD_DIR/irond-0.3.2-src | xargs -n 1 -I'{}' mv $RPM_BUILD_DIR/irond-0.3.2-src/'{}' $RPM_BUILD_DIR/ifmap-server-0.3.2/
#(cd $RPM_SOURCE_DIR;tar -zcvf ifmap-server-0.3.2.tar.gz $RPM_SOURCE_DIR/ifmap-server-0.3.2)

%setup -D -n ifmap-server-0.3.2
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
	
%build
pushd %{_builddir}/ifmap-server-0.3.2
ant
	
%install
install -d -m 755 %{buildroot}/usr/share/ifmap-server
install -p -D -m 640 %{_builddir}/ifmap-server-0.3.2/build/irond.jar %{buildroot}/usr/share/ifmap-server/
#install -p -D -m 640 %{buildroot}/../../BUILD/ifmap-server-0.3.2/ifmap.properties %{buildroot}/usr/share/ifmap-server/
#install -p -D -m 640 %{buildroot}/../../BUILD/ifmap-server-0.3.2/log4j.properties %{buildroot}/usr/share/ifmap-server/

install -d -m 755 %{buildroot}%{_bindir}
install -p -D -m 755 %{_builddir}/ifmap-server-0.3.2/ifmap-server %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}/etc/ifmap-server
#find . -print | sed 's;^;'"%{buildroot}/etc/ifmap-server/"';'| xargs install -d -m 755 
install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/ifmap.properties %{buildroot}/etc/ifmap-server/
install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/basicauthusers.properties %{buildroot}/etc/ifmap-server/
install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/authorization.properties %{buildroot}/etc/ifmap-server/
install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/log4j.properties %{buildroot}/etc/ifmap-server/
install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/publisher.properties %{buildroot}/etc/ifmap-server/
#Create sym links to 
pushd %{buildroot}/usr/share/ifmap-server/
ln -s /etc/ifmap-server/ifmap.properties ifmap.properties 
ln -s /etc/ifmap-server/log4j.properties log4j.properties
popd

#Install the keystore
install -d -m 755 %{buildroot}/etc/ifmap-server/keystore
pushd %{_builddir}/ifmap-server-0.3.2/keystore 
#find . -print | sed 's;^\.;'"%{buildroot}/etc/ifmap-server/keystore"';'| xargs install -p -D -m 644 %{_builddir}/ifmap-server-0.3.2/keystore
for f in %{_builddir}/ifmap-server-0.3.2/keystore/*; do \
    #install -m 644 -D ${f} %{buildroot}/etc/ifmap-server/keystore/ ; \
    install -m 644 ${f} %{buildroot}/etc/ifmap-server/keystore/; \
done
popd

#Install the schema
install -d -m 755 %{buildroot}/etc/ifmap-server/schema
pushd %{_builddir}/ifmap-server-0.3.2/schema
#find . -print | sed 's;^\.\/;'"%{buildroot}/etc/ifmap-server/schema"';'| xargs install -m 755
for f in %{_builddir}/ifmap-server-0.3.2/schema/*; do \
    #install -m 644 -D ${f} %{buildroot}/etc/ifmap-server/schema/ ; \
    install -m 644 ${f} %{buildroot}/etc/ifmap-server/schema/; \
done
popd

%post
set -e

if [ $1 -eq 1 ] ; then
    # Initial installation
  getent group contrail >/dev/null || groupadd -r contrail
  getent passwd contrail >/dev/null || \
    useradd -r -g contrail -d /var/lib/contrail -s /bin/false \
    -c "OpenContail daemon" contrail

  mkdir -p /var/log/contrail
  chown -R contrail:adm /var/log/contrail
  chown -R contrail /etc/contrail
  chmod 0750 /var/log/contrail
  chown -R contrail /var/lib/contrail/
  chown -R contrail:adm /usr/share/ifmap-server
fi

%postun
set -e

if [ "${1}" = "purge" ] ; then

  pkill -9 -f -u contrail irond.jar

  rm -rf /var/log/contrail /var/lib/contrail

  if (which deluser && getent passwd contrail) > /dev/null 2>&1; then
    deluser --system --quiet --backup-to /var/lib contrail
  fi

  if (which delgroup && getent group contrail) > /dev/null 2>&1; then
    delgroup --system --quiet contrail
  fi

fi

%files
%{_bindir}/ifmap-server
/usr/share/ifmap-server/
/etc/ifmap-server/*
