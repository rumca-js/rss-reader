from pathlib import Path
import json
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
        self.sources_data = None

        self.thread_date = datetime.now()

        self.waiting_due = None
        self.start_reading = True

        self.read_sources_data()

    def read_sources_data(self):
        path = Path("sources_data.json")
        if path.exists():
            raw_text = path.read_text()
            try:
                self.sources_data = json.loads(raw_text)
            except Exception as E:
                self.sources_data = {}
        else:
            self.sources_data = {}

    def write_sources_data(self):
        raw_text = json.dumps(self.sources_data)

        path = Path("sources_data.json")
        path.write_text(raw_text)

    def check_source(self, source):
        self.sources_data[source.url] = {}
        self.sources_data[source.url]["date_fetched"] = datetime.now().isoformat()

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
                self.thread_date = datetime.now()

            self.waiting_due = datetime.now() + timedelta(hours = 1)
            self.thread_date = datetime.now()

            if datetime.now() < self.waiting_due and not self.start_reading:
                if self.add_due_sources():
                    continue

                time.sleep(10)

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

        rules = self.connection.entry_rules.get_where({"trigger_rule_url" : source.url})
        rules = next(rules, None)
        if rules:
            self.connection.source.delete(id=source.id)
            return

        this_source_data = self.sources_data.get(source.url)
        if this_source_data:
            date_fetched = this_source_data.get("date_fetched")
            date_fetched = datetime.fromisoformat(date_fetched)
            if datetime.now() - date_fetched < timedelta(hours=1):
                return

        print(f"{index}/{source_count} {source.url} {source.title}: Reading")
        self.check_source(source)
        self.write_sources_data()
        print(f"{index}/{source_count} {source.url} {source.title}: Reading DONE")
        time.sleep(1)

    def add_due_sources(self):
        sources = self.controller.get_sources_to_add()
        if sources:
            self.start_reading = True
            self.controller.add_sources(sources)
            return True
        return False
