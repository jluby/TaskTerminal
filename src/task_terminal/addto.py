#!/usr/bin/env python3
"""Add item to list."""

# base imports
import argparse
import json
from contextlib import suppress
from datetime import datetime

import pandas as pd

from task_terminal import lst

from .helpers.helpers import (
    CONFIG,
    check_init,
    columns,
    data_path,
    define_idx,
    file_options,
    move,
    pkg_path,
    process_file,
    process_name,
    reformat,
    reformat_date,
    timed_sleep,
)


def main():
    check_init()

    # establish parameters
    templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
    project_list = json.load(open(f"{data_path}/project_list.json", "r"))

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get entries to add.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        choices=project_list,
        help="Project to which entry will be added.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default="task",
        choices=file_options,
        help="Project list to which entry will be added.",
    )
    parser.add_argument(
        "pos",
        nargs="?",
        default="TAIL",
        help="Position at which to add entry. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
    )
    parser.add_argument(
        "-flag",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, flag as important.",
    )
    parser.add_argument(
        "-s",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, explicitly schedule movement.",
    )
    d = vars(parser.parse_args())

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

    file = process_file(d["file"])
    entry_name = process_name(d["file"])

    entry_dict = {k: None for k in columns}

    path = f"{data_path}/projects/{d['ref_proj']}/{file}.csv"
    df = pd.read_csv(path)
    entry_dict["entry"] = ""
    entry_dict["description"] = ""
    entry_str = (
        f"Provide {entry_name} entry:"
        if entry_name != "ref"
        else f"Provide {entry_name} description:"
    )
    while entry_dict["entry"] == "":
        entry_dict["entry"] = input(reformat(entry_str, input_type="input"))
    description_str = (
        f"Describe {entry_name} entry:"
        if entry_name != "ref"
        else f"Paste reference below:"
    )
    entry_dict["description"] = input(
        reformat(description_str, input_type="input")
    )
    entry_dict["datetime_created"] = str(
        datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    )
    entry_dict["flagged"] = d["flag"]

    if "attrs" in CONFIG[file].keys() and "hours" in CONFIG[file]["attrs"]:
        entry_dict["time_estimate"] = ""
        while type(entry_dict["time_estimate"]) is not float:
            with suppress(ValueError):
                entry_dict["time_estimate"] = float(
                    input(
                        reformat(
                            "How long will this take (in hours)?",
                            input_type="input",
                        )
                    )
                )
        if (
            "attrs" in CONFIG[file].keys()
            and "schedule" in CONFIG[file]["attrs"]
        ) or d["s"]:
            if "pull_to" not in CONFIG[file].keys():
                raise ValueError(
                    reformat(
                        "Cannot schedule an entry to a file with no 'pull_to' parameter."
                    )
                )
            scheduled = ""
            while (
                type(scheduled) is not datetime
                or not scheduled > datetime.now()
            ):
                with suppress(ValueError):
                    scheduled = input(
                        reformat(
                            "When should this be released? (%-m/%-d %H:%M)",
                            input_type="input",
                        )
                    )
                    scheduled = reformat_date(scheduled)
            entry_dict["datetime_scheduled"] = scheduled.strftime(
                "%m/%d/%Y %H:%M:%S"
            )

    df = df.append(entry_dict, ignore_index=True)
    df = move(df, from_index=-1, to_index=define_idx(d["pos"], df))
    df.to_csv(path, index=False)
    df = pd.read_csv(path)
    print(
        reformat(
            f"{entry_name.capitalize()} added successfully.",
            input_type=None,
        )
    )

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
