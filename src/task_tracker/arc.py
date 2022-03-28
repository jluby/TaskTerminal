#!/usr/bin/env python3
"""Move item from active list to archive."""

# base imports
import argparse
import json
from datetime import datetime

import pandas as pd

from task_tracker import lst

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    halftab,
    pkg_path,
    reformat,
    set_entry_size,
    timed_sleep,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Get entry to move to project archives."
    )
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        help="Project in which entry resides.",
    )
    parser.add_argument(
        "pos",
        type=str,
        nargs="?",
        help="Position of entry.",
    )
    d = vars(parser.parse_args())

    if not d["ref_proj"] or not d["pos"]:
        raise ValueError(
            reformat(
                f"'ref_proj' and 'pos' must be provided.", input_type="error"
            )
        )
    if d["pos"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            reformat(
                f"'pos' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100",
                input_type="error",
            )
        )
    if len(project_list) == 0:
        raise ValueError(
            reformat(
                f"No projects yet created. To create a new project, run {templates['add_template']}",
                input_type="error",
            )
        )
    if d["ref_proj"] not in project_list:
        raise ValueError(
            reformat(
                f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list}.",
                input_type="error",
            )
        )

    path = f"{data_path}/projects/{d['ref_proj']}/tasks.csv"
    df = pd.read_csv(path)
    idx = define_idx(d["pos"])
    if idx not in list(df.index):
        raise ValueError(
            reformat(
                f"Provided index not found in project '{d['ref_proj']}' tasks",
                input_type="error",
            )
        )
    to_be_archived = df.iloc[idx]
    set_entry_size(to_be_archived)
    confirmed = input(
        f"\n{halftab}Are you sure you want to archive the below entry? (y/n)\n{halftab}This action cannot be undone.\n\n{to_be_archived}\n{halftab}"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(
            reformat(
                f"Accepted inputs are ['y', 'Y', 'n', 'N'.", input_type="input"
            )
        )
    if confirmed in ["y", "Y"]:
        archive_path = f"{data_path}/projects/{d['ref_proj']}/archives.csv"
        archive_df = pd.read_csv(archive_path)
        archive_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        archive_df.loc[len(archive_df)] = to_be_archived.tolist() + [
            archive_time
        ]
        archive_df.to_csv(archive_path, index=False)
        df = df.iloc[[i for i in df.index if i != idx]]
        df.to_csv(path, index=False)
        print(reformat(f"Task {d['pos']} archived successfully."))
    else:
        print(reformat("Action cancelled."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
