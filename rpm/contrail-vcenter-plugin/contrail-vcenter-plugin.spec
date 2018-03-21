%define _contrailvcenterplugin /usr/share/contrail-vcenter-plugin
%define _javaapidir            %{_sbtop}/java-api
%define _vrouterjavaapidir     %{_sbtop}/vrouter-java-api
%define _vijavadir             %{_sbtop}/vijava
%define _vcenterplugindir      %{_sbtop}/vcenter-plugin
%define _maven                 mvn -B -Dmaven.test.skip=true

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

Release: %{_relstr}%{?dist}
Summary: Contrail vCenter Plugin Application %{?_gitVer}
Name:    contrail-vcenter-plugin
Version:  %{_verstr}

Group:   Applications/System
License: Commercial
URL:     http://www.juniper.net/
Vendor:  Juniper Networks Inc

BuildRequires: maven

Requires: java-1.7.0-openjdk
Requires: libcontrail-vrouter-java-api
Requires: libcontrail-java-api
Requires: libcontrail-vijava


%description
Metapackage for contrail-vcenter-plugin

%package -n libcontrail-java-api
Summary: Contrail java api %{?_gitVer}
Group:   Applications/System

%description -n libcontrail-java-api
Contrail VNC API Java Library.

%package -n libcontrail-vrouter-java-api
Summary: Contrail vRouter API Java Library %{?_gitVer}
Group:   Applications/System

Requires: libcontrail-java-api

%description -n libcontrail-vrouter-java-api
contrail-vrouter Java API bindings

%package -n libcontrail-vijava
Summary: Contrail vijava %{?_gitVer}
Group:   Applications/System

%description -n libcontrail-vijava
Provides libcontrail-vijava binary

%prep
pushd %{_javaapidir}
%{_maven} -q clean 
popd
pushd %{_vrouterjavaapidir}
%{_maven} -q clean
popd
pushd %{_vijavadir}
%{_maven} -q clean
popd
pushd %{_vcenterplugindir}
%{_maven} -q clean
popd


%build
pushd %{_javaapidir}
%{_maven} install 
popd
pushd %{_vrouterjavaapidir}
%{_maven} install
popd
pushd %{_vijavadir}
%{_maven} install
popd
pushd %{_vcenterplugindir}
%{_maven} install
%{_maven} dependency:copy-dependencies -DincludeScope=runtime
popd

%install
install -d %{buildroot}%{_contrailvcenterplugin}/lib
install -d %{buildroot}%{_bindir}

# Begin install for libcontrail-java-api
install -p -m 755 \
  %{_javaapidir}/target/juniper-contrail-api-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-api-3.0-SNAPSHOT.jar
ln -s \
  %{_contrailvcenterplugin}/juniper-contrail-api-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-api.jar

# Begin install for libcontrail-vrouter-java-api
install -p -m 755 \
  %{_vrouterjavaapidir}/target/juniper-contrail-vrouter-api-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-vrouter-api-3.0-SNAPSHOT.jar
ln -s \
  %{_contrailvcenterplugin}/juniper-contrail-vrouter-api-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-vrouter-api.jar

# Begin install for libcontrail-vijava
install -p -m 755 \
  %{_vijavadir}/target/juniper-contrail-vijava-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-vijava-3.0-SNAPSHOT.jar
ln -s \
  %{_contrailvcenterplugin}/juniper-contrail-vijava-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-vijava.jar

# Begin install for contrail-vcenter-plugin
install -p -m 755 \
  %{_vcenterplugindir}/target/dependency/*.jar \
  %{buildroot}%{_contrailvcenterplugin}/lib
install -p -m 644 \
  %{_vcenterplugindir}/log4j.properties \
  %{buildroot}%{_contrailvcenterplugin}
install -p -m 755 \
  %{_vcenterplugindir}/control_files/contrail-vcenter-plugin \
  %{buildroot}%{_bindir}/contrail-vcenter-plugin
ln -s \
  %{_contrailvcenterplugin}/juniper-contrail-vcenter-3.0-SNAPSHOT.jar \
  %{buildroot}%{_contrailvcenterplugin}/juniper-contrail-vcenter.jar

%files -n libcontrail-java-api
%defattr(-, root, root)
%{_contrailvcenterplugin}/juniper-contrail-api*.jar

%files -n libcontrail-vrouter-java-api
%defattr(-, root, root)
%{_contrailvcenterplugin}/juniper-contrail-vrouter-api*.jar

%files -n libcontrail-vijava
%defattr(-, root, root)
%{_contrailvcenterplugin}/juniper-contrail-vijava*.jar

%files
%defattr(-, root, root)
%{_contrailvcenterplugin}/lib/*.jar
%{_contrailvcenterplugin}/juniper-contrail-vcenter*.jar
%{_contrailvcenterplugin}/log4j.properties
%{_bindir}/contrail-vcenter-plugin
