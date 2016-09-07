#!/bin/bash
# Check if the input is a directory
if [ ! -d $1 ]; then
    exit 0
fi
BASE_DIR=$1
INDEX_FILE=$BASE_DIR/index.html
LOGS_INDEX_FILE=$BASE_DIR/logs_index.html
LOGS_LEVEL_EMERG_INDEX_FILE=$BASE_DIR/logs_level_emerg_index.html
LOGS_LEVEL_ALERT_INDEX_FILE=$BASE_DIR/logs_level_alert_index.html
LOGS_LEVEL_CRIT_INDEX_FILE=$BASE_DIR/logs_level_crit_index.html
LOGS_LEVEL_ERROR_INDEX_FILE=$BASE_DIR/logs_level_error_index.html
LOGS_LEVEL_WARN_INDEX_FILE=$BASE_DIR/logs_level_warn_index.html
LOGS_LEVEL_NOTICE_INDEX_FILE=$BASE_DIR/logs_level_notice_index.html
LOGS_LEVEL_INFO_INDEX_FILE=$BASE_DIR/logs_level_info_index.html
LOGS_LEVEL_DEBUG_INDEX_FILE=$BASE_DIR/logs_level_debug_index.html
LOGS_LEVEL_INVALID_INDEX_FILE=$BASE_DIR/logs_level_invalid_index.html
TRACES_INDEX_FILE=$BASE_DIR/traces_index.html
UVES_INDEX_FILE=$BASE_DIR/uves_index.html
INTROSPECT_INDEX_FILE=$BASE_DIR/introspect_index.html
MODULE_LOGS_FILE=$BASE_DIR/module_logs.html
MODULE_TRACES_FILE=$BASE_DIR/module_traces.html
MODULE_UVES_FILE=$BASE_DIR/module_uves.html
MODULE_INTROSPECT_FILE=$BASE_DIR/module_introspect.html
BASE_DIR_LISTING=$BASE_DIR/*
BASENAME=/usr/bin/basename
DIRNAME=/usr/bin/dirname
CAT=/bin/cat
RM=/bin/rm

create_message_index_file() {
    local index_file=$1
    local file_type=$2
    local file_description=$3

    # Generate the index file from the directory list of base dir
    if [ -e $index_file ]; then
        echo "<html>" > $index_file
    else
        echo "<html>" >> $index_file
    fi
    echo "<head>$file_description Message Documentation</head>" >> $index_file
    echo "<link href=\"/doc-style.css\" rel=\"stylesheet\" type=\"text/css\"/>" >> $index_file
    echo "<table><tr><th>Messages</th></tr>" >> $index_file
    local init_done=0
    for file in $BASE_DIR_LISTING; do
        if ! [ -d $file ]; then
            local filename=$($BASENAME $file)
            local extension="${filename##*.}"
            # Ignore non HTML files
            if [ $extension != "html" ]; then
                continue
            fi
            filename=$($BASENAME $file .html)
            # Ignore index.html
            if [ $filename == "index" ]; then
                continue
            fi
            # Ignore non fle type html files
            if ! [[ $filename = *_$file_type.list ]]; then
                continue
            fi
            if [ -s $file ]; then
                init_done=1
                $CAT $file >> $index_file
            fi
        fi
    done
    echo "</table>" >> $index_file
    echo "</html>" >> $index_file
    if (($init_done == 0)); then
        $RM $index_file
    fi
}

create_module_index_file() {
    local index_file=$1
    local module_name=$2
    local index_file_dir=$($DIRNAME $index_file)
    # Generate the index file from the directory listing of base dir
    if [ -e $index_file ]; then
        echo "<html>" > $index_file
    else
        echo "<html>" >> $index_file
    fi
    echo "<head>Message Documentation for $module_name</head>" >> $index_file
    echo "<link href=\"/doc-style.css\" rel=\"stylesheet\" type=\"text/css\"/>" >> $index_file
    echo "<table><tr><th>Message Types</th><th>Description</th></tr>" >> $index_file
    if [ -e $index_file_dir/logs_index.html ]; then
        echo "<tr><td><a href=logs_index.html>All Logs</a></td><td>All types of system log messages</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_emerg_index.html ]; then
        echo "<tr><td><a href=logs_level_emerg_index.html>Emergency Logs</a></td><td>System panic or other condition that causes the system to stop functioning</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_alert_index.html ]; then
        echo "<tr><td><a href=logs_level_alert_index.html>Alert Logs</a></td><td>Conditions that require immediate correction, such as a corrupted system database</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_crit_index.html ]; then
        echo "<tr><td><a href=logs_level_crit_index.html>Critical Logs</a></td><td>Critical conditions, such as hard errors</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_error_index.html ]; then
        echo "<tr><td><a href=logs_level_error_index.html>Error Logs</a></td><td>Non-urgent failures - these should be relayed to developers or admins</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_warn_index.html ]; then
        echo "<tr><td><a href=logs_level_warn_index.html>Warning Logs</a></td><td>Warning messages - not an error, but indication that an error will occur if action is not taken</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_notice_index.html ]; then
        echo "<tr><td><a href=logs_level_notice_index.html>Notice Logs</a></td><td>Events that are unusual but not error conditions</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_info_index.html ]; then
        echo "<tr><td><a href=logs_level_info_index.html>Informational Logs</a></td><td>Normal operational messages</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_debug_index.html ]; then
        echo "<tr><td><a href=logs_level_debug_index.html>Debug Logs</a></td><td>Information useful to developers for debugging the system</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/logs_level_invalid_index.html ]; then
        echo "<tr><td><a href=logs_level_invalid_index.html>Unknown severity logs</a></td><td>Messages with unknown severity</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/uves_index.html ]; then
        echo "<tr><td><a href=uves_index.html>UVES</a></td><td>Messages related to User Visible Entities (UVEs)</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/traces_index.html ]; then
        echo "<tr><td><a href=traces_index.html>Traces</a></td><td>Trace messages useful to developers for debugging</td></tr>" >> $index_file
    fi
    if [ -e $index_file_dir/introspect_index.html ]; then
        echo "<tr><td><a href=introspect_index.html>Request-Response</a></td><td>Request and response messages used in HTTP Introspect</td></tr>" >> $index_file
    fi
    echo "</table>" >> $index_file
    echo "</html>" >> $index_file
}

create_index_files() {
    local index_file=$1
    # Generate the index file from the directory listing of base dir
    if [ -e $index_file ]; then
        echo "<html>" > $index_file
    else
        echo "<html>" >> $index_file
    fi
    echo "<head>OpenContrail Message Documentation</head>" >> $index_file
    echo "<link href=\"/doc-style.css\" rel=\"stylesheet\" type=\"text/css\"/>" >> $index_file
    echo "<table><tr><th>Module</th></tr>" >> $index_file
    for file in $BASE_DIR_LISTING; do
        if [ -d $file ]; then
            local dirname=$($BASENAME $file)
            echo "<tr><td><a href=$dirname/index.html>$dirname</a></td></tr>" >> $index_file
            create_module_index_file $file/index.html $dirname
        fi
    done
    echo "</table>" >> $index_file
    echo "</html>" >> $index_file
}

create_module_message_file() {
    local index_file=$1
    local file_type=$2
    if ! [ -e $index_file ]; then
        echo > $index_file
    fi
    for file in $BASE_DIR_LISTING; do
        local filename=$($BASENAME $file)
        local extension="${filename##*.}"
        local dirname=$($DIRNAME $file)
        # Ignore non HTML files
        if [ $extension != "html" ]; then
            continue
        fi
        filename=$($BASENAME $file .html)
        # Ignore index files
        if [ $filename == "index" ]; then
            continue
        fi
        # Ignore non fle type html files
        if ! [[ $filename = *_$file_type ]]; then
            continue
        fi
        # Ignore if list html file is zero
        if ! [ -s $dirname/$filename.list.html ]; then
            continue
        fi
        $CAT $file >> $index_file
    done
}

create_message_index_file $LOGS_INDEX_FILE "logs" "Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_EMERG_INDEX_FILE "logs.emerg" "Emergency Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_ALERT_INDEX_FILE "logs.alert" "Alert Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_CRIT_INDEX_FILE "logs.crit" "Critical Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_ERROR_INDEX_FILE "logs.error" "Error Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_WARN_INDEX_FILE "logs.warn" "Warning Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_NOTICE_INDEX_FILE "logs.notice" "Notice Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_INFO_INDEX_FILE "logs.info" "Informational Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_DEBUG_INDEX_FILE "logs.debug" "Debugging Systemlog and Objectlog"
create_message_index_file $LOGS_LEVEL_INVALID_INDEX_FILE "logs.invalid" "Unknown Severity Systemlog and Objectlog"
create_message_index_file $TRACES_INDEX_FILE "traces" "Trace"
create_message_index_file $UVES_INDEX_FILE "uves" "UVE"
create_message_index_file $INTROSPECT_INDEX_FILE "introspect" "Request and Response"
create_index_files $INDEX_FILE
create_module_message_file $MODULE_LOGS_FILE "logs"
create_module_message_file $MODULE_TRACES_FILE "traces"
create_module_message_file $MODULE_UVES_FILE "uves"
create_module_message_file $MODULE_INTROSPECT_FILE "introspect"
