#!/usr/bin/env python3
"""
Display contents of list.

Usage:
$ lst all LIST
$ lst PROJECT LIST
$ lst PROJECT LIST IDX
"""

# base imports
import argparse
import json
import os

import pandas as pd

from .helpers.helpers import (
    check_init,
    check_scheduled,
    data_path,
    define_idx,
    file_options,
    parse_description,
    parse_entries,
    pkg_path,
    print_lines,
    process_file,
    reformat,
)

templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
WIDTH = 55

def main(parse_args=True):

    # establish parameters
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))
    hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))
    project_list = [p for p in project_list if p not in hidden_list]
    check_init()
    check_scheduled()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Display contents of list or entry."
    )
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        default="ALL",
        choices=project_list + ["all", "ALL"],
        help="Projects to display.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default="tasks",
        choices=file_options,
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

    last_lst_path = f"{data_path}/last_lst.json"
    if parse_args:
        d = vars(parser.parse_args())
        json.dump(d, open(last_lst_path, "w"))
    else:
        d = vars(parser.parse_args([]))
        if os.path.isfile(last_lst_path):
            last_lst_params = json.load(
                open(f"{data_path}/last_lst.json", "r")
            )
            d.update(last_lst_params)

    if d["pos"] and d["ref_proj"] in ["all", "ALL"]:
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
                f"No projects active. To create a new directory, run {templates['add_template']}. To unhide an existing directory, run {templates['unhide_project']}.",
                input_type="error",
            )
        )
    elif d["ref_proj"] not in project_list and d["ref_proj"] not in [
        "all",
        "ALL",
    ]:
        raise ValueError(
            reformat(
                f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list} or you may enter 'ALL' to see all projects. To create a new project directory, run {templates['add_template']}.",
                input_type="error",
            )
        )

    file = process_file(d["file"])

    if d["ref_proj"] in ["all", "ALL"]:
        lines = []
        for proj in project_list:
            df = pd.read_csv(f"{data_path}/projects/{proj}/{file}.csv")
            proj_lines = parse_entries(
                df, project=proj, file=file, width=WIDTH
            )
            lines += proj_lines
        lines += [""]
    else:
        df = pd.read_csv(f"{data_path}/projects/{d['ref_proj']}/{file}.csv")
        if d["pos"] is None:
            lines = parse_entries(df, project=d["ref_proj"], file=file, width=WIDTH)
            lines += [""]
        else:
            idx = define_idx(d["pos"], df)
            if idx not in list(df.index):
                raise ValueError(
                    reformat(
                        f"Provided index not found in project '{d['ref_proj']}' file '{file}'. To view file contents, run {templates['list_proj_and_type']}.",
                        input_type="error",
                    )
                )
            else:
                lines = parse_description(df.iloc[idx])

    if not d["pos"]:
        print(f"\n---{file.upper()}---")
        extra_height = 2
    else:
        extra_height = 1
    print_lines(lines, width=WIDTH, extra_height=extra_height)


if __name__ == "__main__":
    main()
