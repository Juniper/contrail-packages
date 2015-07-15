#!/bin/bash

source /etc/contrail/agent_param

function pkt_setup () {
    for f in /sys/class/net/$1/queues/rx-*
    do
        q="$(echo $f | cut -d '-' -f2)"
        r=$(($q%32))
        s=$(($q/32))
        ((mask=1<<$r))
        str=(`printf "%x" $mask`)
        if [ $s -gt 0 ]; then
            for ((i=0; i < $s; i++))
            do
                str+=,00000000
            done
        fi
        echo $str > $f/rps_cpus
    done
}

function insert_vrouter() {
    if cat $CONFIG | grep '^\s*platform\s*=\s*dpdk\b' &>/dev/null; then
        vrouter_dpdk_start
        return $?
    fi

    grep $kmod /proc/modules 1>/dev/null 2>&1
    if [ $? != 0 ]; then
        modprobe $kmod
        if [ $? != 0 ]
        then
            echo "$(date) : Error inserting vrouter module"
            return 1
        fi

        if [ -f /sys/class/net/pkt1/queues/rx-0/rps_cpus ]; then
            pkt_setup pkt1
        fi
        if [ -f /sys/class/net/pkt2/queues/rx-0/rps_cpus ]; then
            pkt_setup pkt2
        fi
        if [ -f /sys/class/net/pkt3/queues/rx-0/rps_cpus ]; then
            pkt_setup pkt3
        fi
    fi

    # check if vhost0 is not present, then create vhost0 and $dev
    if [ ! -L /sys/class/net/vhost0 ]; then
        echo "$(date): Creating vhost interface: $DEVICE."
        # for bonding interfaces
        loops=0
        while [ ! -f /sys/class/net/$dev/address ]
        do
            sleep 1
            loops=$(($loops + 1))
            if [ $loops -ge 60 ]; then
                echo "Unable to look at /sys/class/net/$dev/address"
                return 1
            fi
        done

        DEV_MAC=$(cat /sys/class/net/$dev/address)
        vif --create $DEVICE --mac $DEV_MAC
        if [ $? != 0 ]; then
            echo "$(date): Error creating interface: $DEVICE"
        fi


        echo "$(date): Adding $dev to vrouter"
        DEV_MAC=$(cat /sys/class/net/$dev/address)
        vif --add $dev --mac $DEV_MAC --vrf 0 --vhost-phys --type physical
        if [ $? != 0 ]; then
            echo "$(date): Error adding $dev to vrouter"
        fi

        vif --add $DEVICE --mac $DEV_MAC --vrf 0 --type vhost --xconnect $dev
        if [ $? != 0 ]; then
            echo "$(date): Error adding $DEVICE to vrouter"
        fi
    fi
    return 0
}

############################################################################
## vRouter/DPDK Functions
############################################################################

##
## Read Agent Configuration File and Global vRouter/DPDK Configuration
##
_dpdk_conf_read() {
    if [ -n "${_DPDK_CONF_READ}" ]; then
        return
    fi
    _DPDK_CONF_READ=1

    ## global vRouter/DPDK configuration
    DPDK_BIND="/usr/lib/contrail/dpdk_nic_bind.py"
    DPDK_RTE_CONFIG="/run/.rte_config"
    VROUTER_SERVICE="supervisor-vrouter"
    AGENT_CONF="${CONFIG}"
    VROUTER_DPDK_INI=/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini
    DPDK_NETLINK_TCP_PORT=20914

    if [ ! -s ${AGENT_CONF} ]; then
        echo "$(date): Error reading ${AGENT_CONF}: file does not exist"
        exit 1
    fi

    eval `cat ${AGENT_CONF} | grep '^[a-zA-Z]'`

    AGENT_PLATFORM="${platform}"
    DPDK_PHY="${physical_interface}"
    DPDK_PHY_PCI="${physical_interface_address}"
    DPDK_PHY_MAC="${physical_interface_mac}"
    DPDK_VHOST="${name}"

    if [ -z "${DPDK_PHY}" ]; then
        echo "$(date): Error reading ${AGENT_CONF}: no physical device defined"
        exit 1
    fi
    if [ -z "${DPDK_VHOST}" ]; then
        echo "$(date): Error reading ${AGENT_CONF}: no vhost device defined"
        exit 1
    fi

    ## check for VLANs
    _vlan_file="/proc/net/vlan/${DPDK_PHY}"
    DPDK_VLAN_IF=""
    DPDK_VLAN_ID=""
    DPDK_VLAN_DEV=""
    if [ -f "${_vlan_file}" ]; then
        DPDK_VLAN_IF="${DPDK_PHY}"
        DPDK_VLAN_ID=`cat ${_vlan_file} | grep "VID:" | head -1 | awk '{print $3}'`
        DPDK_VLAN_DEV=`cat ${_vlan_file} | grep "Device:" | head -1 | awk '{print $2}'`
        if [ -n "${DPDK_VLAN_DEV}" ]; then
            ## use raw device and pass VLAN ID as a parameter
            DPDK_PHY="${DPDK_VLAN_DEV}"
        fi
    fi
}

##
## Check if vRouter/DPDK is Running
##
_is_vrouter_dpdk_running() {
    # check for NetLink TCP socket
    lsof -ni:${DPDK_NETLINK_TCP_PORT} -sTCP:LISTEN > /dev/null

    return $?
}

##
## Start vRouter/DPDK
##
vrouter_dpdk_start() {
    echo "$(date): Starting vRouter/DPDK..."

    _dpdk_conf_read

    # remove rte configuration file if vRouter has crashed
    rm -f ${DPDK_RTE_CONFIG}

    service ${VROUTER_SERVICE} start
    loops=0
    # wait for vRouter/DPDK to start
    while ! _is_vrouter_dpdk_running
    do
        sleep 5
        loops=$(($loops + 1))
        if [ $loops -ge 60 ]; then
            echo "$(date): Error starting ${VROUTER_SERVICE} service: vRouter/DPDK is not running"
            return 1
        fi
    done

    echo "$(date): Waiting for Agent to configure ${DPDK_VHOST}..."
    loops=0
    while [ ! -L /sys/class/net/${DPDK_VHOST} ]
    do
        sleep 2
        loops=$(($loops + 1))
        if [ $loops -ge 10 ]; then
            echo "$(date): Error Agent configuring ${DPDK_VHOST}: interface does not exist"
            break
        fi
    done

    # check if vhost0 is not present, then create vhost0 and $dev
    if [ ! -L /sys/class/net/${DPDK_VHOST} ]; then
        echo "$(date): Creating ${DPDK_VHOST} interface with vif utility..."

        if [ -z "${DPDK_PHY_MAC}"]; then
            echo "Error reading ${AGENT_CONF}: physical MAC address is not defined"
            return 1
        fi
        if [ -z "${DPDK_PHY_PCI}"]; then
            echo "Error reading ${AGENT_CONF}: physical PCI address is not defined"
            return 1
        fi

        # TODO: the vhost creation is happening later in vif --add
#        vif --create ${DPDK_VHOST} --mac ${DPDK_PHY_MAC}
#        if [ $? != 0 ]; then
#            echo "$(date): Error creating interface: ${DPDK_VHOST}"
#        fi

        echo "$(date): Adding ${DPDK_PHY} interface with vif utility..."
        # add DPDK ethdev 0 as a physical interface
        vif --add 0 --mac ${DPDK_PHY_MAC} --vrf 0 --vhost-phys --type physical --pmd --id 0
        if [ $? != 0 ]; then
            echo "$(date): Error adding ${DPDK_PHY} interface"
        fi

        echo "$(date): Adding ${DPDK_VHOST} interface with vif utility..."
        # TODO: vif --xconnect seems does not work without --id parameter?
        vif --add ${DPDK_VHOST} --mac ${DPDK_PHY_MAC} --vrf 0 --type vhost --xconnect 0 --pmd --id 1
        if [ $? != 0 ]; then
            echo "$(date): Error adding ${DPDK_VHOST} interface"
        fi
    fi
    echo "$(date): Done starting vRouter/DPDK."
    return 0
}

##
## Collect Runtime Bond Device Information
## Returns:
##     DPDK_BOND_MODE   - non-empty string for bond interface, empty otherwise
##     DPDK_BOND_SLAVES - list of bond device members or just one non-bond device
##
_dpdk_system_bond_info_collect() {
    if [ -n "${_DPDK_SYSTEM_BOND_INFO_COLLECT}" ]; then
        return
    fi
    _DPDK_SYSTEM_BOND_INFO_COLLECT=1

    _dpdk_conf_read

    bond_dir="/sys/class/net/${DPDK_PHY}/bonding"
    DPDK_BOND_MODE=""
    DPDK_BOND_POLICY=""
    DPDK_BOND_SLAVES=""
    if [ -d ${bond_dir} ]; then
        DPDK_BOND_MODE=`cat ${bond_dir}/mode | awk '{print $2}'`
        DPDK_BOND_POLICY=`cat ${bond_dir}/xmit_hash_policy | awk '{print $1}'`
        DPDK_BOND_SLAVES=`cat ${bond_dir}/slaves | tr ' ' '\n' | sort | tr '\n' ' '`
        DPDK_BOND_SLAVES="${DPDK_BOND_SLAVES% }"
    else
        # put the physical interface into the list, so we can use the
        # same code to bind/unbind the interface
        DPDK_BOND_SLAVES="${DPDK_PHY}"
    fi

    ## Map Linux values to DPDK
    case "${DPDK_BOND_POLICY}" in
        "layer2") DPDK_BOND_POLICY="l2";;
        "layer3+4") DPDK_BOND_POLICY="l34";;
        "layer2+3") DPDK_BOND_POLICY="l23";;
        # DPDK 2.0 does not support inner packet hashing
        "encap2+3") DPDK_BOND_POLICY="l23";;
        "encap3+4") DPDK_BOND_POLICY="l34";;
    esac

    DPDK_BOND_PCIS=""
    DPDK_BOND_NUMA=""
    DPDK_BOND_MAC=""
    ## Bond Members
    for slave in ${DPDK_BOND_SLAVES}; do
        slave_dir="/sys/class/net/${slave}"

        slave_pci=`readlink ${slave_dir}/device`
        slave_pci=${slave_pci##*/}
        slave_numa=`cat ${slave_dir}/device/numa_node`
        slave_mac=`cat ${slave_dir}/address`
        if [ -n "${slave_pci}" ]; then
            DPDK_BOND_PCIS="${DPDK_BOND_PCIS} ${slave_pci}"
        fi
        if [ -z "${DPDK_BOND_NUMA}" ]; then
            DPDK_BOND_NUMA="${slave_numa}"
        fi
        if [ -z "${DPDK_BOND_MAC}" ]; then
            DPDK_BOND_MAC="${slave_mac}"
        fi
    done
    DPDK_BOND_PCIS="${DPDK_BOND_PCIS# }"
}

##
## Update vRouter/DPDK INI File
##
_dpdk_vrouter_ini_update() {
    _dpdk_system_bond_info_collect

    dpdk_vdev=""
    if [ -n "${DPDK_BOND_MODE}" -a -n "${DPDK_BOND_NUMA}" ]; then
        echo "${0##*/}: updating bonding configuration in ${VROUTER_DPDK_INI}..."

        dpdk_vdev="--vdev \"eth_bond_${DPDK_PHY},mode=${DPDK_BOND_MODE}"
        dpdk_vdev="${dpdk_vdev},xmit_policy=${DPDK_BOND_POLICY}"
        dpdk_vdev="${dpdk_vdev},socket_id=${DPDK_BOND_NUMA}"
        for SLAVE in ${DPDK_BOND_PCIS}; do
            dpdk_vdev="${dpdk_vdev},slave=${SLAVE}"
        done
        dpdk_vdev="${dpdk_vdev}\""

        ## update the ini file
        sed -ri.bond.bak \
            -e 's/(^ *command *=.*vrouter-dpdk.*) (--vdev +\"[^"]+\"|--vdev +[^ ]+)(.*) *$/\1\3/' \
            -e 's/(^ *command *=.*vrouter-dpdk.*) (--vdev +\"[^"]+\"|--vdev +[^ ]+)(.*) *$/\1\3/' \
            -e "s/(^ *command *=.*vrouter-dpdk.*)/\\1 ${dpdk_vdev}/" \
             ${VROUTER_DPDK_INI}
    fi

    dpdk_vlan=""
    if [ -n "${DPDK_VLAN_ID}" ]; then
        echo "${0##*/}: updating VLAN configuration in ${VROUTER_DPDK_INI}..."

        dpdk_vlan="--vlan \"${DPDK_VLAN_ID}\""

        ## update the ini file
        sed -ri.vlan.bak \
            -e 's/(^ *command *=.*vrouter-dpdk.*) (--vlan +\"[^"]+\"|--vlan +[^ ]+)(.*) *$/\1\3/' \
            -e 's/(^ *command *=.*vrouter-dpdk.*) (--vlan +\"[^"]+\"|--vlan +[^ ]+)(.*) *$/\1\3/' \
            -e "s/(^ *command *=.*vrouter-dpdk.*)/\\1 ${dpdk_vlan}/" \
             ${VROUTER_DPDK_INI}
    fi
}

##
## Bind vRouter/DPDK Interface(s) to DPDK Drivers
## The function is used in pre/post start scripts
##
vrouter_dpdk_if_bind() {
    echo "$(date): Binding interfaces to DPDK drivers..."

    _dpdk_conf_read

    if [ ! -f /sys/class/net/${DPDK_PHY}/address ]; then
        echo "$(date): Error binding physical interface ${DPDK_PHY}: device found"
        ${DPDK_BIND} --status
        return 1
    fi

    modprobe igb_uio
    # multiple kthreads for port monitoring
    modprobe rte_kni kthread_mode=multiple

    _dpdk_system_bond_info_collect
    _dpdk_vrouter_ini_update
    # bind physical device(s) to DPDK driver
    for slave in ${DPDK_BOND_SLAVES}; do
        echo "Binding device ${slave} to DPDK igb_uio driver..."
        ${DPDK_BIND} --force --bind=igb_uio ${slave}
    done

    ${DPDK_BIND} --status

    echo "$(date): Done binding interfaces."
}

##
## Collect Bonding Information from vRouter/DPDK INI File
## Returns:
##     DPDK_BOND_PCI_NAMES - list of bond device members or just one non-bond device
##
_dpdk_vrouter_ini_bond_info_collect() {
    if [ -n "${_DPDK_VROUTER_INI_BOND_INFO_COLLECT}" ]; then
        return
    fi
    _DPDK_VROUTER_INI_BOND_INFO_COLLECT=1

    _dpdk_conf_read

    ## Look for slave PCI addresses of vRouter --vdev argument
    DPDK_BOND_PCIS=`sed -nr \
        -e '/^ *command *=/ {
            s/slave=/\x1/g
            s/[^\x1]+//
            s/\x1([0-9:\.]+)[^\x1]+/ \1/g
            p
        }' \
        ${VROUTER_DPDK_INI}`
    DPDK_BOND_PCIS="${DPDK_BOND_PCIS# }"
    if [ -z "${DPDK_BOND_PCIS}" ]; then
        # fallback to Agent configuration for a single interface
        DPDK_BOND_PCIS="${DPDK_PHY_PCI}"
    fi

    ## Look up a driver name for all the devices
    DPDK_BOND_PCI_NAMES=""
    for slave_pci in ${DPDK_BOND_PCIS}; do
        slave_pci_name=`echo ${slave_pci} | tr ':.' '_'`
        if [ -n "${slave_pci_name}" ]; then
            DPDK_BOND_PCI_NAMES="${DPDK_BOND_PCI_NAMES} ${slave_pci_name}"
        fi
        slave_driver=`lspci -vmmks ${slave_pci} | grep 'Module:' | cut -f 2`
        eval DPDK_BOND_${slave_pci_name}_PCI="${slave_pci}"
        eval DPDK_BOND_${slave_pci_name}_DRIVER="${slave_driver}"
    done
    DPDK_BOND_PCI_NAMES="${DPDK_BOND_PCI_NAMES# }"
}

##
## Unbind vRouter/DPDK Interface(s) Back to System Drivers
## The function is used in pre/post start scripts
##
vrouter_dpdk_if_unbind() {
    echo "$(date): Unbinding interfaces back to system drivers..."

    _dpdk_conf_read
    echo "$(date): Waiting for vRouter/DPDK to stop..."
    loops=0
    while _is_vrouter_dpdk_running
    do
        sleep 2
        loops=$(($loops + 1))
        if [ $loops -ge 60 ]; then
            echo "$(date): Error stopping ${VROUTER_SERVICE} service: vRouter/DPDK is still running"
            return 1
        fi
    done

    _dpdk_vrouter_ini_bond_info_collect

    for slave_pci_name in ${DPDK_BOND_PCI_NAMES}; do
        eval slave_pci=\${DPDK_BOND_${slave_pci_name}_PCI}
        eval slave_driver=\${DPDK_BOND_${slave_pci_name}_DRIVER}

        echo "Binding PCI device ${slave_pci} back to ${slave_driver} driver..."
        ${DPDK_BIND} --force --bind=${slave_driver} ${slave_pci}
    done

    ${DPDK_BIND} --status

    rmmod rte_kni
    rmmod igb_uio

    echo "$(date): Done unbinding interfaces."
}
