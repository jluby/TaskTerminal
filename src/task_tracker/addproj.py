#!/usr/bin/env python3
"""Add project."""

# base imports
import argparse
import json
import os
from pathlib import Path

import pandas as pd

from .helpers.helpers import check_init, data_path, pkg_path

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
cols = ["entry", "description", "flagged", "datetime_created"]


def main():
    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get project to add.")
    parser.add_argument(
        "project",
        type=str,
        nargs="?",
        help="Project to create.",
    )
    d = vars(parser.parse_args())

    if not d["project"]:
        raise ValueError(f"\n\t'project' must be provided.")
    if os.path.exists(f"{data_path}/projects/{d['project']}"):
        raise ValueError(f"\n\tProject '{d['project']}' already exists.")

    base_path = f"{data_path}/projects/{d['project']}"
    os.makedirs(base_path)
    os.makedirs(f"{base_path}/archives")
    for file in ["tasks", "refs", "notes"]:
        pd.DataFrame(columns=cols).to_csv(
            f"{base_path}/{file}.csv", index=False
        )
        pd.DataFrame(columns=cols + ["datetime_archived"]).to_csv(
            f"{base_path}/archives/{file}.csv", index=False
        )

    project_list.append(d["project"])
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))

    print(f"\tProject '{d['project']}' created successfully.")


if __name__ == "__main__":
    main()
