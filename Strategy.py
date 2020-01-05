import datetime
from pytz import timezone
import sys


class Strategy:
    def __init__(self):
        # check required methods and attributes are present
        required_attributes = ["name",  # strategy name
                               "backend",  # backend interface object
                               ]
        for attribute in required_attributes:
            if not hasattr(self, attribute):
                raise ValueError(f"Can't create Strategy without {attribute}")

        self.schedule = {}
        self.frequencies = {}

        self.context = {}

    def run(self):
        print("Running!")
        for method, (trading_days, tod) in self.frequencies.items():
            assert hasattr(self, method), f"{self} doesn't have method {method}"
            self.schedule[method] = [0, tod]

        if not self.backend.is_open():
            next_open = self.backend.get_next_open()
            print(f"Market isn't open right now.")
            self.backend.step(next_open)

        while True:
            print(f"Today is {self.backend.get_time().date()}")

            # decrement trading days on schedule
            for method in self.schedule.keys():
                self.schedule[method][0] -= 1

            methods_to_run = self.get_methods_to_run_today()
            print(f"\tAbout to run: {methods_to_run}")
            while len(methods_to_run) > 0:
                # figure out which method will be next
                next_method = min(methods_to_run, key=lambda x: self.schedule[x][1])
                tod = self.frequencies[next_method][1]
                print(f"\tThe next method is: {next_method} to run at {tod} EST")

                # get backend time
                dt = self.backend.get_time()
                print(f"\tThe current time is {dt}")

                # wait until appropriate time to run method
                sleep_until_time = datetime.datetime.combine(dt.date(), tod)
                # assert sleep_until_time > dt
                self.backend.step(sleep_until_time)

                # run method
                getattr(self, next_method)()
                methods_to_run.remove(next_method)

                self.schedule[method][0] = self.frequencies[method][0]

            # get time of next open
            next_open = self.backend.get_next_open()
            print(f"Done for today!")
            print(f"The next open is {next_open}")
            self.backend.step(next_open)

                
    def schedule_function(self, function_name, trading_days, tod):
        self.frequencies[function_name] = (trading_days, tod)

    def get_methods_to_run_today(self):
        methods_to_run = []
        for method, (trading_days, tod) in self.schedule.items():
            if trading_days <= 0:
                methods_to_run.append(method)
        return methods_to_run
            

