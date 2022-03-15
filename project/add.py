#!/usr/bin/env python3

# base imports
import argparse
import json
import os

import pandas as pd

# establish parameters
templates = json.load(open("templates.json"))
if os.path.exists("projects/.DS_Store"):
    os.remove("projects/.DS_Store")
project_list = os.listdir("projects")
cols = ["entry", "description", "flagged"]

# establish parser to pull in projects to view
parser = argparse.ArgumentParser(
    description="Get projects, references, or tasks to add."
)
parser.add_argument(
    "add_proj",
    type=str,
    nargs="?",
    help="Project list to which task will be added",
)
parser.add_argument(
    "cat",
    type=str,
    nargs="?",
    choices=["task", "ref"],
    default="task",
    help="Project list to which task will be added",
)
parser.add_argument(
    "--pos",
    nargs="?",
    required=False,
    choices=list(range(1000)) + ["HEAD", "TAIL"],
    default="HEAD",
    help="Position at which to add task. Accepted arguments are zero / positive integer indices, 'HEAD', and 'TAIL'.",
)
parser.add_argument(
    "--proj",
    nargs="?",
    required=False,
    help="Project to create",
)
parser.add_argument(
    "--flag",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Flag as important if argument is provided",
)
d = vars(parser.parse_args())

if not d["proj"] and not d["add_proj"]:
    raise ValueError(f"\n\tOne of arguments ['proj', 'add_proj'] required.")
if d["proj"] and d["add_proj"]:
    raise ValueError(
        f"\n\tExtra argument '{d['add_proj']}' provided.\n\tTo create a new project, run {templates['add_template']}"
    )
elif d["proj"] and os.path.exists(f"projects/{d['proj']}"):
    raise ValueError(f"\n\tProject '{d['proj']}' already exists.")
elif len(project_list) == 0 and d["proj"] is None:
    raise ValueError(
        f"\n\tNo projects created.\n\tTo create a new project, run {templates['add_template']}"
    )
elif d["add_proj"] not in project_list and d["proj"] is None:
    raise ValueError(
        f"\n\t'{d['add_proj']}' is not a valid project.\n\tAvailable projects are {project_list}.\n\tTo create a new project directory, run {templates['add_template']}"
    )


def define_idx(pos) -> int:
    if pos == "HEAD":
        return 0
    elif pos == "TAIL":
        return -1
    else:
        return pos


def move(df: pd.DataFrame, from_index: int, to_index: int) -> pd.DataFrame:
    idx = list(df.index)
    idx.remove(idx[from_index])
    to_index = to_index if to_index != -1 else len(idx)
    idx.insert(to_index, from_index)
    return df.iloc[idx].reset_index(drop=True)


proj_str = d["proj"] if d["proj"] else d["add_proj"]
task_path = f"projects/{proj_str}/tasks.csv"
ref_path = f"projects/{proj_str}/refs.csv"
path = task_path if d["cat"] == "task" else ref_path
if d["proj"]:
    os.makedirs(f"projects/{proj_str}")
    for path in [task_path, ref_path]:
        pd.DataFrame(columns=cols).to_csv(path, index=False)
    print(f"Project '{proj_str}' created.")
elif d["add_proj"]:
    df = pd.read_csv(path)
    entry = ""
    description = ""
    while entry == "":
        entry = input(f"\tProvide {d['cat']}:\n\t\t")
    while description == "":
        description = input(f"\tDescribe {d['cat']}:\n\t\t")
    df.loc[len(df)] = [entry, description, d["flag"]]
    df = move(df, from_index=-1, to_index=define_idx(d["pos"]))
    df.to_csv(path, index=False)
    print(f"{d['cat'].capitalize()} added successfully.")
