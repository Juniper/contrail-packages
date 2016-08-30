#!/bin/bash
# Check if the input is a directory
if [ ! -d $1 ]; then
    exit 0
fi
BASE_DIR=$1
INDEX_FILE=$BASE_DIR/index.html
LOGS_INDEX_FILE=$BASE_DIR/logs_index.html
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
            $CAT $file >> $index_file
        fi
    done
    echo "</table>" >> $index_file
    echo "</html>" >> $index_file
}

create_module_index_file() {
    local index_file=$1
    local module_name=$2
    # Generate the index file from the directory listing of base dir
    if [ -e $index_file ]; then
        echo "<html>" > $index_file
    else
        echo "<html>" >> $index_file
    fi
    echo "<head>Message Documentation for $module_name</head>" >> $index_file
    echo "<link href=\"/doc-style.css\" rel=\"stylesheet\" type=\"text/css\"/>" >> $index_file
    echo "<table><tr><th>Message Types</th></tr>" >> $index_file
    echo "<tr><td><a href=logs_index.html>Logs</a></td></tr>" >> $index_file
    echo "<tr><td><a href=uves_index.html>UVES</a></td></tr>" >> $index_file
    echo "<tr><td><a href=traces_index.html>Traces</a></td></tr>" >> $index_file
    echo "<tr><td><a href=introspect_index.html>Request-Response</a></td></tr>" >> $index_file
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

create_index_files $INDEX_FILE
create_message_index_file $LOGS_INDEX_FILE "logs" "Systemlog and Objectlog"
create_message_index_file $TRACES_INDEX_FILE "traces" "Trace"
create_message_index_file $UVES_INDEX_FILE "uves" "UVE"
create_message_index_file $INTROSPECT_INDEX_FILE "introspect" "Request and Response"
create_module_message_file $MODULE_LOGS_FILE "logs"
create_module_message_file $MODULE_TRACES_FILE "traces"
create_module_message_file $MODULE_UVES_FILE "uves"
create_module_message_file $MODULE_INTROSPECT_FILE "introspect"
