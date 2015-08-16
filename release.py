#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

ROOT_DIR = "/var/www/html/"
CONFIG_FILE_NAME = "deployment.conf"

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
for project in projects:
    print project

