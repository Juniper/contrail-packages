contrail-packages
=================

Build and packaging scripts for OpenContrail.

In order to build the debian packages execute the following set of commands from the top level directory of your sandbox.

## OpenContrail

```makefile
packages:

        mkdir -p build/packages
        cp -R tools/packages/debian/opencontrail/debian build/packages
        chmod u+x build/packages/debian/rules
        (cd build/packages; fakeroot debian/rules binary)
```

## ifmap-python-client

[ifmap-python-client](https://github.com/ITI/ifmap-python-client/) with OpenContrail patches

```make
ifmap-client:

        mkdir -p build/packages
        cp -R tools/packages/debian/ifmap-python-client/debian build/packages/ifmap-python-client
        chmod u+x build/packages/ifmap-python-client/debian/rules
        cd build/packages/ifmap-python-client
        fakeroot debian/rules get-orig-source
        fakeroot debian/rules binary
```
