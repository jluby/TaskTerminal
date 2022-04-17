# Task Tracking and Management with Command Line Tools and Basic Automation

## Project Overview
This project seeks to provide utilities for task tracking. Tasks are seperated by project. The core utilities of this project are:
 * Create entries then store to project-specific, user-specified lists
 * Flag important entries
 * View / sort lists, including user-provided task descriptions
 * Allow for task pulls along user-specified list chains (e.g. backburner -> tasks (active) -> archives)
    * Additionally, allow for movement across chains to be scheduled by the user
 * Allow for fully extensible user-specification of list naming and relationships (i.e. list-level 'pull_to' and 'push_to' locations)
 * Store completed tasks (with creation / completion dates) to project-specific dataframe, for easy future reference

## Repository Structure
 * `/src`: `task_terminal` package, contains CLI scripts and helpers.

## Package Installation
 To install the `task_terminal` package:
 1. Clone this repository. 
 2. From the base directory, run `pip install .` from the command line.

## Current Maintainers
 * Jack Luby, UChicago Booth Center for Applied AI - jack.o.luby@gmail.com
