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
    timed_sleep,
    reformat
)
from task_tracker import lst

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

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
            reformat(f"No projects yet created. To create a new project, run {templates['add_template']}.", input_type="error")
        )
    if not d["ref_proj"]:
        raise ValueError(reformat(f"'ref_proj' must be provided.", input_type="error"))
    if d["ref_proj"] not in project_list:
        raise ValueError(
            reformat(f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list}.", input_type="error")
        )
    if d["entry_type"] is None:
        raise ValueError(
            reformat(f"No entry type provided. One of ['task', 'ref', 'note'] must be specified within '{d['ref_proj']}'.", input_type="error")
        )
    if not set([d["to"], d["from"]]).issubset(
        [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]
    ):
        raise ValueError(
            reformat("'from' and 'to' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100.", input_type="error")
        )

    from_idx = define_idx(d["from"])
    to_idx = define_idx(d["to"])
    path = f"{data_path}/projects/{d['ref_proj']}/{d['entry_type']}s.csv"
    df = pd.read_csv(path)
    df = move(df, from_index=from_idx, to_index=to_idx)
    df.to_csv(path, index=False)
    print(
        reformat(f"Entry {from_idx} successfully moved to position {to_idx}.")
    )

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
