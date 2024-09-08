from queue import Queue
import json

def compare_userLoc_botLoc(task:dict, bot_data:dict):
    """ The algorithm to determine which bot is the best fit for the task.
    Decides by comparing every bot_data x,y coordinate + the hall-nr with the corresponding values in usr_data

    :param task:
    :param bot_data:

    :return:
    """
    print("Comparing userLoc and botLoc")
    print(f"task: {task}")
    print(f'UserLoc: ...')
    print(f"botLoc: {bot_data}")


    myqueue = 'tasks.bot1'

    return task,myqueue