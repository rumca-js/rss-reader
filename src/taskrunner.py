import time
from webtoolkit import BaseUrl


class TaskRunner(object):
    def __init__(self, connection):
        self.connection = connection

    def check_source(self, source):
        url = self.get_source_url(source)
        response = url.get_response()
        if response.is_valid():
            source_properties = url.get_properties()
            self.set_source(source, source_properties)

            self.remove_source_entries(source)

            entries = url.get_entries()
            for entry in entries:
                self.add_entry(source, entry)

    def get_source_url(self, source):
        url = BaseUrl(url=source)
        return url

    def remove_source_entries(self, source):
        """
        TODO Remove all entries with source_url = source
        """
        pass

    def set_source(self, source, source_properties=None):
        link = source_properties["link"]

        if self.connection.sources_table.exists(url=link):
            """
            TODO update source
            """
            return

        title = source_properties.get("title", "")
        if not title:
            title = ""
        language = source_properties.get("language", "")
        if not language:
            language = ""

        properties = {
               "url": source,
               "enabled" : True,
               "source_type" : "",
               "title" : title,
               "category_name": "",
               "subcategory_name": "",
               "export_to_cms": False,
               "remove_after_days": 5,
               "language": language,
               "age": 0,
               "fetch_period": 3600,
               "auto_tag": "",
               "entries_backgroundcolor_alpha": 1.0,
               "entries_backgroundcolor": "",
               "entries_alpha": 1.0,
               "proxy_location": "",
               "auto_update_favicon":False,
               "xpath": "",
       }

        self.connection.sources_table.insert_json(properties)

    def add_entry(self, source, entry):
        if self.connection.entries_table.exists(link=entry["link"]):
            return

        entry["source_url"] = source

        if "source" in entry:
            del entry["source"]
        if "feed_entry" in entry:
            del entry["feed_entry"]
        if "link_canonical" in entry:
            del entry["link_canonical"]
        if "tags" in entry:
            del entry["tags"]

        self.connection.entries_table.insert_json(entry)

    def set_sources(self, sources):
        for source in sources:
            self.set_source(source)

    def on_done(self, response):
        pass

    def start(self, init_sources=None):
        """
        Called from a thread
        """
        if init_sources:
            for source in init_sources:
                self.set_source(source)

        print("Starting reading")

        while True:
            sources = self.connection.sources_table.get_sources()

            for source in sources:
                print(f"{source.url} {source.title}: Reading")
                self.check_source(source.url)
                print(f"{source.url} {source.title}: Reading DONE")
                time.sleep(1)

            SLEEP_TIME_6h = 27600
            time.sleep(SLEEP_TIME_6h)

    def print(self):
        for entry in self.connection.entries_table.get_entries():
            self.print_entry(entry)

    def print_entry(self, entry):
        print(entry.title)
        print(entry.link)
