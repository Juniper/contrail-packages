MKFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SB_TOP := $(MKFILE_DIR:/tools/packages/=)

SPEC_DIR := $(MKFILE_DIR)rpm
SPEC_FILES := $(wildcard $(SPEC_DIR)/*/*.spec)
PACKAGES := $(patsubst %.spec,rpm-%,$(notdir $(SPEC_FILES)))
DEPENDENCIES := $(patsubst %.spec,dep-%,$(notdir $(SPEC_FILES)))

DEBUGINFO := TRUE
SCONSOPT := production
SRCVER := $(shell cat $(SB_TOP)/controller/src/base/version.info)
KVERS := $(shell rpm -q --qf "%{VERSION}-%{RELEASE}.%{ARCH}" kernel-devel)
BUILDTAG := $(shell date +%m%d%Y%H%M)

RPMBUILD_FLAGS := -bb --define "_sbtop $(SB_TOP)"
RPMBUILD_FLAGS += --define "_opt $(SCONSOPT)"
RPMBUILD_FLAGS += --define "_kVers $(KVERS)"
RPMBUILD_FLAGS += --define "_srcVer $(SRCVER)"
RPMBUILD_FLAGS += --define "_buildTag $(BUILDTAG)"

SCONSFLAGS := -j$(shell nproc)

export BUILD_ONLY := TRUE
export SCONSFLAGS := $(SCONSFLAGS)

all: dep rpm
	@echo $(PACKAGES)
	@echo $(DEPENDENCIES)

.PHONY: all rpm dep

dep: $(DEPENDENCIES)
rpm: $(PACKAGES)

dep-%:
	$(eval SPECFILE = $(filter %/$(patsubst dep-%,%.spec,$@), $(SPEC_FILES)))
	$(info Installing dependencies for $(SPECFILE)...)
	@yum-builddep -y $(SPECFILE) >/dev/null
	$(info DONE)

rpm-%:
	$(eval SPECFILE = $(filter %/$(patsubst rpm-%,%.spec,$@), $(SPEC_FILES)))
	@rpmbuild $(RPMBUILD_FLAGS) $(SPECFILE)

list:
	@echo $(patsubst rpm-%,%,$(PACKAGES))

info:
	@echo SPEC_FILES=$(SPEC_FILES)
	@echo SRCVER=$(SRCVER)
	@echo KVERS=$(KVERS)
	@echo SCONSOPT=$(SCONSOPT)
	@echo BUILDTAG=$(BUILDTAG)
