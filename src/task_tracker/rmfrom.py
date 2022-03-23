#!/usr/bin/env python3
"""Delete item from list."""

# base imports
import argparse
import json
from pathlib import Path

import pandas as pd

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    halftab,
    pkg_path,
)

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
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
        choices=["task", "ref", "note", "archive"],
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
            f"\n{halftab}No projects yet created.\n{halftab}To create a new project, run {templates['add_template']}."
        )
    if not d["ref_proj"]:
        raise ValueError(f"\n{halftab}'ref_proj' must be provided.")
    if d["ref_proj"] not in project_list:
        raise ValueError(
            f"\n{halftab}'{d['ref_proj']}' is not a valid project.\n{halftab}Available projects are {project_list}."
        )
    if d["entry_type"] is None:
        raise ValueError(
            f"\n{halftab}No entry type provided. One of ['task', 'ref', 'note'] within '{d['ref_proj']}' must be specified."
        )
    elif d["pos"] is None:
        raise ValueError(
            f"\n{halftab}No positional index provided. Index within {d['entry_type']} must be specified."
        )

    base_path = f"{data_path}/projects/{d['ref_proj']}"
    path = f"{base_path}/{d['entry_type']}s.csv"
    df = pd.read_csv(path)
    idx = define_idx(d["pos"])
    if idx not in list(df.index):
        raise ValueError(
            f"Provided index not found in project '{d['ref_proj']}' file {d['entry_type']}s."
        )
    to_be_removed = df.iloc[idx]
    confirmed = input(
        f"\n{halftab}Are you sure you want to remove the below entry? (y/n)\n{halftab}This action cannot be undone.\n\n{to_be_removed}\n{halftab}"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(
            f"\n{halftab}Accepted inputs are ['y', 'Y', 'n', 'N'."
        )
    if confirmed in ["y", "Y"]:
        df = df.iloc[[i for i in df.index if i != idx]]
        df.to_csv(path, index=False)
        print(
            f"{halftab}{d['entry_type'].capitalize()} item {d['pos']} removed successfully."
        )
    else:
        print(f"{halftab}Action cancelled.")


if __name__ == "__main__":
    main()
