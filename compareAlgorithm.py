from queue import Queue
import json
from math import fabs

def compare_userLoc_botLoc(task:dict, bot_data:dict):
    """ The algorithm to determine which bot is the best fit for the task.
    Decides by comparing every bot_data x,y coordinate + the hall-nr with the corresponding values in usr_data

    :param task:
    :param bot_data:

    :return:
    """
    comparison_storage = {}

    print(f'Comparison Storage: {comparison_storage}')
    print("Comparing userLoc and botLoc")
    print(f"task: {task}")
    print(f"botLoc: {bot_data}")

    #location = task['location']
    location = {'terminal':2,'hall':0,'floor':1,'x':21,'y':320} # this is only temporary but necessary for now

    # iterate through the bot_data dictionary
    for key,value in bot_data.items():
        print(f'Comparing {key}:{value} with {location}')

        if value['floor'] == location['floor']:
            hall_diff = int(fabs(value['hall'] - location['hall']))
            x_diff = int(fabs(value['x'] - location['x']))
            y_diff = int(fabs(value['y'] - location['y']))

            comparison_storage[key] = {
                'hall_diff':hall_diff,
                'x_diff':x_diff,
                'y_diff':y_diff
            }

    # Sort by 'name' in the inner dictionaries
    sorted_comparison_storage = dict(sorted(comparison_storage.items(), key=lambda item: item[1]['hall_diff']))
    print(sorted_comparison_storage)

    best_queue = next(iter(sorted_comparison_storage))
    print(best_queue)

    return task,best_queue