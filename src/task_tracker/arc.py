#!/usr/bin/env python3
"""Move item from active list to archive."""

# base imports
import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from .helpers.helpers import check_init, data_path, define_idx, pkg_path

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
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
        "entry_type",
        type=str,
        nargs="?",
        choices=["task", "ref", "note"],
        help="Entry type of project.",
    )
    parser.add_argument(
        "pos",
        type=str,
        nargs="?",
        help="Position of entry.",
    )
    d = vars(parser.parse_args())

    if not d["ref_proj"] or not d["entry_type"] or not d["pos"]:
        raise ValueError(
            f"\n\tAll of 'ref_proj', 'entry_type', and 'pos' must be provided."
        )
    if d["pos"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            f"\n\t'pos' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100"
        )
    if len(project_list) == 0:
        raise ValueError(
            f"\n\tNo projects yet created.\n\tTo create a new project, run {templates['add_template']}"
        )
    if d["ref_proj"] not in project_list:
        raise ValueError(
            f"\n\t'{d['ref_proj']}' is not a valid project.\n\tAvailable projects are {project_list}."
        )

    path = f"{data_path}/projects/{d['ref_proj']}/{d['entry_type']}s.csv"
    df = pd.read_csv(path)
    idx = define_idx(d["pos"])
    if idx not in list(df.index):
        raise ValueError(
            f"Provided index not found in project '{d['ref_proj']}' file {d['entry_type']}s"
        )
    to_be_archived = df.iloc[idx]
    confirmed = input(
        f"\n\tAre you sure you want to archive the below entry? (y/n)\n\tThis action cannot be undone.\n\n{to_be_archived}\n\t"
    )
    while confirmed not in ["y", "Y"] + ["n", "N"]:
        confirmed = input(f"\n\tAccepted inputs are ['y', 'Y', 'n', 'N'.")
    if confirmed in ["y", "Y"]:
        archive_path = f"{data_path}/projects/{d['ref_proj']}/archives/{d['entry_type']}s.csv"
        archive_df = pd.read_csv(archive_path)
        archive_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        archive_df.loc[len(archive_df)] = to_be_archived.tolist()[1:] + [
            archive_time
        ]
        archive_df.to_csv(archive_path, index=False)
        df = df.iloc[[i for i in df.index if i != idx]]
        df.to_csv(path, index=False)
        print(
            f"\t{d['entry_type'].capitalize()} item {d['pos']} archived successfully."
        )
    else:
        print(f"\tAction cancelled.")


if __name__ == "__main__":
    main()