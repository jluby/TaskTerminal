#!/usr/bin/env python3
"""
Show projects currently available.

$ lsproj
"""

# base imports
import json

from .helpers.helpers import check_init, data_path, halftab

check_init()


def main():
    # establish parameters
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))
    hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))

    print(f"\n{halftab}Active projects: {project_list}")
    print(f"\n{halftab}Hidden projects: {hidden_list}\n")


if __name__ == "__main__":
    main()
