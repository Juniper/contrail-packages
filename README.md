contrail-packages
=================

Build and packaging scripts for OpenContrail.

In order to build the debian packages execute the following set of commands from the top level directory of your sandbox.

packages:
        mkdir -p build/packages
        cp -R tools/packages/debian/contrail/debian build/packages
        chmod u+x build/packages/debian/rules
        (cd build/packages; fakeroot debian/rules binary)

