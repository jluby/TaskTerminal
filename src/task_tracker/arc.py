#!/usr/bin/env python3
"""Move item from active list to archive."""

# base imports
import argparse
import json
import warnings
from datetime import datetime
from termcolor import colored

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
    move
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

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
        "pos",
        type=str,
        nargs="+",
        help="Position of entry.",
    )
    parser.add_argument(
        "-U",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, reverse movement (move from archives to tasks).",
    )
    d = vars(parser.parse_args())

    if not d["ref_proj"] or not d["pos"]:
        raise ValueError(
            reformat(
                f"'ref_proj' and 'pos' must be provided.", input_type="error"
            )
        )
    if not all(x in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)] for x in d["pos"]):
        raise ValueError(
            reformat(
                f"'pos' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100",
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
    if len(set(d["pos"])) != len(d["pos"]):
        old_pos = d["pos"]
        d["pos"] = list(dict.fromkeys(d["pos"]))
        warnings.warn(
            reformat(
                f"Dropping duplicate values in {old_pos}. New indices are {list(set(d['pos']))}",
                input_type="error",
            )
        )

    task_path = f"{data_path}/projects/{d['ref_proj']}/tasks.csv"
    arc_path = f"{data_path}/projects/{d['ref_proj']}/archives.csv"
    if not d["U"]:
        from_path = task_path
        to_path = arc_path
        from_name = "tasks"
    else:
        from_path = arc_path
        to_path = task_path
        from_name = "archives"
    from_df = pd.read_csv(from_path)
    to_df = pd.read_csv(to_path)
    for idx in [define_idx(i) for i in d["pos"]]:
        if idx not in list(from_df.index):
            raise ValueError(
                reformat(
                    f"Provided index not found in project '{d['ref_proj']}' {from_name}.",
                    input_type="error",
                )
            )
        iloc = from_df.index.get_loc(idx)
        to_be_moved = from_df.iloc[iloc]
        de = "un" if d["U"] else ""
        q_str = halftab + f"{f'{de}archive'.capitalize()} the below entry? (y/n)"
        set_entry_size(to_be_moved, additional_height=5, min_width=len(q_str)+1, additional_width=21 if d['U'] else 20, max_width=70 if d['U'] else 69)
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
            to_be_moved = to_be_moved.tolist()
            if from_name == "tasks":
                archive_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                to_be_moved += [archive_time]
            else:
                to_be_moved = to_be_moved[:-1]
            to_df.loc[len(to_df)] = to_be_moved
            if from_name == "tasks":
                to_df = move(to_df, from_index=-1, to_index=0)
            to_df.to_csv(to_path, index=False)
            from_df = from_df.loc[from_df.index != idx]
            from_df.to_csv(from_path, index=False)
            if not d["U"]:
                print(
                    reformat(
                        colored("Nice job! \u263A", color="green")
                    )
                )
                timed_sleep(2)
            else:
                print(
                    reformat(
                        f"{from_name[:-1].capitalize()} item {idx} moved successfully."
                    )
                )
                timed_sleep()
        else:
            print(reformat("Action cancelled."))
            timed_sleep()
    
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
