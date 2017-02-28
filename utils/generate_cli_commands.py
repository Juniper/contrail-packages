#!/usr/bin/env python
#
# Copyright (c) 2016 Juniper Networks, Inc. All rights reserved.
#


import os
import sys
import json
import six

class CompleteDictionary:
    """dictionary for bash completion
    """

    def __init__(self):
        self._dictionary = {}

    def add_command(self, command):
        dicto = self._dictionary
        for subcmd in command[:-1]:
            dicto = dicto.setdefault(subcmd, {})
        dicto[command[-1]] = ''

    def get_commands(self):
        return ' '.join(k for k in sorted(self._dictionary.keys()))

    def _get_data_recurse(self, dictionary, path):
        ray = []
        keys = sorted(dictionary.keys())
        for cmd in keys:
            name = path + "_" + cmd if path else cmd
            value = dictionary[cmd]
            if isinstance(value, six.string_types):
                ray.append((name, value))
            else:
                cmdlist = ' '.join(sorted(value.keys()))
                ray.append((name, cmdlist))
                ray += self._get_data_recurse(value, name)
        return ray

    def get_data(self):
        return sorted(self._get_data_recurse(self._dictionary, ""))


class CompleteShellBase(object):
    """base class for bash completion generation
    """
    def __init__(self, name, output):
        self.name = str(name)
        self.output = output

    def write(self, cmdo, data):
        self.output.write(self.get_header())
        self.output.write("  cmds='{0}'\n".format(cmdo))
        for datum in data:
            self.output.write('  cmds_{0}=\'{1}\'\n'.format(*datum))
        self.output.write(self.get_trailer())

class CompleteBash(CompleteShellBase):
    """completion for bash
    """
    def __init__(self, name, output):
        super(CompleteBash, self).__init__(name, output)

    def get_header(self):
        return ('_' + self.name + """()
{
  local cur prev words
  COMPREPLY=()
  _get_comp_words_by_ref -n : cur prev words

  # Command data:
""")

    def get_trailer(self):
        return ("""
  cmd=""
  words[0]=""
  completed="${cmds}"
  for var in "${words[@]:1}"
  do
    if [[ ${var} == -* ]] ; then
      break
    fi
    if [ -z "${cmd}" ] ; then
      proposed="${var}"
    else
      proposed="${cmd}_${var}"
    fi
    local i="cmds_${proposed}"
    local comp="${!i}"
    if [ -z "${comp}" ] ; then
      break
    fi
    if [[ ${comp} == -* ]] ; then
      if [[ ${cur} != -* ]] ; then
        completed=""
        break
      fi
    fi
    cmd="${proposed}"
    completed="${comp}"
  done

  if [ -z "${completed}" ] ; then
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
  else
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
  fi
  return 0
}
complete -F _""" + self.name + ' ' + self.name + '\n')


class CompleteCommand():
    """print bash completion command
    """

    def __init__(self, cmd_name, command_list):
        self._cmd_name = cmd_name
        self._command_list = command_list

    def take_action(self, outfile):
        dicto = CompleteDictionary()
        for cmd in self._command_list:
            command = cmd[1].keys()[0].split()
            dicto.add_command(command)

        shell = CompleteBash(self._cmd_name, outfile)
        shell.write(dicto.get_commands(), dicto.get_data())

        return 0

class ContrailCliGenerator(object):

    def __init__(self, install_dir, base_dir):
        self.entry_points_dict = dict()
        self.entry_points_dict['console_scripts'] = dict()
        self.entry_points_dict["ContrailCli"] = []
        self.mapping_files = dict()
        self.commands = dict()
        self._install_dir = install_dir
        self._base_dir = base_dir
        self._doc_dir = base_dir + "/usr/share/doc/contrail-docs/html/messages/"
        # Hardcoding the mapping for modules
        self.module_to_cli_mapping = {
                        'contrail-alarm-gen' :        'contrail_analytics_cli',
                        'contrail-analytics-api' :    'contrail_analytics_cli',
                        'contrail-collector' :        'contrail_analytics_cli',
                        'contrail-query-engine' :     'contrail_analytics_cli',
                        'contrail-snmp-collector' :   'contrail_analytics_cli',
                        'contrail-topology' :         'contrail_analytics_cli',
                        'contrail-broadview' :        'contrail_analytics_cli',
                        'contrail-api' :              'contrail_config_cli',
                        'contrail-device-manager' :   'contrail_config_cli',
                        'contrail-discovery' :        'contrail_config_cli',
                        'contrail-schema' :           'contrail_config_cli',
                        'contrail-svc-monitor' :      'contrail_config_cli',
                        'contrail-mesos-manager' :    'contrail_config_cli',
                        'contrail-kube-manager' :     'contrail_config_cli',
                        'contrail-control' :          'contrail_control_cli',
                        'contrail-dns' :              'contrail_control_cli',
                        'contrail-named' :            'contrail_control_cli',
                        'XmppServer' :                'contrail_control_cli',
                        'contrail-vrouter-agent' :    'contrail_vrouter_cli',
                        'contrail-tor-agent' :        'contrail_vrouter_cli',
                        'InventoryAgent' :            'contrail_vrouter_cli',
                        'Storage-Stats-mgr' :         'contrail_vrouter_cli',
        }
        cli_modules = ['contrail_analytics_cli', 'contrail_config_cli',
                       'contrail_control_cli', 'contrail_vrouter_cli']
        for cli_module in cli_modules:
            self.commands[cli_module] = dict()
            self.entry_points_dict['console_scripts'][cli_module] = []
    #end __init__

    def _get_mapping_files(self, svc_name):
        svc_name = svc_name.split(':')[0]
        if svc_name in self.mapping_files.keys():
            return self.mapping_files[svc_name]
        return []

    def _populate_entry_points_file(self):
        epfile = open(self._install_dir+"/contrail_cli/entry_points.py", "a")
        epfile.write("\nentry_points_dict = { 'ContrailCli' : "+str(self.entry_points_dict["ContrailCli"])+"}\n")
        epfile.close()
        for cli_module in self.entry_points_dict['console_scripts'].keys():
            if cli_module in os.listdir(self._install_dir):
                epfile = open(self._install_dir+"/"+cli_module+"/entry_points.py", "a")
                epfile.write("\nentry_points_dict = {'console_scripts' : "+str(self.entry_points_dict['console_scripts'][cli_module])+"}\n")
                epfile.close()
        return
    #end _populate_entry_points_file

    def _populate_command_list_file(self):
        for cli_module in self.commands.keys():
            if cli_module in os.listdir(self._install_dir):
                cli_module_pkg = ''.join(x.capitalize() or '_' for x in cli_module.split('_'))
                cmdfile = open(self._install_dir+"/"+cli_module+"/"+cli_module_pkg+"/commandlist.py", "a")
                cmdfile.write("\ncommands_list = "+str(self.commands[cli_module])+"\n")
                cmdfile.close()
        return
    #end _populate_command_list_file

    def _create_entry_points_and_commands(self):
        for svc_name in self.module_to_cli_mapping.keys():
            svc_mapping_files = self._get_mapping_files(svc_name)
            if len(svc_mapping_files) == 0:
                continue
            data = ""
            list_commands = []
            for mapping_file in svc_mapping_files:
                if os.path.getsize(mapping_file) == 0:
                    continue
                with open(mapping_file) as data_file:
                    data = json.load(data_file)
                if "sandesh_cli" in data.keys():
                    for cmd, tables in data["sandesh_cli"].iteritems():
                        list_commands.append((cmd, tables))

            if len(list_commands) == 0:
                continue
            console_command = str(svc_name) + "-cli"
            cli_module = self.module_to_cli_mapping[svc_name]
            cli_module_pkg = ''.join(x.capitalize() or '_' for x in cli_module.split('_'))
            console_script = "{0} = {1}.main:{2}".format(console_command,\
                cli_module_pkg, cli_module)
            self.entry_points_dict['console_scripts'][cli_module].append(console_script)

            self.commands[cli_module][console_command] = list_commands
            for command in list_commands:
                command_exists = False
                for entry_point in self.entry_points_dict["ContrailCli"]:
                    if entry_point.find("{0}".format(command[1].keys()[0])) >= 0:
                        command_exists = True
                        break
                if command_exists == False:
                    self.entry_points_dict["ContrailCli"].append("{0} = \
                            ContrailCli.contrailCli:ContrailCli".format(command[1].keys()[0]))
    #end _create_entry_points_and_commands

    def _parse_cli_mapping_files(self):
        topdir = self._doc_dir
        extn = '_introspect.doc.schema.json'
        for directory in os.listdir(topdir):
            self.mapping_files[directory] = []
            for dirpath, dirnames, files in os.walk(topdir+directory):
                for name in files:
                    if name.lower().endswith(extn):
                        self.mapping_files[directory].append(os.path.join(dirpath, name))
    #end _parse_cli_mapping_files

    def _create_bash_completion_script(self):
        cli_fpath = self._base_dir+"/etc/bash_completion.d/bashrc_contrail_cli"
        if os.path.exists(cli_fpath):
            os.remove(cli_fpath)

        bash_completion_file = open(cli_fpath, "w+")
        for ep in self.entry_points_dict['console_scripts'].values():
            if ep == []:
                continue
            cmds = ep[0].split('=')[0].strip()
            cli_module = self.module_to_cli_mapping[cmds[:cmds.find("-cli")]]
            completer = CompleteCommand(cmds, self.commands[cli_module][cmds])
            completer.take_action(bash_completion_file)
        bash_completion_file.close()

    def run(self):
        self._parse_cli_mapping_files()
        self._create_entry_points_and_commands()
        self._populate_command_list_file()
        self._populate_entry_points_file()
        self._create_bash_completion_script()

def main():
    if len(sys.argv) != 3:
        print 'Usage is python generate_commands.py <install-directory> <base-directory>'
        exit(-1)
    contrail_cli_generator = ContrailCliGenerator(sys.argv[1], sys.argv[2])
    contrail_cli_generator.run()
# end main

if __name__ == "__main__":
    main()
