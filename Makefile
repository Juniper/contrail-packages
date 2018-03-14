MKFILE_DIR 	:= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SB_TOP 			:= $(MKFILE_DIR:tools/packages/=)

SPEC_DIR 			:= $(MKFILE_DIR)rpm
SPEC_FILES 		:= $(wildcard $(SPEC_DIR)/*/*.spec)
PACKAGES 			:= $(patsubst %.spec,rpm-%,$(notdir $(SPEC_FILES)))
DEPENDENCIES 	:= $(patsubst %.spec,dep-%,$(notdir $(SPEC_FILES)))

DEBUGINFO    ?= TRUE
TOPDIR       ?= $(SB_TOP)
SCONSOPT     ?= production
SRCVER       ?= $(shell cat $(SB_TOP)/controller/src/base/version.info)
KVERS        ?= $(shell rpm -q --qf "%{VERSION}-%{RELEASE}.%{ARCH}" kernel-devel)
BUILDTAG     ?= $(shell date +%m%d%Y%H%M)
SKUTAG       ?= ocata
MANIFESTFILE ?= $(SB_TOP).repo/manifest.xml

RPMBUILD_FLAGS := -bb --define "_sbtop $(SB_TOP)"
RPMBUILD_FLAGS += --define "_topdir $(TOPDIR)"
RPMBUILD_FLAGS += --define "_opt $(SCONSOPT)"
RPMBUILD_FLAGS += --define "_kVers $(KVERS)"
RPMBUILD_FLAGS += --define "_skuTag $(SKUTAG)"
RPMBUILD_FLAGS += --define "_srcVer $(SRCVER)"
RPMBUILD_FLAGS += --define "_buildTag $(BUILDTAG)"

ifeq ($(DEBUGINFO),TRUE)
	RPMBUILD_FLAGS += --with debuginfo
else
	RPMBUILD_FLAGS += --without debuginfo
endif

ifdef MANIFESTFILE
	RPMBUILD_FLAGS += --define "_manifestFile $(MANIFESTFILE)"
endif

SCONSFLAGS := -j $(shell nproc)

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
	@echo Installing dependencies for $(SPECFILE)...
	@yum-builddep -y $(SPECFILE)

rpm-%:
	$(eval SPECFILE = $(filter %/$(patsubst rpm-%,%.spec,$@), $(SPEC_FILES)))
	rpmbuild $(RPMBUILD_FLAGS) $(SPECFILE)

list:
	@echo $(sort $(patsubst rpm-%,%,$(PACKAGES)))

info:
	@echo SPEC_FILES=$(SPEC_FILES)
	@echo DEBUGINFO=$(DEBUGINFO)
	@echo MANIFESTFILE=$(MANIFESTFILE)
	@echo TOPDIR=$(TOPDIR)
	@echo SCONSOPT=$(SCONSOPT)
	@echo SRCVER=$(SRCVER)
	@echo KVERS=$(KVERS)
	@echo BUILDTAG=$(BUILDTAG)
	@echo SKUTAG=$(SKUTAG)
	@echo RPMBUILD_FLAGS=$(RPMBUILD_FLAGS)
