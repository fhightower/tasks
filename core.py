#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join("..")))
from democritus_core import *

base_directory = homeDirectoryJoin('tasks')
base_task_file = homeDirectoryJoin('tasks/tasks')

# TODO: create a typings description of a task and add it to the functions below


def search(query_string: str):
    """."""
    query_string = query_string.lower()
    matching_tasks = [task for task in tasks() if query_string in task['name'].lower()]

    # TODO: it would be nice to fall back to a fuzzy search if no results for the given query_string were found
    return matching_tasks


def update(task_name: str, updated_task_data):
    matching_task = task_with_name(task_name, fail_if_no_match=True)
    _replace_task(matching_task, _task_to_text(updated_task_data))
    return updated_task_data


def _task_to_text(task_data):
    """."""
    task_text = f'{json.dumps(task_data)}\n'
    return task_text


def delete(task_name: str):
    """."""
    matching_task = task_with_name(task_name, fail_if_no_match=True)
    _replace_task(matching_task, '')
    return matching_task


def tasks():
    """."""
    file_data = fileRead(base_task_file)
    task_list = []
    for line in file_data.split('\n'):
        try:
            json_task = jsonRead(line)
        except Exception:
            if line != '':
                print(f'Unable to parse this task as json: {line}')
        else:
            task_list.append(json_task)
    return task_list


def _replace_task(task_data, replacement: str):
    """."""
    task_file_data = fileRead(base_task_file)
    task_text = _task_to_text(task_data)
    task_file_data = task_file_data.replace(task_text, replacement)
    fileWrite(base_task_file, task_file_data)


def _write_task(task_data):
    """."""
    new_task_text = _task_to_text(task_data)
    result = fileAppend(base_task_file, new_task_text)
    return result


def task_with_name(task_name: str, fail_if_no_match=False):
    """."""
    matching_tasks = [task_data for task_data in tasks() if task_data['name'] == task_name]
    if any(matching_tasks):
        return matching_tasks[0]
    else:
        if fail_if_no_match:
            message = f'Unable to find a task with the name {task_name}'
            raise RuntimeError(message)
        return None


def add(task_name: str):
    """."""
    matching_task = task_with_name(task_name)
    if matching_task:
        message = f'There is already a task with the name "{task_name}" and no two tasks can have the same name.'
        print(message)
        return

    task_data = {
        "date_added": str(datetime.date.today()),
        "metadata": {},
        "name": task_name
    }

    _write_task(task_data)
    return task_data


if not directoryExists(base_directory):
    directoryCreate(base_directory)

if not fileExists(base_task_file):
    fileWrite(base_task_file, '')
