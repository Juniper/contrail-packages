#!/bin/bash

source /etc/contrail/agent_param

if [ $vgw_subnet_ip != __VGW_SUBNET_IP__ ]
then
    vgw_subnet=$vgw_subnet_ip"/"$vgw_subnet_mask
    route delete -net $vgw_subnet dev vgw
    ifconfig vgw down
fi
