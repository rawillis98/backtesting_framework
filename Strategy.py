import pyfolio as pf
import matplotlib.pyplot as plt
import logging
import logging.config
import os
import time
import datetime
from pytz import timezone
import sys
import pandas as pd


class Strategy:
    def __init__(self):
        # check required methods and attributes are present
        required_attributes = ["name",  # strategy name
                               "backend",  # backend interface object
                               ]
        for attribute in required_attributes:
            if not hasattr(self, attribute):
                raise ValueError(f"Can't create Strategy without {attribute}")

        # get logger
        strat_id = self.get_strategy_id()
        name_strp = self.name.replace(" ", "_")
        self.log_file_name = f"logs/{name_strp}-{strat_id}.log"

        # verify backend account access
        self.backend.get_portfolio()

        # create logging folder
        if not os.path.exists("logs"):
            logging.debug("./logs does not exist. Creating ./logs")
            os.mkdir("logs")

        # initialize logging
        logging.config.fileConfig('logging.conf', disable_existing_loggers=True)
        self.__logger = logging.getLogger(__name__)

        self.frequencies = {}
        self.schedule = {}
        self.equity = {}        
        self.context = {}
        if hasattr(self, "init_context"):
            self.__logger.info("Running init_context")
            getattr(self, "init_context")()

    def get_strategy_id(self):
        return int(time.time())

    def analyze(self):
        equity_series = pd.Series(self.equity)
        returns = equity_series.pct_change()
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
        pf.create_full_tear_sheet(returns)
        plt.show()

    def run(self):
        self.__logger.info("Running!")
        for method, (trading_days, tod) in self.frequencies.items():
            assert hasattr(self, method), f"{self} doesn't have method {method}"
            self.schedule[method] = [0, tod]

        if not self.backend.is_open():
            next_open = self.backend.get_next_open()
            self.__logger.info(f"Market isn't open right now.")
            self.backend.step(next_open)

        while self.backend.get_time() < self.backend.end_time:
            today = self.backend.get_time().date()
            self.__logger.debug(f"Today is {today}")

            # decrement trading days on schedule
            for method in self.schedule.keys():
                self.schedule[method][0] -= 1

            methods_to_run = self.get_methods_to_run_today()
            self.__logger.info(f"\tMethods scheduled for {today}: {methods_to_run}")
            self.equity[self.backend.get_time()] = self.backend.get_equity() 
            while len(methods_to_run) > 0:
                # get backend time
                dt = self.backend.get_time()
                self.__logger.debug(f"\tThe current time is {dt} EST")

                # figure out which method will be next
                next_method = min(methods_to_run, key=lambda x: self.schedule[x][1])
                tods = [x[1] for x in self.schedule.values()]
                tod = self.frequencies[next_method][1]

                # remove the method from the todo list
                methods_to_run.remove(next_method)

                # skip if the tod has already passed
                if tod < dt.time():
                    self.__logger.debug(f"\tSkipping method {next_method} because tod {tod} < dt.time() {dt.time()}")
                    continue
                self.__logger.info(f"\tThe next method is: {next_method} to run at {tod} EST")

                # wait until appropriate time to run method
                sleep_until_time = datetime.datetime.combine(dt.date(), tod)
                assert sleep_until_time >= dt, f"Sleep until time {sleep_until_time} must be gtoe to dt {dt}"
                self.backend.step(sleep_until_time)

                # run method
                self.__logger.info(f"\tRunning method {next_method}")
                getattr(self, next_method)()

                self.schedule[method][0] = self.frequencies[method][0]

            # get time of next open
            next_open = self.backend.get_next_open()
            self.__logger.info(f"\tDone for today! The next open is {next_open}")
            self.backend.step(next_open)

        self.equity[self.backend.get_time()] = self.backend.get_equity() 
        self.logger.info("DONE!")
        return

                
    def schedule_function(self, function_name, trading_days, tod):
        self.frequencies[function_name] = (trading_days, tod)

    def get_methods_to_run_today(self):
        methods_to_run = []
        for method, (trading_days, tod) in self.schedule.items():
            if trading_days <= 0:
                methods_to_run.append(method)
        return methods_to_run
            

