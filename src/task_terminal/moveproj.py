#!/usr/bin/env python3
"""Move project to a new priority position."""

import argparse
import json

from task_terminal import lst

from .helpers.helpers import (
    check_init,
    data_path,
    define_idx,
    reformat,
    timed_sleep,
)

# establish parameters
project_list = json.load(open(f"{data_path}/project_list.json", "r"))


def main():
    check_init()

    # establish parser to pull in projects to view
    parser = argparse.ArgumentParser(
        description="Move project to a new priority position."
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

    from_idx = define_idx(d["from"], project_list)
    to_idx = define_idx(d["to"], project_list)
    proj_to_move = project_list[from_idx]
    del project_list[from_idx]
    project_list.insert(to_idx, proj_to_move)
    json.dump(project_list, open(f"{data_path}/project_list.json", "w"))
    print(
        reformat(
            f"Project {proj_to_move} successfully moved from position {from_idx} to position {to_idx}."
        )
    )

    timed_sleep()
    lst.main(parse_args=False)


if __name__ == "__main__":
    main()
