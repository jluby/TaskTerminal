# Task Tracking and Management with Command Line Tools and Basic Automation

## Project Overview
This project seeks to provide utilities for task tracking. Tasks are seperated by project. The core utilities of this project are:
 * Create entries then store to project-specific, user-specified lists
 * View / sort lists, including user-provided task descriptions
 * Allow for backburner tasks which can be pulled into active list (and pushed back)
 * Store completed tasks (with creation / completion dates) to project-specific dataframe, for easy future reference
    - Upon storage, tasks can additionally be flagged for importance if likely to be needed in the future

## Repository Structure
 * `/src`: `task_tracker` package, contains CLI scripts and helpers.

## Package Installation
 To install the `task_tracker` package:
 1. Clone this repository. 
 2. From the base directory, run `pip install .` from the command line.

## Current Maintainers
 * Jack Luby, UChicago Booth Center for Applied AI - jack.o.luby@gmail.com
