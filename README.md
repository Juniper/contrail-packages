contrail-packages
=================

Build and packaging scripts for OpenContrail.

In order to build the debian packages execute the following set of commands from the top level directory of your sandbox.

```makefile
packages:

        mkdir -p build/packages
        cp -R tools/packages/debian/opencontrail/debian build/packages
        chmod u+x build/packages/debian/rules
        (cd build/packages; fakeroot debian/rules binary)
```
