#
# Copyright (c) 2016 Juniper Networks, Inc. All rights reserved.
#

import sys
import os
import json

_FILE_SUFFIX_DESCRIPTIONS = {
    "_logs" :
        { "type" : "All Logs",
          "title" : "Systemlog and Objectlog",
          "description" : "All types of system log messages",
        },
    "_logs.emerg" :
        { "type" : "Emergency Logs",
          "title" : "Emergency Systemlog and Objectlog",
          "description" : "System panic or other condition that causes the system to stop functioning"
        },
    "_logs.alert" :
        { "type" : "Alert Logs",
          "title" : "Alert Systemlog and Objectlog",
          "description" : "Conditions that require immediate correction, such as a corrupted system database"
        },
    "_logs.crit" :
        { "type" : "Critical Logs",
          "title" : "Critical Systemlog and Objectlog",
          "description" : "Critical conditions, such as hard errors"
        },
    "_logs.error" :
        { "type" : "Error Logs",
          "title" : "Error Systemlog and Objectlog",
          "description" : "Non-urgent failures - these should be relayed to developers or admins"
        },
    "_logs.warn" :
        { "type" : "Warning Logs",
          "title" : "Warning Systemlog and Objectlog",
          "description" : "Warning messages - not an error, but indication that an error will occur if action is not taken"
        },
    "_logs.notice" :
        { "type" : "Notice Logs",
          "title" : "Notice Systemlog and Objectlog",
          "description" : "Events that are unusual but not error conditions"
        },
    "_logs.info" :
        { "type" : "Informational Logs",
          "title" : "Informational Systemlog and Objectlog",
          "description" : "Normal operational messages"
        },
    "_logs.debug" :
        { "type" : "Debugging Logs",
          "title" : "Debugging Systemlog and Objectlog",
          "description" : "Information useful to developers for debugging the system"
        },
    "_logs.invalid" :
        { "type" : "Unknown Severity Logs",
          "title" : "Unknown Severity Systemlog and Objectlog",
          "description" : "Messages with unknown severity"
        },
    "_uves" :
        { "type" : "UVES",
          "title" : "UVE",
          "description" : "Messages related to User Visible Entities (UVEs)"
        },
    "_traces" :
        { "type" : "Traces",
          "title" : "Trace",
          "description" : "Trace messages useful to developers for debugging"
        },
    "_introspect" :
        { "type" : "Request-Response",
          "title" : "Request and Response",
          "description" : "Request and response messages used in HTTP Introspect"
        },
}

_DOC_SCHEMA_FILE_SUFFIX = ".doc.schema.json"
_MODULE_FILE_PREFIX = "module"
_HTML_FILE_SUFFIX = ".html"
_INDEX_FILE_PREFIX = "index"

class DocIndexGenerator(object):

    def __init__(self, cdir):
        self._cdir = cdir
    # end __init__

    def _create_html_module_list_file(self, dirpath, fsuffix, messages_dict):
        if fsuffix == "_uves":
            return
        module_fname = _MODULE_FILE_PREFIX + fsuffix + _HTML_FILE_SUFFIX
        module_fpath = os.path.join(dirpath, module_fname)
        if not messages_dict:
            if os.path.exists(module_fpath):
                os.remove(module_fpath)
            return
        with open(module_fpath, "w+") as fp:
            fp.write("<html>\n")
            fp.write("<head>" + _FILE_SUFFIX_DESCRIPTIONS[fsuffix]["title"] + \
                " Message Documentation</head>\n")
            fp.write("<link href=\"/doc-style.css\" rel=\"stylesheet\" " + \
                "type=\"text/css\"/>\n")
            fp.write("<p>\n")
            fp.write("<table><tr><th>Messages</th></tr>\n")
            for mname, minfo in iter(sorted(messages_dict.items())):
                fp.write("<tr><td><a href=\"" + minfo["href"] + "\">" + \
                    mname + "</a></td></tr>\n")
            fp.write("</table>\n")
            fp.write("</p>\n")
            fp.write("</html>\n")
    # end _create_html_module_list_file

    def _create_doc_schema_module_list_file(self, dirpath, module_fname,
                                            schema_dict):
        module_fpath = os.path.join(dirpath, module_fname)
        if not schema_dict["messages"]:
            if os.path.exists(module_fpath):
                os.remove(module_fpath)
            return
        with open(module_fpath, "w+") as mfp:
            mfp.write(json.dumps(schema_dict, sort_keys=True, indent=2))
    # end _create_doc_schema_module_list_file

    def _create_module_list_file(self, fsuffix):
        module_fname = _MODULE_FILE_PREFIX + fsuffix + _DOC_SCHEMA_FILE_SUFFIX
        for dirpath, dirnames, _ in os.walk(self._cdir):
            for dirname in dirnames:
                schema_dict = {"messages": {}}
                for sdirpath, _, sfilenames in \
                        os.walk(os.path.join(dirpath, dirname)):
                    for sfilename in sfilenames:
                        if sfilename.endswith(fsuffix + \
                                _DOC_SCHEMA_FILE_SUFFIX) and \
                                sfilename != module_fname:
                            with open(os.path.join(sdirpath, sfilename), 'r') \
                                    as sfp:
                                sdict = json.loads(sfp.read())
                                schema_dict["messages"].\
                                    update(sdict["messages"])
                # Now write the module level file - HTML and DOC schema
                self._create_html_module_list_file(sdirpath, fsuffix, \
                    schema_dict["messages"])
                self._create_doc_schema_module_list_file(sdirpath,
                    module_fname, schema_dict)
    # end _create_module_list_file

    def _create_html_module_index_file(self):
        for dirpath, dirnames, _ in os.walk(self._cdir):
            for dirname in dirnames:
                for sdirpath, _, sfilenames in \
                        os.walk(os.path.join(dirpath, dirname)):
                    with open(os.path.join(sdirpath, _INDEX_FILE_PREFIX + \
                            _HTML_FILE_SUFFIX), "w+") as fp:
                        fp.write("<html>\n")
                        fp.write("<head>Message Documentation for" + \
                            dirname + "</head>\n")
                        fp.write("<link href=\"/doc-style.css\" " + \
                            "rel=\"stylesheet\" type=\"text/css\"/>\n")
                        fp.write("<p>\n")
                        fp.write("<table><tr><th>Message Types</th>" + \
                            "<th>Description</th></tr>\n")
                        for fsuffix, fdesc in \
                                iter(sorted(_FILE_SUFFIX_DESCRIPTIONS.items())):
                            if fsuffix == "_uves":
                                continue
                            mfname = _MODULE_FILE_PREFIX + fsuffix + \
                                _HTML_FILE_SUFFIX
                            if mfname in sfilenames:
                                fp.write("<tr><td><a href=" + mfname + ">" + \
                                    fdesc["type"] + "</a></td><td>" + \
                                    fdesc["description"] + "</td></tr>\n")
                        fp.write("</table>\n")
                        fp.write("</p>\n")
                        fp.write("</html>\n")
    # end _create_html_module_index_file

    def _create_html_global_list_file_uves(self, dirpath, fsuffix, messages_dict):
        fname = _INDEX_FILE_PREFIX + fsuffix + _HTML_FILE_SUFFIX
        fpath = os.path.join(dirpath, fname)
        if not messages_dict:
            if os.path.exists(fpath):
                os.remove(fpath)
            return
        with open(fpath, "w+") as fp:
            fp.write("<html>\n")
            fp.write("<head>" + _FILE_SUFFIX_DESCRIPTIONS[fsuffix]["title"] + \
                " Message Documentation</head>\n")
            fp.write("<link href=\"/doc-style.css\" rel=\"stylesheet\" " + \
                "type=\"text/css\"/>\n")
            fp.write("<p>\n")
            fp.write("<table><tr><th>Module</th><th>Messages</th></tr>\n")
            object_list = dict()
            for mname, minfo in iter(sorted(messages_dict.items())):
                if ("object" in minfo.keys()):
                    if minfo["object"] in object_list.keys():
                        object_list[minfo["object"]].append((mname,
                            minfo["href"]))
                    else:
                        object_list[minfo["object"]] = [(mname, minfo["href"])]
            for obj, minfo_list in object_list.iteritems():
                fp.write("<tr><td>" + obj + "</td>")
                first = True
                for minfo in minfo_list:
                    print minfo
                    if first:
                        fp.write("<td>")
                    fp.write("<a href=\"" + minfo[1] + "\">" + minfo[0] +
                            "</a><br/>\n")
                    if first:
                        first = False
                fp.write("</td></tr>")
            fp.write("</table>\n")
            fp.write("</p>\n")
            fp.write("</html>\n")
    # end _create_html_global_list_file_uves

    def _create_html_global_list_file(self, dirpath, fsuffix, messages_dict):
        if fsuffix == "_uves":
            return self._create_html_global_list_file_uves(dirpath, fsuffix,
                    messages_dict)
        fname = _INDEX_FILE_PREFIX + fsuffix + _HTML_FILE_SUFFIX
        fpath = os.path.join(dirpath, fname)
        if not messages_dict:
            if os.path.exists(fpath):
                os.remove(fpath)
            return
        with open(fpath, "w+") as fp:
            fp.write("<html>\n")
            fp.write("<head>" + _FILE_SUFFIX_DESCRIPTIONS[fsuffix]["title"] + \
                " Message Documentation</head>\n")
            fp.write("<link href=\"/doc-style.css\" rel=\"stylesheet\" " + \
                "type=\"text/css\"/>\n")
            fp.write("<p>\n")
            fp.write("<table><tr><th>Messages</th></tr>\n")
            for mname, minfo in iter(sorted(messages_dict.items())):
                fp.write("<tr><td><a href=\"" + minfo["href"] + "\">" + \
                    mname + "</a></td></tr>\n")
            fp.write("</table>\n")
            fp.write("</p>\n")
            fp.write("</html>\n")
    # end _create_html_global_list_file

    def _create_doc_schema_global_list_file(self, dirpath, fsuffix,
                                            schema_dict):
        fname = _INDEX_FILE_PREFIX + fsuffix + _DOC_SCHEMA_FILE_SUFFIX
        fpath = os.path.join(dirpath, fname)
        if not schema_dict["messages"]:
            if os.path.exists(fpath):
                os.remove(fpath)
            return
        with open(fpath, "w+") as fp:
            fp.write(json.dumps(schema_dict, sort_keys=True, indent=2))
    # end _create_doc_schema_global_list_file

    def _create_global_list_file(self, fsuffix):
        fname = _MODULE_FILE_PREFIX + fsuffix + _DOC_SCHEMA_FILE_SUFFIX
        for dirpath, dirnames, _ in os.walk(self._cdir):
            schema_dict = {"messages": {}}
            for dirname in dirnames:
                for sdirpath, _, sfilenames in \
                        os.walk(os.path.join(dirpath, dirname)):
                    if fname in sfilenames:
                        with open(os.path.join(sdirpath, fname), 'r') as sfp:
                            sdict = json.loads(sfp.read())
                            # Update the href to include dirname
                            mdict = sdict["messages"]
                            for minfo in mdict.itervalues():
                                minfo["href"] = dirname + "/" + minfo["href"]
                            schema_dict["messages"].update(mdict)
            # Now write the list file - HTML and DOC schema
            self._create_html_global_list_file(dirpath, fsuffix, \
                schema_dict["messages"])
            self._create_doc_schema_global_list_file(dirpath, fsuffix, \
                schema_dict)
    # end _create_global_list_file

    def _create_html_global_index_file(self):
        index_fname = _INDEX_FILE_PREFIX + _HTML_FILE_SUFFIX
        with open(os.path.join(self._cdir, index_fname), "w+") as fp:
            fp.write("<html>\n")
            fp.write("<head>Contrail Message Documentation</head>\n")
            fp.write("<p>\n")
            fp.write("<table><tr><th>Modules</th></tr>\n")
            fp.write("<link href=\"/doc-style.css\" rel=\"stylesheet\" " + \
                "type=\"text/css\"/>\n")
            cdirlist = os.listdir(self._cdir)
            for dirname in cdirlist:
                dirpath = os.path.join(self._cdir, dirname)
                if os.path.isdir(dirpath):
                    mfname = os.path.join(dirname, index_fname)
                    fp.write("<tr><td><a href=" + mfname + ">" + dirname + \
                        "</a></td></tr>\n")
            fp.write("</table>\n");
            fp.write("</p>\n")
            fp.write("<p>\n")
            fp.write("<table><tr><th>Message Types</th>" + \
                "<th>Description</th></tr>\n")
            for fsuffix, fdesc in \
                  iter(sorted(_FILE_SUFFIX_DESCRIPTIONS.items())):
                ifname = _INDEX_FILE_PREFIX + fsuffix + \
                    _HTML_FILE_SUFFIX
                if ifname in cdirlist:
                    fp.write("<tr><td><a href=" + ifname + ">" + \
                             fdesc["type"] + "</a></td><td>" + \
                             fdesc["description"] + "</td></tr>\n")
            fp.write("</table>\n")
            fp.write("</p>\n")
            fp.write("</html>\n")
    # end _create_html_global_index_file

    def _create_module_files(self):
        for fsuffix in _FILE_SUFFIX_DESCRIPTIONS.keys():
            self._create_module_list_file(fsuffix)
        self._create_html_module_index_file()
    # end _create_module_files

    def _create_global_files(self):
        for fsuffix in _FILE_SUFFIX_DESCRIPTIONS.keys():
            self._create_global_list_file(fsuffix)
        self._create_html_global_index_file()
    # end _create_index_files

    def run(self):
        self._create_module_files()
        self._create_global_files()
    # end run

# end class DocIndexGenerator

def main():
    if len(sys.argv) != 2:
        print 'Usage is python doc_index_generator.py <directory>'
        exit(-1)
    doc_index_generator = DocIndexGenerator(sys.argv[1])
    doc_index_generator.run()
# end main

if __name__ == "__main__":
    main()
