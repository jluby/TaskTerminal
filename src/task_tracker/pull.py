#!/usr/bin/env python3
"""Move item from backburner to active list or vice versa."""

# TODO: make format and push up to git

# base imports
import argparse
import json
import warnings

import pandas as pd
from termcolor import colored

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
    process_file,
    file_options,
    transfer_row,
    define_chain
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))

def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Get entry to move from to config 'send_to' file."
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
        help="If provided, reverse movement.",
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
    if d["file"] is None:
        raise ValueError(
            reformat(
                f"No entry type provided. One of {CONFIG.keys()} (or an alias) within '{d['ref_proj']}' must be specified.",
                input_type="error",
            )
        )

    d["file"] = process_file(d["file"])
    chain = define_chain(d["file"])

    file_idx = chain.index(d["file"])
    end_of_chain = False
    if not d["U"]:
        if file_idx == len(chain):
            raise ValueError(reformat("No 'send_to' file found in 'config.json'. Cannot perform pull.", input_type="error"))
        to_file = chain[file_idx + 1]
        end_of_chain = file_idx + 2 == len(chain)
    else:
        if file_idx == 0:
            raise ValueError(reformat("No sender file found in 'config.json'. Cannot perform push.", input_type="error"))
        to_file = chain[chain.index(d["file"]) - 1]
    
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
    
    for idx in d['pos']:
        if idx not in list(from_df.index):
            raise ValueError(
                reformat(
                    f"Provided index not found in project '{d['ref_proj']}' file {d['file']}.",
                    input_type="error",
                )
            )
        iloc = from_df.index.get_loc(idx)
        to_be_moved = from_df.iloc[iloc]
        m_str = "Pull" if not d["U"] else "Push"
        q_str = halftab + f"{m_str} the below entry? (y/n)"
        set_entry_size(to_be_moved, additional_height=5, min_width=len(q_str)+1, additional_width=23, max_width=72)
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
            from_df, to_df = transfer_row(idx, from_df, to_df)
            to_df.to_csv(to_path, index=False)
            from_df.to_csv(from_path, index=False)
            if end_of_chain:
                print(
                    reformat(
                        colored("-- \u263A Nice job! \u263A --", color="green", attrs=["bold", "blink"])
                    )
                )
                timed_sleep(2)
            else:
                print(
                    reformat(
                        f"Item moved successfully to {to_file}."
                    )
                )
                timed_sleep()
        else:
            print(reformat("Action cancelled."))
            timed_sleep()

    lst.main(parse_args=False)


if __name__ == "__main__":
    main()