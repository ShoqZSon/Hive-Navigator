import publisher as p
import subscriber as s


class Bot(p.Publisher,s.Subscriber):
    def __init__(self):
        super().__init__()