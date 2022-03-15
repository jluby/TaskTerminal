#!/usr/bin/env python3

# base imports
import argparse
import json
import os

# package imports
from task_tracker.helpers import print_ls

# establish parameters
templates = json.load(open("templates.json"))
project_list = os.listdir("projects")

# establish parser to pull in projects to view
parser = argparse.ArgumentParser(description="Input project to view.")
parser.add_argument(
    "proj", type=str, nargs="?", default="", help="projects to display"
)
proj = vars(parser.parse_args())["proj"]

if len(project_list) == 0:
    raise ValueError(
        f"\n\tNo projects created.\n\tTo create a new directory, run {templates['add_template']}"
    )
elif proj not in project_list and proj != "":
    raise ValueError(
        f"\n\t'{proj}' is not a valid project.\n\tAvailable projects are {project_list}.\n\tTo create a new project directory, run {templates['add_template']}"
    )

if proj == "":
    for proj in project_list:
        print_ls(proj)
else:
    print_ls(proj)
