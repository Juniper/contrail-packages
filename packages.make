#
# This Makefile is copied by repo to the top of the sandbox
#
all: package-opencontrail \
     package-ifmap-server \
     package-ifmap-python-client

package-ifmap-server: debian-ifmap-server
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); fakeroot debian/rules get-orig-source)
	(cd build/packages/$(PACKAGE); fakeroot debian/rules binary)

package-%: debian-%
	$(eval PACKAGE := $(patsubst package-%,%,$@))
	@echo "Building package $(PACKAGE)"
	(cd build/packages/$(PACKAGE); fakeroot debian/rules binary)

debian-%:
	$(eval PACKAGE := $(patsubst debian-%,%,$@))
	mkdir -p build/packages/$(PACKAGE)
	cp -R tools/packages/debian/$(PACKAGE)/debian build/packages/$(PACKAGE)
	chmod u+x build/packages/$(PACKAGE)/debian/rules
