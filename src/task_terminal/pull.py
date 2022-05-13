#!/usr/bin/env python3
"""
Move item to list's 'pull_to' location if -U not specified, or to 'push_to' location if -U is specified.

$ pull PROJECT FILE IDX
$ pull PROJECT FILE IDX -U
"""

# base imports
import argparse
import json
import warnings

import pandas as pd
from termcolor import colored

from task_terminal import lst

from .helpers.helpers import (
    CONFIG,
    check_init,
    data_path,
    define_idx,
    file_options,
    pkg_path,
    process_file,
    reformat,
    timed_sleep,
    transfer_row,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Move item to list's 'pull_to' location if -U not specified, or to 'push_to' location if -U is specified."
    )
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        choices=project_list,
        help="Project in which entry resides.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        choices=file_options,
        help="File in which entry resides.",
    )
    parser.add_argument(
        "pos",
        type=str,
        nargs="+",
        help="Position of entry.",
    )
    parser.add_argument(
        "-U",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, send to 'push_to' location.",
    )
    d = vars(parser.parse_args())

    if not d["ref_proj"] or not d["pos"]:
        raise ValueError(
            reformat(
                f"'ref_proj' and at least one 'pos' must be provided.",
                input_type="error",
            )
        )
    if not all(
        x in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]
        for x in d["pos"]
    ):
        raise ValueError(
            reformat(
                f"'pos' entries must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100",
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
    if d["file"] is None:
        raise ValueError(
            reformat(
                f"No entry type provided. One of {CONFIG.keys()} (or an alias) within '{d['ref_proj']}' must be specified.",
                input_type="error",
            )
        )

    d["file"] = process_file(d["file"])

    if not d["U"]:
        if "pull_to" not in CONFIG[d["file"]].keys():
            raise ValueError(
                reformat(
                    "No 'pull_to' file found in 'config.json'. Cannot perform pull.",
                    input_type="error",
                )
            )
        to_file = CONFIG[d["file"]]["pull_to"]
    else:
        if "push_to" not in CONFIG[d["file"]].keys():
            raise ValueError(
                reformat(
                    "No 'push_to' file found in 'config.json'. Cannot perform push.",
                    input_type="error",
                )
            )
        to_file = CONFIG[d["file"]]["push_to"]

    from_path = f"{data_path}/projects/{d['ref_proj']}/{d['file']}.csv"
    to_path = f"{data_path}/projects/{d['ref_proj']}/{to_file}.csv"
    from_df = pd.read_csv(from_path)
    to_df = pd.read_csv(to_path)

    d["pos"] = [define_idx(i, from_df) for i in d["pos"]]
    if len(set(d["pos"])) != len(d["pos"]):
        warnings.warn(
            reformat(
                f"Dropping duplicate values in {d['pos']}. New indices are {list(set(d['pos']))}",
                input_type="error",
            )
        )
    d["pos"] = list(dict.fromkeys(d["pos"]))

    for idx in d["pos"]:
        if idx not in list(from_df.index):
            raise ValueError(
                reformat(
                    f"Provided index not found in project '{d['ref_proj']}' file {d['file']}.",
                    input_type="error",
                )
            )
        from_df, to_df = transfer_row(idx, from_df, to_df)
        to_df.to_csv(to_path, index=False)
        from_df.to_csv(from_path, index=False)
        print(
            reformat(
                f"{d['file'].capitalize()} item {idx} moved successfully to {to_file.capitalize()}."
            )
        )
        if "pull_to" not in CONFIG[to_file].keys():
            print(
                reformat(
                    colored(
                        "-- \u263A Nice job! \u263A --",
                        color="green",
                        attrs=["bold", "blink"],
                    )
                )
            )
            timed_sleep(2)
        else:
            timed_sleep(1)

    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
