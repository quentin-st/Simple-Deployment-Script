#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Easy & simple yet flexible production deployment script """

import argparse
import os
import sys
import inspect
import json
import re

from operator import itemgetter

from utils.stdio import Printer
import plugins
# The following line is necessary for project types to be found
from plugins import *
from config import ROOT_DIR

__author__ = 'Quentin Stoeckel'
__copyright__ = 'Copyright 2016, Quentin Stoeckel and contributors'
__credits__ = ['Contributors at https://github.com/chteuchteu/Simple-Deployment-Script/graphs/contributors']

__license__ = 'gpl-v2'
__version__ = '1.0.0'
__maintainer__ = "qstoeckel"
__email__ = 'stoeckel.quentin@gmail.com'
__status__ = 'Production'

CONFIG_FILE_NAME = 'deploy.json'
CONFIG_FILE_NAME_DEPRECATED = 'deploy.conf.json'


def find_projects():
    sanitized_root_dir = os.path.expanduser(ROOT_DIR.rstrip('/'))
    projects = []

    # Recursively find config file in ROOT_DIR
    printer.verbose("Scanning {} for {} files".format(sanitized_root_dir, CONFIG_FILE_NAME))
    for root, dirs, files in os.walk(sanitized_root_dir):
        for file in files:
            if file == CONFIG_FILE_NAME or file == CONFIG_FILE_NAME_DEPRECATED:
                file_path = os.path.join(root, file)
                project = load_project(root)
                conf_malformed = True if project['conf'] is None else False
                conf_deprecated = file == CONFIG_FILE_NAME_DEPRECATED

                text = "\tFound ~/{}".format(os.path.relpath(file_path, sanitized_root_dir))

                if conf_malformed:
                    text += ' (malformed)'
                elif conf_deprecated:
                    text += ' (deprecated conf file format)'

                if conf_malformed or conf_deprecated:
                    printer.warning(text)
                else:
                    printer.info(text)

                projects.append(project)

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

    if conf_path.endswith(CONFIG_FILE_NAME_DEPRECATED):
        printer.warning("Warning: '{}' as conf filename is deprecated, consider renaming it to '{}'.".format(
            CONFIG_FILE_NAME_DEPRECATED, CONFIG_FILE_NAME
        ))

    # Conf is malformed
    if conf is None:
        printer.error("\nMalformed config file ({})".format(conf_path))
        return False

    # Read conf
    project_type = conf.get("projectType", "generic")
    branch = conf.get("branch", "release")
    forced_passes = conf.get("passes", "").split()

    printer.info("\nDeploying project {} ({})".format(project_name, branch), bold=True)

    # Check the project type
    types = get_supported_project_types()
    if project_type not in types:
        printer.error("Unknown project type \"{}\".".format(project_type))
        return False

    # Let's go!
    os.chdir(project_path)

    # Check if either git_checkout or git_pull special passes are disabled
    if "-git_checkout" not in forced_passes:
        e = printer.pexec('git', "git checkout {}".format(branch))

        if e != 0:
            printer.error('git checkout command finished with non-zero exit value, aborting deploy')
            return False

    print('')

    if "-git_pull" not in forced_passes:
        e = printer.pexec('git', "git pull")

        if e != 0:
            printer.error('git pull command finished with non-zero exit value, aborting deploy')
            return False

        # Get an updated version of the conf, if the config file has changed after the pull
        # Handle case where conf_path gets renamed to non-deprecated version
        if not os.path.isfile(conf_path):
            project['conf_path'] = conf_path = os.path.join(project_path, CONFIG_FILE_NAME)

        conf = parse_conf(conf_path)
        forced_passes = conf.get("passes", "").split()

    # Determine plugin-specific passes
    plugin = types[project_type](printer, args)

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

        if pass_name not in deploy_passes:
            deploy_passes.append(pass_name)

    if len(deploy_passes) > 0:
        printer.success("\nDeployment starting with passes: {}".format(", ".join(deploy_passes)))

        # Start env-specific passes
        npasses = len(deploy_passes)
        for i, pass_name in enumerate(deploy_passes):
            printer.info("\nPass {} of {} [{}]".format(i+1, npasses, pass_name), True)
            e = getattr(plugin, pass_name + "_pass")(project)

            if e != 0:
                printer.error("Pass '{}' finished with non-zero ({}) exit value, aborting deploy".format(
                    pass_name, e
                ))
                return False

    # Execute custom commands
    commands = conf.get("commands", [])
    if len(commands) > 0:
        printer.success("\nExecuting custom commands")

        for command in commands:
            e = printer.pexec('commands', command)

            if e != 0:
                printer.error("Custom command finished with non-zero ({}) exit value, aborting deploy.".format(e))
                return False

    # The End
    printer.success("\n{} successfully deployed. Have an A1 day!\n".format(project_path))
    return True


# Here goes the code
try:
    sanitized_root_dir = os.path.expanduser(ROOT_DIR.rstrip('/'))

    # Command line argument
    parser = argparse.ArgumentParser(description='Easily deploy projects')
    # Script args
    parser.add_argument('--self-update', action='store_true', dest='self_update')
    parser.add_argument('path', nargs='?')
    parser.add_argument('--project', default='ask_for_it')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('--no-color', action='store_true', dest='no_color')
    parser.add_argument('--not-verbose', action='store_true', dest='not_verbose')
    # Plugin-specific args
    parser.add_argument('--env', default='prod')  # Symfony
    args = parser.parse_args()

    printer = Printer(not args.no_color, not args.not_verbose)

    if args.self_update:
        # cd to own directory
        self_dir = os.path.dirname(os.path.realpath(__file__))

        if not os.path.isdir(os.path.join(self_dir, '.git')):
            printer.error("Cannot self-update: missing .git directory")
            sys.exit(1)

        os.chdir(self_dir)
        os.system("git pull")

        printer.success("\nUpdated to the latest version")
    elif args.path is not None:
        project_path = os.path.abspath(os.path.join(os.curdir, args.path))

        if not os.path.isdir(project_path):
            printer.error("This is not a valid directory")
            sys.exit(1)

        if not os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME))\
                and not os.path.isfile(os.path.join(project_path, CONFIG_FILE_NAME_DEPRECATED)):
            printer.error("There is no {} file in this directory.".format(CONFIG_FILE_NAME))
            sys.exit(1)

        # Load project
        project = load_project(project_path)
        success = release(project)
        sys.exit(0 if success else 1)
    elif args.all:
        projects = find_projects()

        # Deploy all projects!
        if len(projects) > 0:
            for i, project in enumerate(projects):
                release(project)
        else:
            printer.error("There is no suitable project in {}".format(sanitized_root_dir))

    elif args.project == 'ask_for_it':
        projects = find_projects()

        if len(projects) == 0:
            printer.error("No project found in {}, exiting.".format(ROOT_DIR))
            sys.exit(1)

        printer.info("Please select a project to deploy (^C to exit): '1' or '1, 3, 5'")

        # List projects
        for i, project in enumerate(projects):
            malformed_conf = True if project['conf'] is None else False

            if malformed_conf:
                printer.warning("\t[{}] {} (malformed conf)".format(str(i), project['name']))
            else:
                target_branch = project['conf'].get("branch", "release")
                printer.info("\t[{}] {} ({})".format(str(i), project['name'], target_branch))

        # Read user input
        regex = re.compile('(-?\d+)(,\s*-?d+)?')
        matches = []

        while len(matches) == 0:
            user_input = input("? ") if sys.version_info.major == 3 else raw_input("? ")
            matches = regex.findall(user_input)

            if len(matches) > 0:
                for match in matches:
                    index = int(match[0])
                    if 0 <= index < len(projects):
                        release(projects[index])
                    else:
                        printer.warning("Invalid project index {}, ignoring".format(index))
            else:
                printer.error("Not a valid sequence. Use either '1' or '1, 3, 5' instead")
    else:
        projects = find_projects()
        project_path = os.path.join(sanitized_root_dir, args.project)

        results = [project for project in projects if project['path'] == project_path]

        if len(results) == 0:
            printer.error("No project found with this name. Re-run this script without args to list all projects")
            sys.exit(1)
        elif len(results) > 1:
            printer.error("Ambiguous project name, re-run this script without args or specify absolute path")
            sys.exit(1)

        success = release(load_project(project_path))
        sys.exit(0 if success else 1)
except KeyboardInterrupt:
    # noinspection PyUnboundLocalVariable
    printer.info("\n^C signal caught, exiting")
    sys.exit(1)
