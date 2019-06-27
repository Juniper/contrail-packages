# contrail-packages
---

Build and packaging scripts for OpenContrail.


## Contents of this repository

```
├── debian/                  # Debian packaging
│   ├── contrail/            # Debian package for contrail
│   └── <pkg-name>/          # Debian package <pkg-name>
├── rpm/                     # RPM packaging
│   ├── contrail/            # RPMs for contrail
│   │   ├── contrail.spec    # RPM spec for package contrail
│   │   └── <pkg-files>      # Files used with package contrail
│   └── <pkg-name>/          # RPMs for <pkg-name>
│   │   ├── <pkg-name>.spec  # RPM spec for package <pkg-name>
│   │   └── <pkg-files>      # Files used with package <pkg-name>
├── utils/                   # Utility scripts
└── Makefile
```

## Packaging guide (RPM)

1. Keep spec files in corresponding directories (e.g. contrail-heat: rpm/contrail-heat/contrail-heat.spec)
2. Keep all additional files in directories specific to package
3. Use absolute paths for sandbox-related variables (e.g. `%define _distropkgdir %{_sbtop}tools/packages/rpm/%{name}`)

## Using Makefile for RPM

1. Makefile can be used from anywhere within the contrail sandbox, e.g. `make -f <current_path_to_packages>/Makefile`
2. Following Makefile targets are supported:
    1. `rpm` - builds all rpm packages in the repository
    2. `rpm-<pkg-name>` - builds specific package `<pkg-name>`
    3. `dep` - installs all dependencies for all packages (**requires root privileges or sudo**)
    4. `dep-<pkg-name>` - installs dependencies for `<pkg-name>` (**requires root privileges or sudo**)
    5. `list` - lists all the packages available for building
    6. `info` - shows information about set variables
3. Following Environment variables can be used for controlling Makefile behavior:
    1. `DEBUGINFO` = `TRUE`/`FALSE` - build debuginfo packages (default: `TRUE`)
    2. `TOPDIR` - control where packages will be built (default: `SB_TOP`)
    3. `SCONSOPT` = `debug`/`production` - select optimization level for scons (default: `production`)
    4. `SRCVER` - specify source code version (default from `controller/src/base/version.info`)
    5. `KVERS` - kernel version to build against (default: installed version of `kernel-devel`)
    6. `BUILDTAG` - additional tag for versioning (default: `date +%m%d%Y%H%M`)
    7. `SKUTAG` - OpenStack SKU (default: `ocata`)

---

## Debian Packaging (Deprecated)

In order to build the debian packages execute the following set of commands from the top level directory of your sandbox.

```
make -f packages.make
```
