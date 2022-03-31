#!/usr/bin/env python3
"""Move item from backburner to active list or vice versa."""

# base imports
import argparse
import json
import warnings

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
        nargs="+",
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
                f"'ref_proj' and at least one 'pos' must be provided.", input_type="error"
            )
        )
    if not all(x in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)] for x in d["pos"]):
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
    d["pos"] = [define_idx(i) for i in d["pos"]]
    if len(set(d["pos"])) != len(d["pos"]):
        warnings.warn(
            reformat(
                f"Dropping duplicate values in {d['pos']}. New indices are {list(set(d['pos']))}",
                input_type="error",
            )
        )
    d["pos"] = list(set(d["pos"]))

    task_path = f"{data_path}/projects/{d['ref_proj']}/tasks.csv"
    back_path = f"{data_path}/projects/{d['ref_proj']}/backburner.csv"
    if not d["U"]:
        from_path = back_path
        to_path = task_path
        from_name = "backburner"
    else:
        from_path = task_path
        to_path = back_path
        from_name = "tasks"
    from_df = pd.read_csv(from_path)
    to_df = pd.read_csv(to_path)
    for idx in d['pos']:
        if idx not in list(from_df.index):
            raise ValueError(
                reformat(
                    f"Provided index {idx} not found in project '{d['ref_proj']}' {from_name}.",
                    input_type="error",
                )
            )
        iloc = from_df.index.get_loc(idx)
        to_be_moved = from_df.iloc[iloc]
        de = "de" if d["U"] else ""
        q_str = halftab + f"{f'{de}activate'.capitalize()} the below entry? (y/n)"
        set_entry_size(to_be_moved, additional_height=5, min_width=len(q_str)+1)
        confirmed = input(
            f"\n{q_str}\n\n{to_be_moved}\n{halftab}"
        )
        while confirmed not in ["y", "Y"] + ["n", "N"]:
            confirmed = input(
                reformat(
                    f"Accepted inputs are ['y', 'Y', 'n', 'N'].", input_type="input"
                )
            )
        if confirmed in ["y", "Y"]:
            to_df.loc[len(to_df)] = to_be_moved.tolist()
            to_df.to_csv(to_path, index=False)
            from_df = from_df.loc[from_df.index != idx]
            from_df.to_csv(from_path, index=False)
            print(
                reformat(
                    f"{from_name.capitalize()} item {idx} moved successfully."
                )
            )
        else:
            print(reformat("Action cancelled."))
        timed_sleep()

    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
