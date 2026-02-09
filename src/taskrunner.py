import time
from datetime import datetime, timedelta
from webtoolkit import BaseUrl, RemoteUrl
import traceback

from .dbconnection import DbConnection
from .controller import Controller
from .system import System
from .sourcedata import SourceData
from .sources import Sources
from .entries import Entries
from .sourcewriter import SourceWriter
from .applogging import AppLogging


class TaskRunner(object):
    def __init__(self, table_name):
        self.connection = None
        self.controller = None
        self.table_name = table_name

        system = System.get_object()
        system.set_thread_ok()

        self.waiting_due = None
        self.start_reading = True

    def check_source(self, source):
        sourcedata = SourceData(self.connection)
        sourcedata.mark_read(source)

        url = self.get_source_url(source)
        if not url:
            return

        response = url.get_response()
        if response:
            if response.is_valid():
                source_properties = url.get_properties()

                sources = Sources(self.connection)
                sources.set(source.url, source_properties)
                sources.delete_entries(source)

                entries = url.get_entries()
                for entry in entries:
                    entries = Entries(self.connection)
                    entries.add(entry, source)
            else:
                AppLogging.error("URL:{source.url} Response is invalid")
        else:
            AppLogging.error("URL:{source.url} No response")

    def get_source_url(self, source):
        config = self.connection.configurationentry.get()
        try:
            if self.is_remote_server() or self.is_config_remote_server():
                # TODO dates are strings
                location = config.remote_webtools_server_location
                if not location:
                    location = RemoteUrl.get_remote_server_location()

                url = RemoteUrl(url=source.url, remote_server_location=location)
            else:
                url = BaseUrl(url=source.url)
            return url
        except:
            print(f"Removing invalid source:{source.url}")
            sources = Sources(self.connection)
            sources.delete(id=source.id)
    
    def is_remote_server(self):
        return RemoteUrl.get_remote_server_location()

    def is_config_remote_server(self):
        config = self.connection.configurationentry.get()
        if config.remote_webtools_server_location is None:
            return False
        if config.remote_webtools_server_location == "":
            return False
        if config.remote_webtools_server_location == "None":
            return False
        return True

    def on_done(self, response):
        pass

    def start(self, init_sources=None):
        """
        Called from a thread
        """
        try:
            self.connection = DbConnection(self.table_name)
            self.controller = Controller(connection=self.connection)

            self.sources_data = SourceData(self.connection)

            self.setup_start()

            if init_sources:
                self.init_sources(init_sources)

            self.controller.close()
            self.connection.close()

            self.process_sources()
        except Exception as e:
            traceback.print_exc()

    def init_sources(self, init_sources):
        for source_url in init_sources:
            sources = Sources(self.connection)
            sources.set(source_url)

    def setup_start(self):
        entries = Entries(self.connection)
        entries_len = entries.count()
        sources = Sources(self.connection)
        sources_len = sources.count()

        print(f"Entries: {entries_len}")
        print(f"Sources: {sources_len}")

    def process_sources(self):
        self.add_due_sources()

        print("Starting reading")
        while True:
            system = System.get_object()

            self.start_reading = False

            source_ids = self.get_sources_ids()

            for index, source_id in enumerate(source_ids):
                self.connection = DbConnection(self.table_name)
                self.controller = Controller(connection=self.connection)

                self.process_source(index, source_id, len(source_ids))

                self.controller.close()
                self.connection.close()
                system.set_thread_ok()

            self.waiting_due = datetime.now() + self.get_due_time()
            system.set_thread_ok()
            self.wait_for_due_time()

    def get_due_time(self):
        return timedelta(hours = 1)

    def wait_for_due_time(self):
        system = System.get_object()
        while True:
            system.set_thread_ok()

            self.add_due_sources()

            if self.start_reading:
                return True

            if datetime.now() < self.waiting_due:
                time.sleep(10)
            else:
                self.start_reading = True
                return True

    def get_sources_ids(self):
        """
        we assume that we have a small number of sources
        """
        self.connection = DbConnection(self.table_name)
        self.controller = Controller(connection=self.connection)

        sources = Sources(self.connection)
        source_count = sources.count()

        source_ids = []
        for source in self.connection.sources_table.get_sources():
            source_ids.append(source.id)

        self.controller.close()
        self.connection.close()

        return source_ids

    def process_source(self, index, source_id, source_count):
        sources = Sources(self.connection)
        source = sources.get(id=source_id)

        if not source:
            print("Could not find source")
            return

        if not source.enabled:
            print("Not enabled")
            return

        if self.controller.is_entry_rule_triggered(source.url):
            print("rule triggered")
            sources = Sources(connection=self.connection)
            sources.delete(id=source.id)
            return

        sources_data = SourceData(self.connection)

        if not sources_data.is_update_needed(source):
            print("Update not needed")
            return

        print(f"{index}/{source_count} {source.url} {source.title}: Reading")
        self.check_source(source)

        #writer = SourceWriter(connection=self.connection, source=source)
        #writer.write()

        print(f"{index}/{source_count} {source.url} {source.title}: Reading DONE")
        time.sleep(1)

    def add_due_sources(self):
        self.connection = DbConnection(self.table_name)
        self.controller = Controller(connection=self.connection)

        status = False

        sources = self.controller.get_sources_to_add()
        if sources:
            self.start_reading = True
            self.controller.add_sources(sources)
            status = True

        self.controller.close()
        self.connection.close()
        return status
