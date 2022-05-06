#!/usr/bin/env python3
"""Create a hidden project list so that currently dead projects are not printed on 'show' calls."""

# base imports
import argparse
import json
from pathlib import Path

from task_terminal import lst

from .helpers.helpers import (
    check_init,
    data_path,
    pkg_path,
    reformat,
    timed_sleep,
)

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Create a hidden project list so that currently dead projects are not printed on 'show' calls.")
    parser.add_argument(
        "-U",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If provided, unhide project.",
    )
    parser.add_argument(
        "project",
        type=str,
        nargs="?",
        help="Project to hide.",
    )
    d = vars(parser.parse_args())

    helper_str = reformat(
        f"To hide a project, run {templates['hide_project']}. To unhide a project, run {templates['unhide_project']}.",
        input_type="error",
    )
    if not d["project"]:
        raise ValueError(
            reformat("Project name must be provided.", input_type="error")
            + helper_str
        )
    ref_ls = project_list if not d["U"] else hidden_list
    if d["project"] not in ref_ls:
        raise ValueError(
            reformat(
                "Project not found in reference list.", input_type="error"
            )
            + helper_str
        )

    if not d["U"]:
        hidden_list.append(d["project"])
        project_list.remove(d["project"])
    else:
        hidden_list.remove(d["project"])
        hidden_list.append(d["project"])
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))
    json.dump(hidden_list, open(f"{data_path}/hidden_project_list.json", "w"))
    type_str = "added to" if not d["U"] else "removed from"
    print(
        reformat(
            f"Project {d['project']} successfully {type_str} hidden list."
        )
    )

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
