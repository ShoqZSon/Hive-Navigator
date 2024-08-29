import hivemind_class as hive


hivemind = hive.Hivemind('127.0.0.1',65432)

# fills the task queue from the webserver data
hivemind.listenToConn()