#!/usr/bin/env python3
"""Move item in list to another position."""

import argparse
import json

import pandas as pd

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
    timed_sleep,
    transfer_row,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get entry to move.")
    parser.add_argument(
        "ref_proj",
        type=str,
        nargs="?",
        choices=project_list,
        help="Project in which entry will be moved.",
    )
    parser.add_argument(
        "file",
        type=str,
        nargs="?",
        choices=file_options,
        help="List in which entry will be moved.",
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
    if d["from"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        raise ValueError(
            reformat(
                f"'from' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100.",
                input_type="error",
            )
        )
    send_to_file = False
    if d["to"] not in [None, "HEAD", "TAIL"] + [str(i) for i in range(100)]:
        try:
            d["to"] = process_file(d["to"])
            send_to_file = True
        except:
            raise ValueError(
                reformat(
                    f"'to' must be one of 'HEAD', 'TAIL', 0, or a positive integer less than 100 OR be an existing project in {project_list}.",
                    input_type="error",
                )
            )

    if not send_to_file:
        file = process_file(d["file"])

        path = f"{data_path}/projects/{d['ref_proj']}/{file}.csv"
        df = pd.read_csv(path)

        from_idx = define_idx(d["from"], df)
        to_idx = define_idx(d["to"], df)
        df = move(df, from_index=from_idx, to_index=to_idx)
        df.to_csv(path, index=False)
        print(
            reformat(f"Entry {from_idx} successfully moved to position {to_idx}.")
        )
    else:
        from_file = process_file(d["file"])
        from_path = f"{data_path}/projects/{d['ref_proj']}/{from_file}.csv"
        to_path = f"{data_path}/projects/{d['ref_proj']}/{d['to']}.csv"
        from_df = pd.read_csv(from_path)
        to_df = pd.read_csv(to_path)

        from_idx = define_idx(d["from"], from_df)
        from_df, to_df = transfer_row(from_idx, from_df, to_df)
        to_df.to_csv(to_path, index=False)
        from_df.to_csv(from_path, index=False)
        print(reformat(f"{d['file'].capitalize()} item {from_idx} moved successfully to {d['to'].capitalize()}."))

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
