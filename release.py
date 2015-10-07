#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import sys
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


def release(project_path):
    # Parse conf
    conf = parse_conf(project_path + "/" + CONFIG_FILE_NAME)

    # Read conf
    project_type = read_conf(conf, "projectType", "vanilla")
    branch = read_conf(conf, "branch", "release")

    # Check the project type
    valid_types = ["vanilla", "symfony2"]
    if project_type not in valid_types:
        print("Unknown project type...")
        sys.exit(1)

    # Let's go!
    os.chdir(project_path)
    # Checkout release branch
    os.system("git checkout " + branch)
    # Pull changes
    os.system("git pull")

    # Symfony2-specific commands
    if project_type == "symfony2":
        # Install assets
        os.system("php app/console assets:install")
        # Clear cache
        os.system("php app/console cache:clear")

    # Restore files ownership for new files
    os.system("chown -R www-data:www-data " + project_path)

    print("Release finished. Have an A1 day!")


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


# Ask user for project to sync
if len(projects) > 0:
    print("Please select a project to sync\n")
    for i, project in enumerate(projects):
        project_name = os.path.basename(os.path.normpath(project))
        target_branch = read_conf(parse_conf(project + "/" + CONFIG_FILE_NAME), "branch", "release")

        print("    [" + str(i) + "]" + " " + project_name + " (" + target_branch + ")")

    project_index = int(input("?"))  # Blindly parse input

    if 0 <= project_index < len(projects):
        # Here goes the thing
        project = projects[project_index]

        release(project)
    else:
        print("I won't take that as an answer")
else:
    print("No suitable project found in " + ROOT_DIR)
