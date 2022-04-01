#!/usr/bin/env python3
"""Add item to list."""

# base imports
import argparse
import json
from contextlib import suppress
from datetime import datetime

import pandas as pd

from task_tracker import lst

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    move,
    pkg_path,
    reformat,
    timed_sleep,
    file_options,
    process_file,
    process_name
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
        help="Project to which entry will be added.",
    )
    parser.add_argument(
        "entry_type",
        type=str,
        nargs="?",
        default="backburner",
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

    file_name = process_file(d["entry_type"])
    entry_name = process_name(d["entry_type"])

    path = f"{data_path}/projects/{d['ref_proj']}/{file_name}.csv"
    df = pd.read_csv(path)
    entry = ""
    description = ""
    entry_str = (
        f"Provide {entry_name} entry:"
        if entry_name != "ref"
        else f"Provide {entry_name} description:"
    )
    while entry == "":
        entry = input(reformat(entry_str, input_type="input"))
    description_str = (
        f"Describe {entry_name} entry:"
        if entry_name != "ref"
        else f"Paste reference below:"
    )
    description = input(reformat(description_str, input_type="input"))
    entry_time = str(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    if entry_name in ["task", "back", "backburner", "schedule"]:
        time_estimate = ""
        while type(time_estimate) is not float:
            with suppress(ValueError):
                time_estimate = float(
                    input(
                        reformat(
                            "How long will this take (in hours)?",
                            input_type="input",
                        )
                    )
                )
        out_ls = [entry, description, time_estimate, d["flag"], entry_time]
        if entry_name == "schedule":
            scheduled_release = ""
            while type(scheduled_release) is not datetime or not scheduled_release > datetime.now():
                with suppress(ValueError):
                    scheduled_release = datetime.strptime(
                        input(
                            reformat(
                                "When should this be released? (%m/%d/%Y %H:%M)",
                                input_type="input",
                            )
                        ), "%m/%d/%Y %H:%M"
                    )
            out_ls.append(scheduled_release.strftime("%m/%d/%Y %H:%M:%S"))
    else:
        out_ls = [entry, description, d["flag"], entry_time]
    df.loc[len(df)] = out_ls
    df = move(df, from_index=-1, to_index=define_idx(d["pos"]))
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


# TODO: fix sizing on schedule rm / edit / whatever
