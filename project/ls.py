#!/usr/bin/env python3

import argparse
import json
import os

from task_tracker.helpers import print_ls

# establish parameters
templates = json.load(open("templates.json"))
project_list = os.listdir("projects")

# establish parser to pull in projects to view
parser = argparse.ArgumentParser(description="Input project to view.")
parser.add_argument(
    "proj", type=str, nargs="?", default=None, help="projects to display"
)
proj = vars(parser.parse_args())["proj"]

if proj is None:
    while proj not in project_list and proj != "":
        proj = input(
            f"""Please specify a project or, to show all projects, press Enter.\nAvailable projects are {project_list}:\n\n"""
        )

if proj not in project_list and proj != "":
    raise ValueError(
        f"\n\t'{proj}' is not a valid directory.\n\tTo create a new directory, run {templates['add_template']}"
    )
if proj == "" and len(project_list) == 0:
    raise ValueError(
        f"\n\tNo projects available.\n\tTo create a new directory, run {templates['add_template']}"
    )

if proj == "":
    for proj in project_list:
        print_ls(proj)
else:
    print_ls(proj)
