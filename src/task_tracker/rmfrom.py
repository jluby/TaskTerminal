#!/usr/bin/env python3
"""Delete item from list."""

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
    get_bonus_width,
    halftab,
    pkg_path,
    reformat,
    set_entry_size,
    timed_sleep,
    file_options,
    process_file
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
        choices=file_options,
        help="Project list from which entry will be removed.",
    )
    parser.add_argument(
        "pos",
        nargs="+",
        help="Positions from which to remove task. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
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
                f"No entry type provided. One of ['task', 'ref', 'note'] within '{d['ref_proj']}' must be specified.",
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
    d["pos"] = [define_idx(i) for i in d["pos"]]
    if len(set(d["pos"])) != len(d["pos"]):
        warnings.warn(
            reformat(
                f"Dropping duplicate values in {d['pos']}. New indices are {list(set(d['pos']))}",
                input_type="error",
            )
        )
    d["pos"] = list(set(d["pos"]))

    file_name = process_file(d["entry_type"])
    bonus_width = get_bonus_width(file_name)

    base_path = f"{data_path}/projects/{d['ref_proj']}"
    path = f"{base_path}/{file_name}.csv"
    df = pd.read_csv(path)
    for idx in d["pos"]:
        if idx not in list(df.index):
            raise ValueError(
                reformat(
                    f"Provided index not found in project '{d['ref_proj']}' file {file_name}.",
                    input_type="error",
                )
            )
        iloc = df.index.get_loc(idx)
        to_be_removed = df.iloc[iloc]
        q_str = halftab + "Remove the below entry? (y/n)"
        set_entry_size(to_be_removed, min_width=len(q_str)+1, additional_width=21+bonus_width, max_width=70+bonus_width)
        confirmed = input(
            f"\n{q_str}\n{halftab}This action cannot be undone.\n\n{to_be_removed}\n{halftab}"
        )
        while confirmed not in ["y", "Y"] + ["n", "N"]:
            confirmed = input(
                reformat(
                    f"Accepted inputs are ['y', 'Y', 'n', 'N'].",
                    input_type="input",
                )
            )
        if confirmed in ["y", "Y"]:
            df = df.loc[df.index != idx]
            df.to_csv(path, index=False)
            print(
                reformat(
                    f"{d['entry_type'].capitalize()} item {idx} removed successfully."
                )
            )
        else:
            print(reformat("Action cancelled."))
        timed_sleep()

    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
