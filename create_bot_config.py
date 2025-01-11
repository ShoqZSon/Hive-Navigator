import json
from pathlib import Path
import argparse
import os

def create_file(file_path: Path, arguments: dict):
    arguments['type'] = 'bot_config'
    with open(file_path, 'w') as file:
        json.dump(arguments, file)

def set_permissions(file_path: Path):
    # Set permissions: 0o700 grants read, write, execute for the owner (user)
    # 0o700 = rwx------ (Owner can read, write, and execute)
    os.chmod(file_path, 0o744)
    print(f"Permissions set to 744 for {file_path}")

if __name__ == '__main__':
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Script to create the config file for a bot.")

    # Add arguments
    parser.add_argument('--config_name', type=str, required=False, default='bot_config', help='(optional) Name of the config file stored in "configs" directory. Defaults to "bot_config".')
    parser.add_argument('--bot_id', type=str, required=True, help="Sets the id for the bot like: bot_<id>.")
    parser.add_argument('--hall_nr', type=int, required=True, help="Sets the starting hall number for the bot.")
    parser.add_argument('--floor', type=int, required=True, help="Sets the starting floor for the bot.")
    parser.add_argument('--additional_info', type=str, required=False, default="--", help="(optional) Additional information of the bot. ")

    # Parse the arguments
    args = parser.parse_args()

    args_dict = vars(args)
    args_dict['config_name'] = args.config_name + '.json'
    for arg_name, arg_value in args_dict.items():
        print(f"{arg_name}: {arg_value}")

    curr_dir = Path(__file__).parent
    config_dir = curr_dir / 'configs'
    config_dir.mkdir(exist_ok=True)

    config_name = args.config_name
    config_path = config_dir / config_name
    if config_path.exists():
        print(f'Config file for {args_dict['config_name']} already exists.')
        print(f'Overwrites are not allowed.')
        exit(-1)
    try:
        create_file(config_path, args_dict)
        print(f"Config file created successfully at {config_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(-2)

    try:
        set_permissions(config_path)
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(-3)