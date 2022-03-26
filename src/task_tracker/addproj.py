#!/usr/bin/env python3
"""Add project."""

# base imports
import argparse
import json
import os

import pandas as pd

from .helpers.helpers import check_init, data_path, halftab, timed_sleep
from task_tracker import lst

def main():
    check_init()

    # establish parameters
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))
    cols = ["entry", "description", "flagged", "datetime_created"]

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
        raise ValueError(f"\n{halftab}'project' must be provided.")
    if os.path.exists(f"{data_path}/projects/{d['project']}"):
        raise ValueError(
            f"\n{halftab}Project '{d['project']}' already exists."
        )

    base_path = f"{data_path}/projects/{d['project']}"
    os.makedirs(base_path)
    os.makedirs(f"{base_path}/archives")
    for file in ["tasks", "refs", "notes"]:
        if file == "tasks":
            cols.insert(2, "time_estimate")
        pd.DataFrame(columns=cols).to_csv(
            f"{base_path}/{file}.csv", index=False
        )
        pd.DataFrame(columns=cols + ["datetime_archived"]).to_csv(
            f"{base_path}/archives/{file}.csv", index=False
        )

    project_list.append(d["project"])
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))

    print(f"{halftab}Project '{d['project']}' created successfully.")
    
    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
