# TaskTerminal

TaskTerminal is a package which provides task tracking utilities in Terminal with basic automation to make your TODOs readily accessible and easy to manage.

<img width="402" alt="sample_lst" src="https://user-images.githubusercontent.com/43190780/168383804-76c4bb1a-5d55-42db-b143-28067803430f.png">

## Project Overview

This project seeks to provide utilities for task tracking. Tasks are seperated by project. The core utilities of this project are:

-   Create entries then store to project-specific, user-specified lists
-   View / sort lists, including user-provided task descriptions
-   Allow for task pulls along user-specified list chains (e.g. backburner -> tasks (active) -> archives)
-   Additionally, allow for movement across chains to be scheduled by the user
-   Allow for fully extensible user-specification of list naming and relationships (i.e. list-level 'pull_to' and 'push_to' locations)
-   Flag important entries

## Repository Structure

-   `/src/task_terminal`: `task_terminal` package, contains CLI scripts and helpers.
-   `/helpers`: Files which help CLI function but cannot be called.
-   `config.json`: User configuration. Sets file types, names, attributes, and relationships per user specification. See 'Configuration' below.
-   `helpers.py`: General helper functions for setup and printing.
-   `templates.json`: Print templates for help in error handling.
    Other files in `task_terminal` can be called from the command line after installation. Their usage is outlined in the `tutorial.sh` file.

## Package Installation

 To install the `task_terminal` package:

  1. Clone this repository.
  2. Read the 'Configuration' section and establish a package configuration which will best suit your needs.
  3. From the base directory, run `pip install .` from the command line.

## Configuration

 List types and relationships are configurable via the package's `config.json` file. To configure, follow these steps:

1.  Establish desired file types. These will be the keys of the configuration directory.

<img width="346" alt="config_base" src="https://user-images.githubusercontent.com/43190780/167225525-f6806abc-c1a3-4c5c-b749-08b0f9cc7dc6.png">

-   NOTE: It is recommended that file types be set prior to establishing task entries. Users should be aware that entries within a given file would likely be lost upon package re-configuration.

2.  Establish file-level attributes. As values paired to their corresponding files, these attributes will be contained in their own dictionary. Available attributes are:
    REQUIRED:

-   `aliases`: `list` - A list of aliases by which file can be identified in CLI commands. These must be unique to each file.
    OPTIONAL: 

-   `pull_to`: `str` - File to which `pull` command will move file.

-   `push_to`: `str` - File to which `pull` command will move file when '-U' flag is provided.

-   `stat`: `str` - Statistic to be displayed at the task-level. These will typically be one of 'time_estimate', indicating how long the task is expected to take, or 'datetime_scheduled', indicating the date at which the task is to be moved to its 'pull_to' file.

-   `attrs`: `list` - Optional attributes for display of file lists. These can be chosen from:
    -   'show_total': show the sum of a project list's 'time_estimate' values
    -   'hours': Ask for a 'time_estimate' when a task is created within that list
    -   'schedule': Ask for a 'datetime_scheduled' at which a task will be moved to its 'pull_to' file

-   `stats_from_prev`: `list` - Statistics to be shown from a file's 'push_to' location. These can be chosen from:
    -   'n': Number of tasks in the preceding list
    -   'total': The sum of the preceding list's 'time_estimate' values
        A fully established `config.json` file might look something like this:

<img width="372" alt="full_config" src="https://user-images.githubusercontent.com/43190780/167225752-f7e63a9b-cfe2-4028-b4c9-ca159e68579e.png">

3.  Re-install the package with `pip install .` to establish configuration options.

## Usage

 See file-level docstrings in `src`.

## Current Maintainers

-   Jack Luby, UChicago Booth Center for Applied AI - jack.o.luby@gmail.com
