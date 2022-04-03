#!/usr/bin/env python3
"""Add project."""

# base imports
import argparse
import json
import os

import pandas as pd

from task_tracker import lst

from .helpers.helpers import check_init, data_path, reformat, timed_sleep, CONFIG, cols


def main():
    check_init()

    # establish parameters
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))

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
        raise ValueError(
            reformat("'project' must be provided.", input_type="error")
        )
    if os.path.exists(f"{data_path}/projects/{d['project']}"):
        raise ValueError(
            reformat(
                f"Project '{d['project']}' already exists.", input_type="error"
            )
        )

    base_path = f"{data_path}/projects/{d['project']}"

    os.makedirs(base_path)
    for file in CONFIG.keys():
        pd.DataFrame(columns=cols).to_csv(
            f"{base_path}/{file}.csv", index=False
        )

    project_list.append(d["project"])
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))

    print(reformat(f"Project '{d['project']}' created successfully."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
