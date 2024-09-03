import json

def decode_json_object(json_object) -> dict:
    """Decodes the content of the jsonObject to a string and then to dictionary
    :param json_object: jsonObject to be decoded
    :return: dict of a task"""
    task_str = json_object.decode('utf-8')
    task = json.loads(task_str)

    return task