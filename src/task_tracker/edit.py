#!/usr/bin/env python3
"""Edit list item."""

# base imports
import argparse
import json

import pandas as pd
import numpy as np

from datetime import datetime

pd.options.mode.chained_assignment = None
from contextlib import suppress

from task_tracker import lst

from .helpers.helpers import (
    CONFIG,
    check_init,
    data_path,
    define_idx,
    halftab,
    pkg_path,
    reformat,
    set_entry_size,
    timed_sleep,
    split_to_width,
    set_entry_size_manual,
    file_options,
    process_file,
    reformat_date
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
        choices=project_list,
        help="Project from which entry will be removed.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        choices=file_options,
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
    if d["file"] is None:
        raise ValueError(
            reformat(
                f"No entry type provided. One of {CONFIG.keys()} (or an alias) within '{d['ref_proj']}' must be specified.",
                input_type="error",
            )
        )
    elif d["pos"] is None:
        raise ValueError(
            reformat(
                f"No positional index provided. Index within {d['file']} must be specified.",
                input_type="error",
            )
        )

    file_name = process_file(d["file"])

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
    set_entry_size(to_be_edited, min_width=53, max_width=76, additional_height=5, additional_width=27)
    val_idx = int(
        input(
            f"\n{halftab}Which item would you like to edit (enter index)?\n\n{to_be_edited}\n{halftab}"
        )
    )
    edit_lines = split_to_width(str(to_be_edited[val_idx]), linelen=50)
    set_entry_size_manual(6+len(edit_lines), np.max([len(l) for l in edit_lines])+10)
    print(f"\n{halftab}{to_be_edited.index[val_idx][:-4].capitalize()} was:"); [print(f"{halftab}{l}") for l in edit_lines]; print(f"{halftab}{type(to_be_edited[val_idx])}\n")
    is_date = "datetime" in to_be_edited.index[val_idx]
    new_value = None
    while not (type(new_value) == type(to_be_edited[val_idx]) and not is_date) and not ((type(new_value) is datetime) and is_date):
        with suppress(ValueError):
            new_value = input(
                reformat(
                    "What would you like to replace it with?",
                    input_type="input",
                )
            )
            if to_be_edited.index[val_idx][:4] == "desc" and type(new_value) is str:
                break

            if "datetime" in to_be_edited.index[val_idx]:
                if new_value in ["NaN", "NA", "na", "nan"]:
                    new_value = float("NaN"); break
                new_value = reformat_date(new_value)
            else:
                new_value = type(to_be_edited[val_idx])(new_value)

    if is_date and not pd.isna(new_value):
        new_value = new_value.strftime("%m/%d/%Y %H:%M:%S")
    to_be_edited.iloc[val_idx] = new_value
    df.iloc[idx] = to_be_edited.tolist()
    df.to_csv(path, index=False)

    print(reformat("Item successfully edited."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
