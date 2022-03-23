#!/usr/bin/env python3
"""Add item to list."""

# base imports
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from .helpers.helpers import check_init, data_path, define_idx, move, pkg_path

check_init()


def main():
    # establish parameters
    templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get entries to add.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        help="Project to which entry will be added.",
    )
    parser.add_argument(
        "entry_type",
        type=str,
        nargs="?",
        default="task",
        choices=["task", "tasks", "ref", "refs", "note", "notes"],
        help="Project list to which entry will be added.",
    )
    parser.add_argument(
        "pos",
        nargs="?",
        default="HEAD",
        help="Position at which to add entry. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
    )
    parser.add_argument(
        "-flag",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, flag as important.",
    )
    d = vars(parser.parse_args())

    if d["pos"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            f"\n\t'pos' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100."
        )
    if len(project_list) == 0:
        raise ValueError(
            f"\n\tNo projects yet created.\n\tTo create a new project, run {templates['add_template']}."
        )
    if not d["ref_proj"]:
        raise ValueError(f"\n\t'ref_proj' must be provided.")
    if d["ref_proj"] not in project_list:
        raise ValueError(
            f"\n\t'{d['ref_proj']}' is not a valid project.\n\tAvailable projects are {project_list}."
        )

    path = f"{data_path}/projects/{d['ref_proj']}/{d['entry_type']}s.csv"
    df = pd.read_csv(path)
    entry = ""
    description = ""
    while entry == "":
        entry = input(f"\tProvide {d['entry_type']}:\n\t\t")
    description = input(f"\tDescribe {d['entry_type']}:\n\t\t")
    entry_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    df.loc[len(df)] = [entry, description, d["flag"], entry_time]
    df = move(df, from_index=-1, to_index=define_idx(d["pos"]))
    df.to_csv(path, index=False)
    print(f"\t{d['entry_type'].capitalize()} added successfully.")


if __name__ == "__main__":
    main()