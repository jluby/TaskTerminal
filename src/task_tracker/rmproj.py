#!/usr/bin/env python3
"""Delete project."""

# base imports
import argparse
import json
import os
from shutil import rmtree

from .helpers.helpers import check_init, data_path, pkg_path

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))


def main():
    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get project to delete.")
    parser.add_argument(
        "project",
        type=str,
        nargs="?",
        help="Project to delete.",
    )
    d = vars(parser.parse_args())

    if not d["project"]:
        raise ValueError(f"\n\t'project' must be provided.")
    if not os.path.exists(f"{data_path}/projects/{d['project']}"):
        raise ValueError(f"\n\tProject '{d['project']}' does not exist.")

    base_path = f"{data_path}/projects/{d['project']}"
    confirmed = None
    confirmed = input(
        f"Are you sure you want to remove {d['project']}? (y/n)\n\tThis action cannot be undone.\n\t"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(f"\n\tAccepted inputs are ['y', 'Y', 'n', 'N'.")
    if confirmed in ["y", "Y"]:
        rmtree(base_path)
        if d["project"] in project_list:
            project_list.remove(d["project"])
            json.dump(
                project_list, open(f"{data_path}/project_list.json", "w")
            )
        else:
            hidden_list.remove(d["project"])
            json.dump(
                hidden_list, open(f"{data_path}/hidden_project_list.json", "w")
            )
        print(f"\tProject '{d['project']}' removed successfully.")


if __name__ == "__main__":
    main()