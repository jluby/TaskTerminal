#!/usr/bin/env python3

import argparse
import json
import os

# establish parameters
templates = json.load(open("templates.json"))
project_list = os.listdir("projects")

# establish parser to pull in projects to view
parser = argparse.ArgumentParser(description="Get projects, references, or tasks to add.")
parser.add_argument(
    "src_project", type=str, nargs=1, help="Project list to which task will be added"
)
parser.add_argument(
    "position", nargs=1, choices=list(range(1000)) + ['HEAD', 'TAIL'], help="Position at which to add task. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'."
)
proj = vars(parser.parse_args())["proj"]