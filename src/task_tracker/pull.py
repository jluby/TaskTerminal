#!/usr/bin/env python3
"""Move item from backburner to active list or vice versa."""

# base imports
import argparse
import json

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
        description="Get entry to move from backburner to active task list."
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
    parser.add_argument(
        "-U",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, reverse movement (move from tasks to backburner).",
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

    task_path = f"{data_path}/projects/{d['ref_proj']}/tasks.csv"
    back_path = f"{data_path}/projects/{d['ref_proj']}/backburner.csv"
    if not d["U"]:
        from_path = back_path
        to_path = task_path
        from_name = "tasks"
    else:
        from_path = task_path
        to_path = back_path
        from_name = "backburner"
    from_df = pd.read_csv(from_path)
    to_df = pd.read_csv(to_path)
    idx = define_idx(d["pos"])
    if idx not in list(from_df.index):
        raise ValueError(
            reformat(
                f"Provided index not found in project '{d['ref_proj']}' {from_name}.",
                input_type="error",
            )
        )
    to_be_archived = from_df.iloc[idx]
    set_entry_size(to_be_archived)
    confirmed = input(
        f"\n{halftab}Are you sure you want to activate the below entry? (y/n)\n\n{to_be_archived}\n{halftab}"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(
            reformat(
                f"Accepted inputs are ['y', 'Y', 'n', 'N'.", input_type="input"
            )
        )
    if confirmed in ["y", "Y"]:
        to_df.loc[len(to_df)] = to_be_archived.tolist()
        to_df.to_csv(to_path, index=False)
        from_df = from_df.iloc[[i for i in from_df.index if i != idx]]
        from_df.to_csv(from_path, index=False)
        print(
            reformat(
                f"{from_name.capitalize()} item {d['pos']} moved successfully."
            )
        )
    else:
        print(reformat("Action cancelled."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
