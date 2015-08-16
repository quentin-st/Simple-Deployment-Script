#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import sys
from subprocess import call

ROOT_DIR = "/var/www/html/"
CONFIG_FILE_NAME = "deployment.conf"


# Here goes the functions
def read_conf(array, key, default_value):
    "Returns the value for a conf key. If not found, returns the default_value"
    if key in array:
        return array[key]
    else:
        return default_value



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
    print "Please select a project to sync\n"
    for i, project in enumerate(projects):
        print "    ["+str(i)+"]" + " " + project

    project_index = int(raw_input("?")) # Blindly parse input

    if project_index >= 0 and project_index < len(projects):
        # Here goes the thing
        project = projects[project_index]

        # Configuration file parsing
        conf_raw = open(project + "/" + CONFIG_FILE_NAME, "r").read()
        conf = json.loads(conf_raw)

        # Read conf        
        project_type = read_conf(conf, "projectType", "vanilla")
        branch = read_conf(conf, "branch", "release")

        # Check the project type
        valid_types = ["vanilla", "symfony2"]
        if not project_type in valid_types:
            print "Unknown project type..."
            sys.exit(1)

        # Let's go!
        os.chdir(project)
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
        os.system("chown -R www-data:www-data " + project)
        
        print "Release finished. Have an A1 day!"
    else:
        print "I won't take that as an answer"
else:
    print "No suitable project found in " + ROOT_DIR
    
