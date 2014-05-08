#
# Version:
#    For development packages: <release><branch>~<ref>
#    For snapshots: <release><branch>~$(shell date +%Y%m%d)
#
ifdef VERSION

CONTRAIL_VERSION = $(VERSION)
NEUTRON_VERSION = $(VERSION)

else
#
# Use the git reference of the controller repository as a version id.
# TODO: store the git refs for all projects in the manifest in a file
#

CONTROLLER_REF := $(shell (cd controller; git log --oneline -1) | awk '/[0-9a-f]+/ { print $$1; }')
NEUTRON_REF := $(shell (cd openstack/neutron_plugin; git log --oneline -1) | awk '/[0-9a-f]+/ { print $$1; }')
CONTRAIL_VERSION = 1.1master~$(CONTROLLER_REF)
NEUTRON_VERSION = 1.1master~$(NEUTRON_REF)

endif
