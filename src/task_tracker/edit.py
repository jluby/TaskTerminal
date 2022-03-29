#!/usr/bin/env python3
"""Edit list item."""

# base imports
import argparse
import json
from tkinter import E

import pandas as pd

pd.options.mode.chained_assignment = None
from contextlib import suppress

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
        choices=["task", "ref", "note", "archive", "back", "backburner"],
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
            reformat(
                f"No projects yet created. To create a new project, run {templates['add_template']}.",
                input_type="error",
            )
        )
    if not d["ref_proj"]:
        raise ValueError(
            reformat(f"'ref_proj' must be provided.", input_type="error")
        )
    if d["ref_proj"] not in project_list:
        raise ValueError(
            reformat(
                f"'{d['ref_proj']}' is not a valid project. Available projects are {project_list}.",
                input_type="error",
            )
        )
    if d["entry_type"] is None:
        raise ValueError(
            reformat(
                f"No entry type provided. One of ['task', 'ref', 'note', 'backburner' (or 'back')] within '{d['ref_proj']}' must be specified.",
                input_type="error",
            )
        )
    elif d["pos"] is None:
        raise ValueError(
            reformat(
                f"No positional index provided. Index within {d['entry_type']} must be specified.",
                input_type="error",
            )
        )

    if d["entry_type"] not in ["back", "backburner"]:
        file_name = d["entry_type"] + "s"
    else:
        file_name = "backburner"
        d["entry_type"] = "backburner"

    base_path = f"{data_path}/projects/{d['ref_proj']}"
    path = f"{base_path}/{file_name}.csv"
    df = pd.read_csv(path)
    idx = define_idx(d["pos"])
    if idx not in list(df.index):
        raise ValueError(
            reformat(
                f"Provided index not found in project '{d['ref_proj']}' file {file_name}.",
                input_type="error",
            )
        )
    to_be_edited = df.iloc[idx]
    to_be_edited.index = [
        f"{c} ({i})" for i, c in enumerate(to_be_edited.index)
    ]
    set_entry_size(to_be_edited)
    val_idx = int(
        input(
            f"\n{halftab}Which item would you like to edit (enter index)?\n\n{to_be_edited}\n{halftab}"
        )
    )
    print(
        f"\n{halftab}The value was:\n\t{to_be_edited[val_idx]}\n{halftab}{type(to_be_edited[val_idx])}"
    )
    new_value = None
    while type(new_value) != type(to_be_edited[val_idx]):
        with suppress(ValueError):
            new_value = input(
                reformat(
                    "What would you like to replace it with?",
                    input_type="input",
                )
            )
            new_value = type(to_be_edited[val_idx])(new_value)

    to_be_edited.iloc[val_idx] = new_value
    df.iloc[idx] = to_be_edited.tolist()
    df.to_csv(path, index=False)

    print(reformat("Item successfully edited."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
