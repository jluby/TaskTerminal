#!/usr/bin/env python3
"""Display contents of list."""

# base imports
import argparse
import json

import pandas as pd

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    parse_description,
    parse_entries,
    pkg_path,
    print_lines,
    reformat,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))
project_list = [p for p in project_list if p not in hidden_list]
lists = [
    "notes",
    "note",
    "tasks",
    "task",
    "refs",
    "ref",
    "archive",
    "archives",
    "back",
    "backburner",
]


def main(parse_args=True):
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Input project to view.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        default="ALL",
        choices=project_list + ["ALL"],
        help="Projects to display.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default="tasks",
        choices=lists,
        help="List to display within project.",
    )
    parser.add_argument(
        "pos",
        type=str,
        nargs="?",
        help="Position of item within list for which to display description.",
    )
    parser.add_argument(
        "-flagged",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, list only flagged entries.",
    )
    parser.add_argument(
        "-arc",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, show archives.",
    )
    if parse_args:
        d = vars(parser.parse_args())
    else:
        d = vars(parser.parse_args([]))

    if d["pos"] and d["ref_proj"] == "ALL":
        raise ValueError(
            reformat(
                f"Use of 'pos' kwarg requires specification of a single project.",
                input_type="error",
            )
        )
    if d["pos"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            reformat(
                f"'pos' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100.",
                input_type="error",
            )
        )
    if len(project_list) == 0:
        raise ValueError(
            reformat(
                f"No projects created. To create a new directory, run {templates['add_template']}.",
                input_type="error",
            )
        )
    elif d["ref_proj"] not in project_list and d["ref_proj"] != "ALL":
        raise ValueError(
            reformat(
                f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list} or you may enter 'ALL' to see all projects. To create a new project directory, run {templates['add_template']}.",
                input_type="error",
            )
        )

    if d["file"][-1] != "s" and d["file"] != "backburner":
        d["file"] += "s"
    if d["file"] in ["back", "backburner"]:
        d["file"] = "backburner"

    if d["ref_proj"] == "ALL":
        lines = []
        for proj in project_list:
            df = pd.read_csv(f"{data_path}/projects/{proj}/{d['file']}.csv")
            lines += ["", proj]
            proj_lines = parse_entries(df, file=d["file"])
            lines += proj_lines
        lines.append("")
    else:
        df = pd.read_csv(
            f"{data_path}/projects/{d['ref_proj']}/{d['file']}.csv"
        )
        if d["pos"] is None:
            lines = parse_entries(df, file=d["file"])
        else:
            idx = define_idx(d["pos"])
            if idx not in list(df.index):
                raise ValueError(
                    reformat(
                        f"Provided index not found in project '{d['ref_proj']}' file '{d['file']}'. To view file contents, run {templates['list_proj_and_type']}.",
                        input_type="error",
                    )
                )
            else:
                lines = parse_description(df.iloc[idx])

    print_lines(lines)


if __name__ == "__main__":
    main()
