#!/usr/bin/env python3
"""Delete item from list."""

# base imports
import argparse
import json
import os
import time
from re import L

import numpy as np
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
    parser = argparse.ArgumentParser(description="Get entries to remove.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        help="Project from which entry will be removed.",
    )
    parser.add_argument(
        "entry_type",
        type=str,
        nargs="?",
        choices=["task", "ref", "note", "archive", "back", "backburner"],
        help="Project list from which entry will be removed.",
    )
    parser.add_argument(
        "pos",
        nargs="?",
        help="Position from which to remove task. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
    )
    d = vars(parser.parse_args())

    if len(project_list) == 0:
        raise ValueError(
            reformat(
                f"No projects yet created. To create a new project, run {templates['add_template']}.",
                input_type="error",
            )
        )
    if not d["ref_proj"]:
        raise ValueError(
            reformat(f"'ref_proj' must be provided.", input_type="error")
        )
    if d["ref_proj"] not in project_list:
        raise ValueError(
            reformat(
                f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list}.",
                input_type="error",
            )
        )
    if d["entry_type"] is None:
        raise ValueError(
            reformat(
                f"No entry type provided. One of ['task', 'ref', 'note'] within '{d['ref_proj']}' must be specified.",
                input_type="error",
            )
        )
    elif d["pos"] is None:
        raise ValueError(
            reformat(
                f"No positional index provided. Index within {d['entry_type']} must be specified.",
                input_type="error",
            )
        )

    if d["entry_type"] not in ["back", "backburner"]:
        filename = d["entry_type"] + "s"
    else:
        filename = "backburner"
        d["entry_type"] = "backburner"

    base_path = f"{data_path}/projects/{d['ref_proj']}"
    path = f"{base_path}/{filename}.csv"
    df = pd.read_csv(path)
    idx = define_idx(d["pos"])
    if idx not in list(df.index):
        raise ValueError(
            reformat(
                f"Provided index not found in project '{d['ref_proj']}' file {filename}.",
                input_type="error",
            )
        )
    to_be_removed = df.iloc[idx]
    q_str = halftab + "Remove the below entry? (y/n)"
    set_entry_size(to_be_removed, min_width=len(q_str)+1)
    confirmed = input(
        f"\n{q_str}\n{halftab}This action cannot be undone.\n\n{to_be_removed}\n{halftab}"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(
            reformat(
                f"Accepted inputs are ['y', 'Y', 'n', 'N'].",
                input_type="input",
            )
        )
    if confirmed in ["y", "Y"]:
        df = df.iloc[[i for i in df.index if i != idx]]
        df.to_csv(path, index=False)
        print(
            reformat(
                f"{d['entry_type'].capitalize()} item {d['pos']} removed successfully."
            )
        )
    else:
        print(reformat("Action cancelled."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
