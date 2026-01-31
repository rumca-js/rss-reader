from pathlib import Path
from datetime import datetime


def read_line_things(input_text):
    sources = [
        line.strip()
        for line in input_text.splitlines()
        if line.strip()
    ]

    return sources


class Controller(object):
    def __init__(self, connection):
        self.connection = connection

    def add_entry(self, source, entry):
        if self.connection.entries_table.exists(link=entry["link"]):
            return

        entry["source_url"] = source.url

        if "source" in entry:
            del entry["source"]
        if "feed_entry" in entry:
            del entry["feed_entry"]
        if "link_canonical" in entry:
            del entry["link_canonical"]
        if "tags" in entry:
            del entry["tags"]

        entry["date_created"] = datetime.now()
        entry["source_id"] = source.id

        try:
            self.connection.entries_table.insert_json(entry)
        except Exception as E:
            print(E)
            print(entry)
            raise

    def add_sources(self, sources):
        self.start_reading = True

        for source_url in sources:
            self.set_source(source_url)

    def add_sources_text(self, raw_text):
        # write raw_text to file
        output_path = Path("sources.txt")
        with output_path.open("a", encoding="utf-8", errors="ignore") as f:
            f.write("\n")
            f.write(raw_text)

    def get_sources_to_add(self):
        output_path = Path("sources.txt")
        if output_path.exists():
            raw_text = output_path.read_text(encoding="utf-8")
            if raw_text:
                sources = read_line_things(raw_text)
                output_path.unlink()
                return sources

    def set_source(self, source_url, source_properties=None):
        link = source_url

        title = ""
        language = ""
        favicon = ""

        if source_properties:
            title = source_properties.get("title", "")
            language = source_properties.get("language", "")
            favicon = source_properties.get("thumbnail", "")

        if not title:
            title = ""
        if not language:
            language = ""
        if not favicon:
            favicon = ""

        source_iter = self.connection.sources_table.get_where({"url":link})
        source = next(source_iter, None)
        if source:
            """
            TODO update source
            """
            data = {}
            data["title"] = title
            data["favicon"] = favicon
            data["language"] = favicon

            self.connection.sources_table.update_json_data(source.id, data)
            return

        properties = {
               "url": link,
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
               "favicon": favicon,
       }

        self.connection.sources_table.insert_json(properties)

    def remove_source_entries(self, source):
        """
        TODO Remove all entries with source_url = source
        """
        self.connection.entries_table.delete_where({"source_url" : source.url})

    def add_entry_rules(self, raw_input):
        self.connection.entry_rules.truncate()

        entry_rule_urls = read_line_things(raw_input)
        for entry_rule_url in entry_rule_urls:
            self.add_entry_rule(entry_rule_url)

    def add_entry_rule(self, entry_rule):
        entries = self.connection.entry_rules.get_where({"trigger_rule_url" : entry_rule})
        entry = next(entries, None)

        if not entry:
            data = {}
            data["trigger_rule_url"] = entry_rule
            data["enabled"] = True
            data["priority"] = 0
            data["rule_name"] = entry_rule
            data["trigger_text"] = ""
            data["trigger_text_hits"] = 0
            data["trigger_text_fields"] = ""
            data["block"] = True
            data["trust"] = False
            data["auto_tag"] = ""
            data["apply_age_limit"] = 0
            data["browser_id"] = 0

            self.connection.entry_rules.insert_json_data(data)

    def truncate(self):
        self.connection.entries_table.truncate()
        self.connection.sources_table.truncate()

    def print(self):
        for entry in self.connection.entries_table.get_entries():
            self.print_entry(entry)

    def print_entry(self, entry):
        print(entry.title)
        print(entry.link)

    def get_entries_count(self):
        return self.connection.entries_table.count()

    def get_sources_count(self):
        return self.connection.sources_table.count()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
