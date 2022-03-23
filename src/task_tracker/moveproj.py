#!/usr/bin/env python3
"""Move project to a new priority position."""

import argparse
import json
from pathlib import Path

from .helpers.helpers import check_init, data_path, define_idx, pkg_path

check_init()

# establish parameters
templates = json.load(open(f"{pkg_path}/helpers/templates.json"))
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Get project or entry to move."
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
        help="Index to which item should be moved.",
    )
    d = vars(parser.parse_args())

    from_idx = define_idx(d["from"])
    to_idx = define_idx(d["to"])
    proj_to_move = project_list[from_idx]
    del project_list[from_idx]
    project_list.insert(to_idx, proj_to_move)
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))
    print(
        f"\tProject {proj_to_move} successfully moved from position {from_idx} to position {to_idx}."
    )


if __name__ == "__main__":
    main()
