#!/usr/bin/env python3
"""Add item to list."""

# base imports
import argparse
import json
from contextlib import suppress
from datetime import datetime, timedelta
from datetime import date as dt
from dateutil.relativedelta import relativedelta
from parse import *
import time

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

# TODO: allow 'sc' as schedule entry

def reformat_date(date_and_time: str):
    if " " in date_and_time:
        date_str, time_str = date_and_time.split(" ")
    elif ":" not in date_and_time:
        date_str, time_str = date_and_time, "00:00"
    else:
        date, time_str = dt.today(), date_and_time
        date_str = None
    
    if date_str:
        if date_str.count("/") == 0:
            today = dt.today()
            day = time.strptime(date_str, "%a").tm_wday
            remainder = (day-today.weekday()-1) % 7 + 1
            date = today + timedelta(days=remainder)
        else:
            p = [v.zfill(2) for v in parse("{}/{}", date_str)]
            date = datetime.strptime(f"{p[0]}/{p[1]}", "%m/%d")
            date += relativedelta(years=datetime.now().year - date.year)
            if datetime.now() > date:
                date += relativedelta(years=1)
    
    p = [v.zfill(2) for v in parse("{}:{}", time_str[:-2])]
    tm = datetime.strptime(f"{p[0]}:{p[1]}{time_str[-2:]}", "%I:%M%p").time()
    
    return datetime.combine(date, tm)

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
            release = ""
            while type(release) is not datetime or not release > datetime.now():
                #with suppress(ValueError):
                release = input(
                    reformat(
                        "When should this be released? (%-m/%-d %H:%M)",
                        input_type="input",
                        )
                )
                release = reformat_date(release)
            out_ls.append(release.strftime("%m/%d/%Y %H:%M:%S"))
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
