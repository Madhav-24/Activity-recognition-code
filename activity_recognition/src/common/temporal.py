from collections import deque


class TemporalBuffer:

    def __init__(
        self,
        max_length=10
    ):

        self.buffer = deque(
            maxlen=max_length
        )


    def add(self, value):

        self.buffer.append(
            value
        )


    def get(self):

        return list(
            self.buffer
        )


    def clear(self):

        self.buffer.clear()


    def average(self):

        values = self.get()

        if not values:
            return 0.0

        return sum(values) / len(values)
