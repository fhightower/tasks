#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join("..")))
from democritus_core import (
    random_selection,
    date_to_epoch,
    epoch_time_now,
    date_standardize_all_args,
    date_standardize,
    list_count,
)

import core

TO_DONT_METADTA_KEY = 'toDont'


def _is_three_months_or_more_ago(date: str) -> bool:
    """."""
    old_date = date_to_epoch(date)
    now = epoch_time_now()
    ninety_days_difference = 7776000

    if now - old_date >= ninety_days_difference:
        return True
    else:
        return False


def _is_on_do_list(task_data) -> bool:
    """Return whether or not the task represented by the task_data is on the do list."""
    return task_data['metadata'][TO_DONT_METADTA_KEY]['list'] == 'do'


def search(query: str, ignore_done_results=True):
    """."""
    results = core.search(query)
    # remove tasks on the 'deleted' list
    updated_results = [result for result in results if result['metadata'][TO_DONT_METADTA_KEY]['list'] != 'deleted']
    if ignore_done_results:
        # remove tasks on the 'done' list
        updated_results = [result for result in updated_results if result['metadata'][TO_DONT_METADTA_KEY]['list'] != 'done']
    return updated_results


def move_to_do(task_name: str):
    """Move the task with the given name to the "do" list."""
    do_tasks = do()
    # I'm checking for >= 3 rather than == 3 just to be safe
    if len(do_tasks) >= 3:
        message = f'There are already three tasks on the "Do" list. You can\'t add any more.'
        print(message)
        return

    return _move_task_to_list(task_name, 'do')


def _celebrate():
    """."""
    path = random_selection([0, 1, 2, 3])
    if path < 3:
        celebration_phrases = ['BOOM!', 'Yeeeessssssss', 'Score!', 'Nicely done ;)', 'Noice!']
        s = random_selection(celebration_phrases)
        for i in s:
            print(i, end='')
            time.sleep(0.25)
    else:
        from IPython.display import clear_output

        s = '=       O'
        for i in range(1, 10):
            if i < 9:
                new_string = f'{s[:i]}-{s[i:]}'
                print(new_string)
            else:
                new_string = f'{s[:i-1]}X'
                print(new_string)
            time.sleep(0.25)
            clear_output(wait=True)


def move_to_done(task_name: str):
    """Move the task with the given name to the "dont" list."""
    _celebrate()
    finished_task = core.task_with_name(task_name, fail_if_no_match=True)
    finished_task['metadata'][TO_DONT_METADTA_KEY]['date_done'] = core._datestamp()
    core.update(task_name, finished_task)
    return _move_task_to_list(task_name, 'done')


def move_to_dont(task_name: str):
    """Move the task with the given name to the "dont" list."""
    return _move_task_to_list(task_name, 'dont')


def delete(task_name: str):
    """Move the task with the given name to the "deleted" list."""
    return _move_task_to_list(task_name, 'deleted')


def _move_task_to_list(task_name: str, list_name: str):
    """Move the task with the given task_name to the given list_name."""
    updated_task = core.task_with_name(task_name, fail_if_no_match=True)
    updated_task['metadata'][TO_DONT_METADTA_KEY]['list'] = list_name
    return core.update(task_name, updated_task)


def do():
    """List tasks on the "Do" list."""
    tasks = _tasks_with_list_name('do')
    return tasks


def do_pretty_print():
    """Print out the tasks of the "Do" list in a readable way."""
    print('\n\n\n===TO DO:==========================================================================\n')
    for i in do():
        print(f'> {i["name"]}')
    print('\n===================================================================================\n\n\n')


def done():
    """List tasks on the "Done" list."""
    tasks = _tasks_with_list_name('done')
    return tasks


def dont():
    """List tasks on the "Dont" list."""
    tasks = _tasks_with_list_name('dont')
    return tasks


def _tasks_with_list_name(list_name, task_list=None):
    """."""
    if task_list is None:
        task_list = tasks()

    filtered_tasks = [task for task in task_list if task['metadata'][TO_DONT_METADTA_KEY]['list'] == list_name]
    return filtered_tasks


def tasks():
    """."""
    all_tasks = core.tasks()
    to_dont_tasks = [task for task in all_tasks if task['metadata'].get(TO_DONT_METADTA_KEY)]
    return to_dont_tasks


def add(task_name: str):
    """Add a task (it will be added to the "Dont" list)."""
    new_task_data = core.add(task_name)
    if new_task_data:
        new_task_data['metadata'][TO_DONT_METADTA_KEY] = {'list': 'dont'}
        return core.update(task_name, new_task_data)


def _delete_old_tasks():
    """."""
    task_list = tasks()
    for task in task_list:
        if not _is_on_do_list(task):
            if _is_three_months_or_more_ago(task['date_added']):
                delete(task['name'])


_delete_old_tasks()


def metrics(time_frame_start='30 days ago', time_frame_end='now'):
    """Show metrics on completed tasks over time."""
    time_frame_start = date_standardize(time_frame_start)
    time_frame_end = date_standardize(time_frame_end)
    finished_tasks = done()
    metrics = list_count([task['metadata']['toDont'].get('date_done', None) for task in finished_tasks])
    # ignore tasks without a "Date Done"
    del metrics[None]
    applicable_metrics = {
        k: v
        for k, v in metrics.items()
        if date_standardize(k) > time_frame_start and date_standardize(k) < time_frame_end
    }
    return applicable_metrics
