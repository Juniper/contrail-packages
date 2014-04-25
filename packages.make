#
# This Makefile is copied by repo to the top of the sandbox
#
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
	$(eval VERSION := 1.1dev)
	@echo "Building package $(PACKAGE)"
	sed -i 's/VERSION/$(VERSION)/g' build/packages/$(PACKAGE)/debian/changelog
	(cd build/packages/$(PACKAGE); dpkg-buildpackage -uc -us -b -rfakeroot)
	chmod u+x build/packages/contrail/debian/rules.modules
	(cd build/packages/$(PACKAGE); fakeroot debian/rules.modules KVERS=`uname -r` binary-modules)

package-%: debian-%
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); fakeroot debian/rules binary)

debian-%:
	$(eval PACKAGE := $(patsubst debian-%,%,$@))
	mkdir -p build/packages/$(PACKAGE)
	cp -R tools/packages/debian/$(PACKAGE)/debian build/packages/$(PACKAGE)
	chmod u+x build/packages/$(PACKAGE)/debian/rules
