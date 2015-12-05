#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import inspect
import json
from utils import stdio
from utils.stdio import CRESET, CBOLD, LGREEN
import plugins
from plugins import *
from config import ROOT_DIR, CONFIG_FILE_NAME

# Here goes the functions


def read_conf(array, key, default_value):
    """Returns the value for a conf key. If not found, returns the default_value"""
    if key in array:
        return array[key]
    else:
        return default_value


def parse_conf(file_path):
    """Returns a JSON representation of the configuration file whose path is given as argument"""
    conf_raw = open(file_path, "r").read()
    return json.loads(conf_raw)


def get_supported_project_types():
    """Registers the supported project types"""
    plugins_list = {}
    for plugin_pkg_name, plugin_pkg in inspect.getmembers(plugins, inspect.ismodule):
        plugin_variants = plugin_pkg.register_variants()
        for plugin_variant in plugin_variants:
            plugins_list[plugin_variant.key_name] = plugin_variant
    return plugins_list


def release(project_path):
    # Parse conf
    conf = parse_conf(os.path.join(project_path, CONFIG_FILE_NAME))

    # Read conf
    project_type = read_conf(conf, "projectType", "generic")
    branch = read_conf(conf, "branch", "release")
    forced_passes = read_conf(conf, "passes", "").split()

    # Check the project type
    types = get_supported_project_types()
    if project_type not in types:
        print("Unknown project type \"{}\".".format(project_type))
        return

    # Let's go!
    os.chdir(project_path)
    os.system("git checkout " + branch)
    os.system("git pull")

    # Determine plugin-specific passes
    plugin = types[project_type]()

    deploy_passes = []

    for pass_name in plugin.register_passes():
        # Check if optional task is enabled
        if pass_name[0] == "?":
            pass_name = pass_name[1:]
            if "+"+pass_name not in forced_passes:
                continue
        # Check if pass is enabled
        if "-"+pass_name in forced_passes:
            continue

        deploy_passes.append(pass_name)

    print(CBOLD+LGREEN, "\n==> Deployment starting with passes: {}".format(", ".join(deploy_passes)), CRESET)

    # Start env-specific passes
    npasses = len(deploy_passes)
    for i, pass_name in enumerate(deploy_passes):
        print(CBOLD, "\n==> Pass {} of {} [{}]".format(i+1, npasses, pass_name), CRESET)
        getattr(plugin, pass_name + "_pass")()

    # Execute custom commands
    commands = read_conf(conf, "commands", [])
    if len(commands) > 0:
        print(CBOLD + LGREEN, "\nExecuting custom commands", CRESET)

        for command in commands:
            stdio.ppexec(command)

    # The End
    print(CBOLD+LGREEN, "\n==> {} successfully deployed. Have an A1 day!\n".format(project_path), CRESET)



# Here goes the code

projects = []
# Get all projects for ROOT_DIR
for dir_name in os.listdir(ROOT_DIR):
    if os.path.isdir(ROOT_DIR + dir_name):
        dir_path = ROOT_DIR + dir_name
        config_file_path = dir_path + "/" + CONFIG_FILE_NAME

        # Look for config file for this project
        if os.path.exists(config_file_path) and os.path.isfile(config_file_path):
            # Here we should try to parse it just in case, but hey
            projects.append(dir_path)


# Check command line argument
parser = argparse.ArgumentParser(description='Easily deploy projects')
parser.add_argument('--project', default='ask_for_it')
parser.add_argument('-a', '--all', action='store_true')
args = parser.parse_args()

if args.all:
    # Deploy all projects!
    if len(projects) > 0:
        for i, project in enumerate(projects):
            project_name = os.path.basename(os.path.normpath(project))
            target_branch = read_conf(parse_conf("{}/{}".format(project, CONFIG_FILE_NAME)), "branch", "release")

            print(CBOLD+LGREEN, "\nDeploying project {} ({})".format(project_name, target_branch), CRESET)
            release(project)
    else:
        print("There is no suitable project in {}".format(ROOT_DIR))

elif args.project == 'ask_for_it':
    print("Please select a project to sync")
    for i, project in enumerate(projects):
        project_name = os.path.basename(os.path.normpath(project))
        target_branch = read_conf(parse_conf("{}/{}".format(project, CONFIG_FILE_NAME)), "branch", "release")

        print("\t[{}] {} ({})".format(str(i), project_name, target_branch))

    project_index = -1
    is_valid = 0
    while not is_valid:
        try:
            project_index = int(input("? "))
            is_valid = 1
        except ValueError:
            print("Not a valid integer.")

    if 0 <= project_index < len(projects):
        # Here goes the thing
        project = projects[project_index]

        release(project)
    else:
        print("I won't take that as an answer")
else:
    # Deploy project passed as argument
    if args.project.startswith('/'):
        project_path = args.project

        if not os.path.isdir(project_path):
            print("\"{}\" is not a directory".format(project_path))
            sys.exit(1)
    else:
        project_path = os.path.join(ROOT_DIR, args.project)

        if project_path not in projects:
            print("Project not found")
            sys.exit(1)

    release(project_path)
