#!/usr/bin/env python3
"""Create a hidden project list so that currently dead projects are not printed on 'show' calls."""

# base imports
import argparse
import json
from pathlib import Path

from .helpers.helpers import check_init, data_path, halftab, pkg_path, timed_sleep
import lst

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))
hidden_list = json.load(open(f"{data_path}/hidden_project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(description="Get project to hide.")
    parser.add_argument(
        "-u",
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

    helper_str = f"\n{halftab}To hide a project, run {templates['hide_project']}\n{halftab}To unhide a project, run {templates['unhide_project']}."
    if not d["project"]:
        raise ValueError(
            f"\n{halftab}Project name must be provided.{helper_str}"
        )
    ref_ls = project_list if not d["u"] else hidden_list
    if d["project"] not in ref_ls:
        raise ValueError(
            f"\n{halftab}Project not found in reference list.{helper_str}"
        )

    if not d["u"]:
        hidden_list.append(d["project"])
        project_list.remove(d["project"])
    else:
        hidden_list.remove(d["project"])
        hidden_list.append(d["project"])
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))
    json.dump(hidden_list, open(f"{data_path}/hidden_project_list.json", "w"))
    type_str = "added to" if not d["u"] else "removed from"
    print(
        f"{halftab}Project {d['project']} successfully {type_str} hidden list."
    )

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
