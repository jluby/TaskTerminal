#!/usr/bin/env python3
"""Move item in list to another position."""

import argparse
import json
from pathlib import Path

import pandas as pd

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    halftab,
    move,
    pkg_path,
)

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get entry to move.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        help="Project in which entry will be moved.",
    )
    parser.add_argument(
        "entry_type",
        type=str,
        nargs="?",
        choices=["task", "ref", "note"],
        help="List in which entry will be moved.",
    )
    parser.add_argument(
        "from",
        type=str,
        nargs="?",
        help="Index from which to move. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
    )
    parser.add_argument(
        "to",
        type=str,
        nargs="?",
        help="Index to which item should be moved.",
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
            f"\n{halftab}No entry type provided. One of ['task', 'ref', 'note'] must be specified within '{d['ref_proj']}'."
        )
    if not set([d["to"], d["from"]]).issubset(
        [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]
    ):
        raise ValueError(
            f"\n{halftab}'from' and 'to' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100."
        )

    from_idx = define_idx(d["from"])
    to_idx = define_idx(d["to"])
    path = f"{data_path}/projects/{d['ref_proj']}/{d['entry_type']}s.csv"
    df = pd.read_csv(path)
    entry = df.loc[from_idx, "entry"]
    df = move(df, from_index=from_idx, to_index=to_idx)
    df.to_csv(path, index=False)
    print(
        f"{halftab}Entry {entry} successfully moved from position {from_idx} to position {to_idx}."
    )


if __name__ == "__main__":
    main()
