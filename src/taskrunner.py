import time
from datetime import datetime, timedelta
from webtoolkit import BaseUrl

from .dbconnection import DbConnection
from .controller import Controller
from .system import System
from .sourcedata import SourceData


class TaskRunner(object):
    def __init__(self, table_name):
        self.connection = None
        self.controller = None
        self.table_name = table_name
        self.sources_data = SourceData()

        system = System.get_object()
        system.set_thread_ok()

        self.waiting_due = None
        self.start_reading = True

    def check_source(self, source):
        self.sources_data.mark_read(source)

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
        self.connection = DbConnection(self.table_name)
        self.controller = Controller(connection=self.connection)

        self.setup_start()

        if init_sources:
            self.init_sources(init_sources)

        self.controller.close()

        self.process_sources()

    def init_sources(self, init_sources):
        for source in init_sources:
            self.controller.set_source(source)

    def setup_start(self):
        entries_len = self.controller.get_entries_count()
        sources_len = self.controller.get_sources_count()

        print(f"Entries: {entries_len}")
        print(f"Sources: {sources_len}")

    def process_sources(self):
        print("Starting reading")

        self.add_due_sources()

        while True:
            self.start_reading = False

            source_ids = self.get_sources_ids()

            for index, source_id in enumerate(source_ids):
                self.connection = DbConnection(self.table_name)
                self.controller = Controller(connection=self.connection)

                self.process_source(index, source_id, len(source_ids))

                self.controller.close()
                system = System.get_object()
                system.set_thread_ok()

            self.waiting_due = datetime.now() + self.get_due_time()
            system.set_thread_ok()
            self.wait_for_due_time()

    def get_due_time(self):
        return timedelta(hours = 1)

    def wait_for_due_time(self):
        while True:
            if self.start_reading:
                return True

            if datetime.now() < self.waiting_due:
                time.sleep(10)

            if self.add_due_sources():
                continue

    def get_sources_ids(self):
        """
        we assume that we have a small number of sources
        """
        self.connection = DbConnection(self.table_name)
        self.controller = Controller(connection=self.connection)

        source_count = self.controller.get_sources_count()

        source_ids = []
        for source in self.connection.sources_table.get_sources():
            source_ids.append(source.id)

        self.controller.close()

        return source_ids

    def process_source(self, index, source_id, source_count):
        source = self.connection.sources_table.get(id=source_id)

        if not source:
            print("Could not find source")
            return

        if not source.enabled:
            return

        if self.controller.is_entry_rule_triggered(source.url):
            self.connection.sources_table.delete(id=source.id)
            return

        if not self.sources_data.is_update_needed(source):
            return

        print(f"{index}/{source_count} {source.url} {source.title}: Reading")
        self.check_source(source)
        self.sources_data.write_sources_data()
        print(f"{index}/{source_count} {source.url} {source.title}: Reading DONE")
        time.sleep(1)

    def add_due_sources(self):
        sources = self.controller.get_sources_to_add()
        if sources:
            self.start_reading = True
            self.controller.add_sources(sources)
            return True
        return False
