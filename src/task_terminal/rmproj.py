#!/usr/bin/env python3
"""
Delete project.

$ rmproj PROJECT
"""

# base imports
import argparse
import json
import os
from shutil import rmtree

from task_terminal import lst

from .helpers.helpers import check_init, data_path, halftab, pkg_path, reformat, timed_sleep

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Delete project.")
    parser.add_argument(
        "project",
        type=str,
        nargs="?",
        help="Project to delete.",
    )
    d = vars(parser.parse_args())

    if not d["project"]:
        raise ValueError(reformat("'project' must be provided.", input_type="error"))
    if not os.path.exists(f"{data_path}/projects/{d['project']}"):
        raise ValueError(reformat(f"Project '{d['project']}' does not exist.", input_type="error"))

    base_path = f"{data_path}/projects/{d['project']}"
    confirmed = None
    confirmed = input(f"Remove {d['project']}? (y/n)\n{halftab}This action cannot be undone.\n{halftab}")
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(
            reformat(
                f"Accepted inputs are ['y', 'Y', 'n', 'N'].",
                input_type="input",
            )
        )
    if confirmed in ["y", "Y"]:
        rmtree(base_path)
        if d["project"] in project_list:
            project_list.remove(d["project"])
            json.dump(project_list, open(f"{data_path}/project_list.json", "w"))
        else:
            hidden_list.remove(d["project"])
            json.dump(hidden_list, open(f"{data_path}/hidden_project_list.json", "w"))
        print(reformat(f"Project '{d['project']}' removed successfully."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
