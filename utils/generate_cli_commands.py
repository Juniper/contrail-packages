#!/usr/bin/env python

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


class CompleteNoCode(CompleteShellBase):
    """completion with no code
    """
    def __init__(self, name, output):
        super(CompleteNoCode, self).__init__(name, output)

    def get_header(self):
        return ''

    def get_trailer(self):
        return ''


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

    def __init__(self, install_dir, base_dir, package_dir):
        self.entry_points_dict = dict()
        self.entry_points_dict['console_scripts'] = dict()
        self.entry_points_dict['console_scripts']['supervisord_analytics_files'] = []
        self.entry_points_dict['console_scripts']['supervisord_config_files'] = []
        self.entry_points_dict['console_scripts']['supervisord_control_files'] = []
        self.entry_points_dict['console_scripts']['supervisord_vrouter_files'] = []
        self.entry_points_dict["ContrailCli"] = []
        self.mapping_files = dict()
        self.commands = dict()
        self._install_dir = install_dir
        self._base_dir = base_dir
        self._doc_dir = base_dir + "/usr/share/doc/contrail-docs/html/messages/"
        supervisor_files_dir = base_dir + "/etc/contrail/"
        extn = '.ini'
        module_list = dict()
        self.module_to_cli_mapping = dict()
        module_list['supervisord_analytics_files'] = []
        module_list['supervisord_control_files'] = []
        module_list['supervisord_config_files'] = []
        module_list['supervisord_vrouter_files'] = []
        for key in module_list.keys():
            for dirpath, dirname, files in os.walk(supervisor_files_dir+key):
                for name in files:
                    if name.lower().endswith(extn):
                        module_list[key].append(os.path.join(dirpath, name))
                        self.module_to_cli_mapping[name] = key
        sys.path.append(package_dir)

    def _get_mapping_files(self, svc_name):
        names = svc_name.split(':')
        svc_name = names[0]
        if svc_name in self.mapping_files.keys():
            return self.mapping_files[svc_name]
        return []

    def _define_cli_entry_points(self):
        myfile = open(self._install_dir+"/contrail_cli/ContrailCli/main.py", "a")
        from sandesh_common.vns.constants import ServiceHttpPortMap
        for svc_name in ServiceHttpPortMap:
            http_port = ServiceHttpPortMap[svc_name]
            svc_mapping_files = self._get_mapping_files(svc_name)
            if len(svc_mapping_files) == 0:
                continue
            svc_name = svc_name.replace('-', '_')
            myfile.write("\ndef {0}_cli(argv=sys.argv[1:]):\n".format(svc_name))
            myfile.write("    cliapp = ContrailCliApp({0})\n".format(http_port))
            myfile.write("    return cliapp.run(argv)\n")
        myfile.close()
        return
    #end _define_cli_entry_points
    
    def _populate_command_list_file(self):
        commandfile = open(self._install_dir+"/commandlist.py", "w")
        commandfile.write("\ncommands_list = "+str(self.commands)+"\n\n")
        commandfile.close()
        entry_points_file = open(self._install_dir+"/entry_points.py", "w")
        entry_points_file.write("\nentry_points_dict = "+str(self.entry_points_dict)+"\n")
        entry_points_file.close()
        return
    #end _populate_command_list_file
        
    def _create_entry_points_and_commands(self, mapping_files):
        from sandesh_common.vns.constants import ServiceHttpPortMap
        for svc_name in ServiceHttpPortMap:
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
                for cmd in data.keys():
                    list_commands.append((cmd, data[cmd]))
    
            console_command = str(svc_name) + "-cli"
            console_script_list = []
            console_script_list.append("{0} = {1}".format(console_command,\
                "ContrailCli.main:{0}_cli".format(str(svc_name.replace('-', '_')))))
            module_cli = self.module_to_cli_mapping[svc_name+".ini"]
            self.entry_points_dict['console_scripts'][module_cli].append(console_script_list)
    
            self.commands[console_command] = list_commands
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
        extn = '_introspect_cli.json'
        for directory in os.listdir(topdir):
            self.mapping_files[directory] = []
            for dirpath, dirnames, files in os.walk(topdir+directory):
                for name in files:
                    if name.lower().endswith(extn):
                        self.mapping_files[directory].append(os.path.join(dirpath, name))
    #end _parse_cli_mapping_files
    
    def _create_bash_completion_script(self):
        cli_fpath = self._base_dir+"/etc/bash_completion.d/bashrc_contrail_analytics_cli"
        if os.path.exists(cli_fpath):
            os.remove(cli_fpath)

        bash_completion_file = open(cli_fpath, "w+")
        for ep in self.entry_points_dict['console_scripts'].values():
            if ep == []:
                continue
            cmds = ep[0][0].split('=')[0].strip()
            completer = CompleteCommand(cmds, self.commands[cmds])
            completer.take_action(bash_completion_file)
        bash_completion_file.close()

    def run(self):
        self._parse_cli_mapping_files()
        self._create_entry_points_and_commands(self.mapping_files)
        self._populate_command_list_file()
        self._define_cli_entry_points()
        self._create_bash_completion_script()

def main():
    if len(sys.argv) != 4:
        print 'Usage is python generate_commands.py <install-directory> <base-directory> <package-dir>'
        exit(-1)
    contrail_cli_generator = ContrailCliGenerator(sys.argv[1], sys.argv[2], sys.argv[3])
    contrail_cli_generator.run()
# end main

if __name__ == "__main__":
    main()
