#!/usr/bin/env python3
"""
Move item in list to another position or to tail of another list.

$ move PROJECT LIST FROM_IDX TO_IDX
# move PROJECT FROM_LIST FROM_IDX TO_LIST
"""

import argparse
import json
from contextlib import suppress
from datetime import datetime

import pandas as pd
from termcolor import colored

from task_terminal import lst

from .helpers.helpers import (
    CONFIG,
    check_init,
    data_path,
    define_idx,
    file_options,
    move,
    pkg_path,
    process_file,
    reformat,
    reformat_date,
    timed_sleep,
    transfer_row,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Move item in list to another position or to tail of another list.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        choices=project_list,
        help="Project in which entry to be moved resides.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        choices=file_options,
        help="List in which entry to be moved resides.",
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
        help="Index or file to which item should be moved.",
    )
    parser.add_argument(
        "-schedule",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, explicitly schedule next pull after move.",
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
        raise ValueError(reformat("'ref_proj' must be provided.", input_type="error"))
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
    if d["from"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            reformat(
                "'from' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100.",
                input_type="error",
            )
        )
    send_to_file = False
    if d["to"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        try:
            to_file = process_file(d["to"])
            send_to_file = True
        except:
            raise ValueError(
                reformat(
                    f"'to' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100 OR be an existing project in {project_list}.",
                    input_type="error",
                )
            )

    if not send_to_file:
        if d["schedule"]:
            raise ValueError(reformat("Movements within file do not accept -schedule kwarg.", input_type="error"))
        file = process_file(d["file"])

        path = f"{data_path}/projects/{d['ref_proj']}/{file}.csv"
        df = pd.read_csv(path)

        from_idx = define_idx(d["from"], df)
        to_idx = define_idx(d["to"], df)
        df = move(df, from_index=from_idx, to_index=to_idx)
        df.to_csv(path, index=False)
        print(reformat(f"Entry {from_idx} successfully moved to position {to_idx}."))
    else:
        from_file = process_file(d["file"])
        from_path = f"{data_path}/projects/{d['ref_proj']}/{from_file}.csv"
        to_path = f"{data_path}/projects/{d['ref_proj']}/{to_file}.csv"
        from_df = pd.read_csv(from_path)
        to_df = pd.read_csv(to_path)

        from_idx = define_idx(d["from"], from_df)
        from_df, to_df = transfer_row(from_idx, from_df, to_df)
        if ("attrs" in CONFIG[to_file].keys() and "schedule" in CONFIG[to_file]["attrs"]) or d["schedule"]:
            if "pull_to" not in CONFIG[to_file].keys():
                raise ValueError(reformat("Cannot schedule an entry to a file with no 'pull_to' parameter."))
            scheduled = ""
            while type(scheduled) is not datetime or not scheduled > datetime.now():
                with suppress(ValueError):
                    scheduled = input(
                        reformat(
                            "When should this be released? (%-m/%-d %H:%M)",
                            input_type="input",
                        )
                    )
                    scheduled = reformat_date(scheduled)
            to_df.loc[len(to_df) - 1, "datetime_scheduled"] = scheduled.strftime("%m/%d/%Y %H:%M:%S")
        to_df.to_csv(to_path, index=False)
        from_df.to_csv(from_path, index=False)
        print(reformat(f"{from_file.capitalize()} item {from_idx} moved successfully to {to_file.capitalize()}."))
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
            timed_sleep()

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
