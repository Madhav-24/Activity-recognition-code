# Purpose: Implements the activity_recognition/src/common/temporal.py module.
# Use: Provides the functions, classes, or application entry points used by this project.
# Documentation: Comments below identify the responsibility of each logical function or class block.

from collections import deque


# Logical block: defines the class TemporalBuffer and controls its related behavior.
class TemporalBuffer:

    # Logical block: defines the def __init__ and controls its related behavior.
    def __init__(
        self,
        max_length=10
    ):

        self.buffer = deque(
            maxlen=max_length
        )


    # Logical block: defines the def add and controls its related behavior.
    def add(self, value):

        self.buffer.append(
            value
        )


    # Logical block: defines the def get and controls its related behavior.
    def get(self):

        return list(
            self.buffer
        )


    # Logical block: defines the def clear and controls its related behavior.
    def clear(self):

        self.buffer.clear()


    # Logical block: defines the def average and controls its related behavior.
    def average(self):

        values = self.get()

        if not values:
            return 0.0

        return sum(values) / len(values)
