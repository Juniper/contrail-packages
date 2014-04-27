# -*- mode: makefile -*-
#
# This Makefile is copied by repo to the top of the sandbox
#

#
# Use the git reference of the controller repository as a version id.
# TODO: store the git refs for all projects in the manifest in a file
#
GIT_REF := $(shell (cd controller; git show --oneline) | awk '/[0-9a-f]+/ { print $$1; }')

#
# Version:
#    For development packages: <release><branch>~<ref>
#
VERSION := 1.1master~$(GIT_REF)

#
# KVERS
#    The kernel version to use when building a kernel module.
KVERS ?= `uname -r`

#
# KEYID
#    Specify secret key id when generating source packages.
#
KEYID?=
KEYOPT=-k$(KEYID)

#
# Directories listed in manifest (excluding package scripts)
#
SOURCE_CONTRAIL_DIRS:=$(shell xmllint --xpath '//manifest/project/@path' .repo/manifest.xml | sed -r 's/path=\"([^\"]+)\"/\1/g' | sed 's/tools\/packages//')
SOURCE_CONTRAIL_ARCHIVE:=SConstruct $(SOURCE_CONTRAIL_DIRS)

all: package-contrail \
     package-ifmap-server \
     package-ifmap-python-client

package-ifmap-server: debian-ifmap-server
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); fakeroot debian/rules get-orig-source)
	(cd build/packages/$(PACKAGE); fakeroot debian/rules binary)

package-contrail: debian-contrail
	$(eval PACKAGE := contrail)
	@echo "Building package $(PACKAGE)"
	sed -i 's/VERSION/$(VERSION)/g' build/packages/$(PACKAGE)/debian/changelog
	(cd build/packages/$(PACKAGE); dpkg-buildpackage -uc -us -b -rfakeroot)
	chmod u+x build/packages/contrail/debian/rules.modules
	(cd build/packages/$(PACKAGE); fakeroot debian/rules.modules KVERS=$(KVERS) binary-modules)

source-package-contrail: clean-contrail debian-contrail
	$(eval PACKAGE := contrail)
	sed -i 's/VERSION/$(VERSION)/g' build/packages/$(PACKAGE)/debian/changelog
	(cd vrouter; git clean -f -d)
	tar zcf build/packages/contrail_$(VERSION).orig.tar.gz $(SOURCE_CONTRAIL_ARCHIVE)
	@echo "Building source package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); dpkg-buildpackage -S -rfakeroot $(KEYOPT))

source-package-ifmap-server: clean-ifmap-server debian-ifmap-server
	$(eval PACKAGE := ifmap-server)
	(cd build/packages/$(PACKAGE); fakeroot debian/rules get-orig-source)
	(cd build/packages/$(PACKAGE); tar zcf ../ifmap-server_0.3.2.orig.tar.gz .)
	(cd build/packages/$(PACKAGE); dpkg-buildpackage -S -rfakeroot $(KEYOPT))

package-%: debian-%
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); fakeroot debian/rules binary)

debian-%:
	$(eval PACKAGE := $(patsubst debian-%,%,$@))
	mkdir -p build/packages/$(PACKAGE)
	cp -R tools/packages/debian/$(PACKAGE)/debian build/packages/$(PACKAGE)
	chmod u+x build/packages/$(PACKAGE)/debian/rules

clean-%:
	$(eval PACKAGE := $(patsubst clean-%,%,$@))
	rm -rf build/packages/$(PACKAGE)
