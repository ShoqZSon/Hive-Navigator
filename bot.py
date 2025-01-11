import json

from publisher import Publisher
from subscriber import Subscriber
from bot_class import Bot
import threading
import sys
from pathlib import Path

# TODO: maybe outsource this config search for better testability
curr_dir = Path(__file__).parent
config_dir = curr_dir / 'configs'
configs_count = 0
for json_file in config_dir.glob('*.json'):
    with open(json_file, 'r') as f:
        config = json.load(f)
        config_type = config.get('type', None)
        if config_type:
            configs_count += 1
            print(f'Config nr:{configs_count} found at: {config_dir / json_file}')
            print(json.dumps(config, indent=4))
            if configs_count > 1:
                print('Too many configs found. Please use only one config file.')
                sys.exit(-1)
            bot_args = []
            for _, arg_value in config.items():
                bot_args.append(arg_value)

if configs_count == 0:
    print('No valid config files found.')
    sys.exit(-1)

bot_id = bot_args[1]
bot_hallNr = bot_args[2]
bot_floor = bot_args[3]

print(f'Bot ID: {bot_id}, Hall Number: {bot_hallNr}, Floor: {bot_floor}')

# TODO: build message broker config
message_broker_host = '192.168.56.106'
message_broker_port = 5672

bot = Bot(bot_id,bot_hallNr,bot_floor)
bot.setXY(85,120)

# ---- Publisher & Subscriber Initialization ---- #

pub_one_time_notification = Publisher(message_broker_host,message_broker_port)

# publisher for the bot data
pub_bot_curr_loc = Publisher(message_broker_host, message_broker_port)
# subscriber to the notifications queue
sub_task_notification = Subscriber(message_broker_host, message_broker_port)
# subscriber for the bot tasks that listens on his own queue bot.{bot_id}
sub_bot_tasks = Subscriber(message_broker_host, message_broker_port)


# ---- Connections to RabbitMQ ---- #

# establishes the connection with the messageBroker
pub_one_time_notification.connect()
pub_bot_curr_loc.connect()
sub_task_notification.connect()
sub_bot_tasks.connect()

pub_one_time_notification.publishToQueue(bot.getBotData(),
                                         queue='registration',
                                         auto_delete=True,
                                         durable=False
                                         )
pub_one_time_notification.disconnect()


# ---- Thread Area ---- #

# publishes the bot data towards the hivemind for processing
# waits until a notification from the hivemind gets sent
pub_bot_curr_loc_Thread = threading.Thread(target=bot.publishBotData,
                                           args=(pub_bot_curr_loc,)
                                           )

# subscribes the notification queue in order to let the bot know when to publish its data
sub_task_notification_Thread = threading.Thread(target=sub_task_notification.subscribeToTopic,
                                                args=(
                                                    bot.notificationCallback,
                                                    'notification_topic',
                                                    f'notifications_{bot.getId()}',
                                                    'notification.*')
                                                )
# subscribes to its own task queue for incoming tasks
sub_bot_tasks_Thread = threading.Thread(target=sub_bot_tasks.subscribeToQueue,
                                        args=(
                                            bot.addTaskCallback,
                                            bot.getId())
                                        )

executing_tasks_Thread = threading.Thread(target=bot.executeTask)

# starts the threads
pub_bot_curr_loc_Thread.start()
sub_task_notification_Thread.start()
sub_bot_tasks_Thread.start()
executing_tasks_Thread.start()

# closes the threads gracefully
pub_bot_curr_loc_Thread.join()
sub_task_notification_Thread.join()
sub_bot_tasks_Thread.join()
executing_tasks_Thread.join()

# ---- Closing the RabbitMQ connections ---- #

# closes the connection to RabbitMQ
pub_bot_curr_loc.disconnect()
sub_task_notification.disconnect()
sub_bot_tasks.disconnect()
