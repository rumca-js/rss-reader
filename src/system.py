from pathlib import Path
from datetime import datetime, timedelta


class System(object):
    instance = None

    def __init__(self):
        self.set_thread_ok()

    def get_object():
        if System.instance is None:
            System.instance = System()
        return System.instance

    def set_thread_ok(self):
        self.thread_date = datetime.now()

    def is_system_ok(self):
        return self.is_read_thread_ok()

    def is_read_thread_ok(self):
        if self.thread_date:
            return datetime.now() - self.thread_date < timedelta(minutes=5)

    def get_indicators(self):
        data = {}
        data["Reading thread"] = self.is_read_thread_ok()

    def get_export_dir(self):
        """
        TODO url to file name
        """
        return Path("export")

