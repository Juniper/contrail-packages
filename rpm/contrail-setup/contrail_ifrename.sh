#!/bin/bash

devpath=`/sbin/udevadm info --path=/sys/class/net/$1 --query=all 2>/dev/null | grep DEVPATH | grep pci | grep -v usb`
if [ $? -ne 0 ]
then
    exit 2
fi

string=`expr "$devpath" : '.*\(\/.*/net/*\)'`
IFS=\/ pci_string=($string)
spec_string=${pci_string[1]}
IFS=\: domain_bus_dev_fn=($spec_string)
bus=`printf "%d\n" 0x${domain_bus_dev_fn[1]}`
IFS=\. dev_fn=(${domain_bus_dev_fn[2]})
dev=`printf "%d\n" 0x${dev_fn[0]}`
fn=`printf "%d\n" 0x${dev_fn[1]}`
echo "p$bus""p$dev""p$fn"
