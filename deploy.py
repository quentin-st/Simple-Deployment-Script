#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import inspect
import json
import re

from operator import itemgetter

from utils import stdio
from utils.stdio import CRESET, CDIM, CBOLD, LGREEN, LWARN, LRED
import plugins
# The following line is necessary for project types to be found
from plugins import *
from config import ROOT_DIR

CONFIG_FILE_NAME = 'deploy.json'
CONFIG_FILE_NAME_DEPRECATED = 'deploy.json'


def find_projects():
    sanitized_root_dir = os.path.expanduser(ROOT_DIR.rstrip('/'))
    projects = []

    # Recursively find config file in ROOT_DIR
    print(CDIM, "Scanning {} for {} files".format(sanitized_root_dir, CONFIG_FILE_NAME), CRESET)
    for root, dirs, files in os.walk(sanitized_root_dir):
        for file in files:
            if file == CONFIG_FILE_NAME or file == CONFIG_FILE_NAME_DEPRECATED:
                file_path = os.path.join(root, file)
                project = load_project(root)
                malformed_conf = True if project['conf'] is None else False

                print(CDIM+LWARN if malformed_conf else CDIM, "\tFound ~/{} {}".format(
                    os.path.relpath(file_path, sanitized_root_dir),
                    '(malformed)' if malformed_conf else ''
                ), CRESET)

                projects.append(project)

    print()

    # Sort projects by name alphabetically
    return sorted(projects, key=itemgetter('name'))


def load_project(project_path):
    # If project isn't located in ROOT_DIR, set the full relative path as project_name
    if os.path.dirname(project_path) != ROOT_DIR:
        project_name = os.path.relpath(project_path, ROOT_DIR)
    else:
        project_name = os.path.basename(os.path.normpath(project_path))

    # Handle both deprecated & preferred conf filenames
    conf_path = os.path.join(project_path, CONFIG_FILE_NAME)
    if not os.path.isfile(conf_path):
        print(LWARN, "\tWarning: '{}' as filename is deprecated, consider using '{}' instead.".format(
            CONFIG_FILE_NAME_DEPRECATED, CONFIG_FILE_NAME
        ))
        conf_path = os.path.join(project_path, CONFIG_FILE_NAME_DEPRECATED)

    # Try to parse conf (a malformed conf file may prevent one from deploying at all)
    try:
        conf = parse_conf(conf_path)
    except ValueError:
        conf = None

    return {
        'name': project_name,
        'path': project_path,
        'conf': conf,
        'conf_path': conf_path
    }


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


def release(project):
    project_name = project['name']
    project_path = project['path']
    conf = project['conf']
    conf_path = project['conf_path']

    # Conf is malformed
    if conf is None:
        print(CBOLD + LRED, "\nMalformed config file ({})".format(project['conf_path']), CRESET)
        return

    # Read conf
    project_type = conf.get("projectType", "generic")
    branch = conf.get("branch", "release")
    forced_passes = conf.get("passes", "").split()

    print(CBOLD + LGREEN, "\nDeploying project {} ({})".format(project_name, branch), CRESET)

    # Check the project type
    types = get_supported_project_types()
    if project_type not in types:
        print(CBOLD + LWARN, "Unknown project type \"{}\".".format(project_type), CRESET)
        return

    # Let's go!
    os.chdir(project_path)

    # Check if either git_checkout or git_pull special passes are disabled
    if "-git_checkout" not in forced_passes:
        os.system("git checkout " + branch)

    if "-git_pull" not in forced_passes:
        os.system("git pull")

        # Get an updated version of the conf, if the config file has changed after the pull
        conf = parse_conf(conf_path)
        forced_passes = conf.get("passes", "").split()

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

    if len(deploy_passes) > 0:
        print(CBOLD+LGREEN, "\n==> Deployment starting with passes: {}".format(", ".join(deploy_passes)), CRESET)

        # Start env-specific passes
        npasses = len(deploy_passes)
        for i, pass_name in enumerate(deploy_passes):
            print(CBOLD, "\n==> Pass {} of {} [{}]".format(i+1, npasses, pass_name), CRESET)
            getattr(plugin, pass_name + "_pass")(project)

    # Execute custom commands
    commands = conf.get("commands", [])
    if len(commands) > 0:
        print(CBOLD + LGREEN, "\nExecuting custom commands", CRESET)

        for command in commands:
            stdio.ppexec(command)

    # The End
    print(CBOLD+LGREEN, "\n==> {} successfully deployed. Have an A1 day!\n".format(project_path), CRESET)


# Here goes the code
try:
    sanitized_root_dir = os.path.expanduser(ROOT_DIR.rstrip('/'))

    # Check command line argument
    parser = argparse.ArgumentParser(description='Easily deploy projects')
    parser.add_argument('--self-update', action='store_true', dest='self_update')
    parser.add_argument('path', nargs='?')
    parser.add_argument('--project', default='ask_for_it')
    parser.add_argument('-a', '--all', action='store_true')
    args = parser.parse_args()

    if args.self_update:
        # cd to own directory
        self_dir = os.path.dirname(os.path.realpath(__file__))

        if not os.path.isdir(os.path.join(self_dir, '.git')):
            print(CDIM+LWARN, "Cannot self-update: missing .git directory", CRESET)
            sys.exit(1)

        os.chdir(self_dir)
        os.system("git pull")

        print()
        print(LGREEN, "Updated to the latest version", CRESET)
    elif args.path is not None:
        project_path = os.path.abspath(os.path.join(os.curdir, args.path))

        if not os.path.isdir(project_path):
            print("This is not a valid directory")
            sys.exit(1)

        if not os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME))\
                or not os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME_DEPRECATED)):
            print("There is no {} file in this directory.".format(CONFIG_FILE_NAME))
            sys.exit(1)

        # Load project
        project = load_project(project_path)
        release(project)
    elif args.all:
        projects = find_projects()

        # Deploy all projects!
        if len(projects) > 0:
            for i, project in enumerate(projects):
                release(project)
        else:
            print("There is no suitable project in {}".format(sanitized_root_dir))

    elif args.project == 'ask_for_it':
        projects = find_projects()

        if len(projects) == 0:
            print("No project found in {}, exiting.".format(ROOT_DIR))
            sys.exit(1)

        print("Please select a project to deploy (^C to exit): '1' or '1, 3, 5'")

        # List projects
        for i, project in enumerate(projects):
            malformed_conf = True if project['conf'] is None else False

            if malformed_conf:
                print(CDIM+LWARN, "\t[{}] {} (malformed conf)".format(str(i), project['name']), CRESET)
            else:
                target_branch = project['conf'].get("branch", "release")
                print("\t[{}] {} ({})".format(str(i), project['name'], target_branch))

        # Read user input
        regex = re.compile('(-?\d+)(,\s*-?d+)?')
        matches = []

        while len(matches) == 0:
            matches = regex.findall(input("? "))

            if len(matches) > 0:
                for match in matches:
                    index = int(match[0])
                    if 0 <= index < len(projects):
                        release(projects[index])
                    else:
                        print("Invalid project index {}, ignoring".format(index))
            else:
                print("Not a valid sequence. Use either '1' or '1, 3, 5' instead")
    else:
        projects = find_projects()
        project_path = os.path.join(sanitized_root_dir, args.project)

        results = [project for project in projects if project['path'] == project_path]

        if len(results) == 0:
            print(CBOLD+LRED, "No project found with this name. Re-run this script without args to list all projects", CRESET)
            sys.exit(1)
        elif len(results) > 1:
            print(CBOLD+LWARN, "Ambiguous project name, re-run this script without args or specify absolute path", CRESET)
            sys.exit(1)

        release(load_project(project_path))
except KeyboardInterrupt:
    print("\n^C signal caught, exiting")
    sys.exit(1)
