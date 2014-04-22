## Work in progress on dependency

### Backport available in Debian

* [python-thrift](http://ftp.de.debian.org/debian/pool/main/p/python-thrift/python-thrift_0.9.0-1_amd64.deb)
* [python-kazoo](http://ftp.de.debian.org/debian/pool/main/k/kazoo/python-kazoo_1.3.1-1_all.deb)
* [python-stevedore](http://ftp.de.debian.org/debian/pool/main/s/stevedore/python-stevedore_0.14.1-1_all.deb)
* [python-lxml](http://ftp.de.debian.org/debian/pool/main/l/lxml/python-lxml_3.3.1-1~bpo70+1_amd64.deb)

### Backport available in Ubuntu

* [python-bitarray](http://de.archive.ubuntu.com/ubuntu/pool/universe/p/python-bitarray/python-bitarray_0.8.0-2_amd64.deb)
* [python-bottle](http://de.archive.ubuntu.com/ubuntu/pool/universe/p/python-bottle/python-bottle_0.11.6-1_all.deb)
  * [python](http://de.archive.ubuntu.com/ubuntu/pool/main/p/python-defaults/python_2.7.5-5ubuntu1_amd64.deb)
  * [libpython-stdlib](http://de.archive.ubuntu.com/ubuntu/pool/main/p/python-defaults/libpython-stdlib_2.7.5-5ubuntu1_amd64.deb)
  * [libpython2.7-stdlib](http://security.ubuntu.com/ubuntu/pool/main/p/python2.7/libpython2.7-stdlib_2.7.5-8ubuntu3.1_amd64.deb)
  * [libpython2.7-minimal](http://security.ubuntu.com/ubuntu/pool/main/p/python2.7/libpython2.7-minimal_2.7.5-8ubuntu3.1_amd64.deb)
  * [python2.7-minimal](http://security.ubuntu.com/ubuntu/pool/main/p/python2.7/python2.7-minimal_2.7.5-8ubuntu3.1_amd64.deb)

### Work in progress (backport)

* [python-ncclient](http://anonscm.debian.org/gitweb/?p=collab-maint/python-ncclient.git)
  * WIP on [mentors](http://mentors.debian.net/debian/pool/main/p/python-ncclient/python-ncclient_0.4.1-1.dsc)
* [python-geventhttpclient](http://anonscm.debian.org/gitweb/?p=collab-maint/python-geventhttpclient.git)
* [python-xmltodict](http://anonscm.debian.org/gitweb/?p=collab-maint/python-xmltodict.git)
  * In [NEW queue](http://ftp-master.debian.org/new/python-xmltodict_0.9.0-1.html)
* [python-pycassa](http://anonscm.debian.org/gitweb/?p=collab-maint/pycassa.git)
  * In [NEW queue](http://ftp-master.debian.org/new/pycassa_1.11.0-1.html)

### Need investigations

* Differences between (or debug pydist-override)
 * [python-zookeeper](https://packages.debian.org/wheezy/python-zookeeper)
 * [zc-zookeeper-static](https://github.com/python-zk/zc-zookeeper-static)
