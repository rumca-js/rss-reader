import time
from datetime import datetime, timedelta
from webtoolkit import BaseUrl

from .dbconnection import DbConnection
from .controller import Controller


class TaskRunner(object):
    def __init__(self, table_name):
        self.connection = None
        self.controller = None
        self.table_name = table_name

        self.waiting_due = None
        self.start_reading = True

    def check_source(self, source):
        url = self.get_source_url(source.url)
        response = url.get_response()
        if response.is_valid():
            source_properties = url.get_properties()

            self.controller.set_source(source.url, source_properties)
            self.controller.remove_source_entries(source)

            entries = url.get_entries()
            for entry in entries:
                self.controller.add_entry(source, entry)

    def get_source_url(self, source):
        url = BaseUrl(url=source)
        return url

    def on_done(self, response):
        pass

    def start(self, init_sources=None):
        """
        Called from a thread
        """
        self.setup_start()

        if init_sources:
            self.init_sources(init_sources)

        self.process_sources()

    def init_sources(self, init_sources):
        for source in init_sources:
            self.controller.set_source(source)

    def setup_start(self):
        self.connection = DbConnection(self.table_name)
        self.controller = Controller(connection=self.connection)

        entries_len = self.controller.get_entries_count()
        sources_len = self.controller.get_sources_count()

        print(f"Entries: {entries_len}")
        print(f"Sources: {sources_len}")

    def process_sources(self):
        print("Starting reading")

        while True:
            self.start_reading = False
            source_count = self.controller.get_sources_count()
            sources = self.connection.sources_table.get_sources()

            for index, source in enumerate(sources):
                if not source.enabled:
                    continue

                print(f"{index}/{source_count} {source.url} {source.title}: Reading")
                self.check_source(source)
                print(f"{index}/{source_count} {source.url} {source.title}: Reading DONE")
                time.sleep(1)

            self.waiting_due = datetime.now() + timedelta(hours = 6)

            if datetime.now() < self.waiting_due and not self.start_reading:
                time.sleep(10)
