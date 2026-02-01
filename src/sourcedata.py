import json
from pathlib import Path
from datetime import datetime, timedelta


class SourceData(object):
    def __init__(self):
        self.sources_data = None

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

    def get_source_data(self, source):
        return self.sources_data.get(source.url)

    def mark_read(self, source):
        self.sources_data[source.url] = {}
        self.sources_data[source.url]["date_fetched"] = datetime.now().isoformat()

    def is_update_needed(self, source):
        this_source_data = self.get_source_data(source)
        if this_source_data:
            date_fetched = this_source_data.get("date_fetched")
            date_fetched = datetime.fromisoformat(date_fetched)

            if datetime.now() - date_fetched < timedelta(hours=1):
                return False

        return True

    def remove(self):
        sources_data = Path("sources_data.json")
        if sources_data.exists():
            sources_data.unlink()
