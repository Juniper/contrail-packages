Name:           python-kazoo
Version:        2.5.0
Release:        2018-06-01
Summary:        Higher Level Zookeeper Client

License:        Apache 2.0
URL:            https://pypi.python.org/pypi/kazoo
Source0:        %pypi_source

BuildArch:      noarch

Requires:       python-eventlet >= 0.17.1
# 2.5.0 wants (but not requires) gevent>=1.2 but only 1.1.2 only available for build. for 2.4.0 it's >=1.1
# TODO: if gevent is critical than kazoo version should be down in contrail-thirdparty to 2.4.0
#Requires:       gevent >= 1.2

%description
Higher Level Zookeeper Client

%prep

%build

%install
pushd %{_sbtop}third_party/kazoo-2.5.0
%{__python} setup.py install --root=%{buildroot}
popd

%files
%defattr(-,root,root,-)
%{python_sitelib}/kazoo*

