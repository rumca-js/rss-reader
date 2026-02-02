from pathlib import Path
from datetime import datetime
from .sourcedata import SourceData
from .sources import Sources


def read_line_things(input_text):
    sources = [
        line.strip()
        for line in input_text.splitlines()
        if line.strip()
    ]

    sources = set(sources)
    sources = list(sources)

    return sources


class Controller(object):
    def __init__(self, connection):
        self.connection = connection

    def add_sources(self, sources):
        self.start_reading = True

        for source_url in sources:
            if not self.is_entry_rule_triggered(source_url):
                sources = Sources(self.connection)
                sources.set(source_url)

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

    def is_entry_rule_triggered(self, url) -> bool:
        rules = self.connection.entry_rules.get_where({"trigger_rule_url" : url})
        rules = next(rules, None)
        if rules:
            return True
        return False

    def add_entry_rules(self, raw_input):
        self.connection.entry_rules.truncate()

        entry_rule_urls = read_line_things(raw_input)
        for entry_rule_url in entry_rule_urls:
            self.add_entry_rule(entry_rule_url)

    def get_rule_urls(self):
        urls = []

        rules = self.connection.entry_rules.get_where(limit=10000)
        for rule in rules:
            urls.append(rule.trigger_rule_url)

        return urls

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

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
