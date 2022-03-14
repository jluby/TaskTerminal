import pandas as pd


def print_ls(proj: str) -> None:
    tasks = pd.read_csv(f"projects/{proj}/todo.csv")
    print(tasks)
