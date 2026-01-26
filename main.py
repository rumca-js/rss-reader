"""
Simple RSS reader
"""
from flask import Flask, render_template_string, jsonify
from sqlalchemy import create_engine

from webtoolkit import BaseUrl
from linkarchivetools.utils.reflected import (
   ReflectedEntryTable,
   ReflectedSourceTable,
   ReflectedTable,
)


sources = [
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCJ0-OtVpF0wOKEqT2Z1HEtA',
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCQG4cX86zZ51IU2cerZgPSA',
]


class Connection(object):
    def __init__(self, db_file):
        self.db_file = db_file

        self.engine = create_engine(f"sqlite:///{self.db_file}")
        self.connection = self.engine.connect()

        self.entries_table = ReflectedEntryTable(engine=self.engine, connection=self.connection)
        self.sources_table = ReflectedSourceTable(engine=self.engine, connection=self.connection)

    def truncate(self):
        self.entries_table.truncate()
        self.sources_table.truncate()

        table = ReflectedTable(engine=self.engine, connection=self.connection)
        table.vacuum()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None


class Runner(object):
    def __init__(self, connection):
        self.connection = connection

    def run_item(self, source):
        url = BaseUrl(url=source)
        response = url.get_response()
        if response.is_valid():
            source_properties = url.get_properties()
            self.add_source(source, source_properties)

            self.remove_source_entries(source)

            #self.responses[source] = response
            entries = url.get_entries()
            for entry in entries:
                self.add_entry(source, entry)

    def remove_source_entries(source):
        """
        TODO Remove all entries with source_url = source
        """
        pass

    def add_source(self, source, source_properties):
        link = source_properties["link"]

        if self.connection.sources_table.is_url(link):
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
        if self.connection.entries_table.is_entry_link(entry["link"]):
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

        self.connection.entries_table.insert_entry_json(entry)

    def on_done(self, response):
        pass

    def start(self):
        for source in sources:
            self.run_item(source)

    def print(self):
        for entry in self.connection.entries_table.get_entries():
            self.print_entry(entry)

    def print_entry(self, entry):
        print(entry.title)
        print(entry.link)


app = Flask(__name__)
connection = Connection("table.db")
runner = Runner(connection)


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>YouTube Feed Entries</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h2 { margin-top: 30px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin-bottom: 10px; }
        a { text-decoration: none; color: #1a0dab; }
    </style>
</head>
<body>
    <h1>YouTube Feed Entries</h1>

        {% for entry in entries %}
            <li>
                {% if entry.title and entry.link %}
                    <a href="{{ entry.link }}" target="_blank">
                        {{ entry.title }}
                    </a>
                {% elif entry.title %}
                    {{ entry.title }}
                {% endif %}
            </li>
        {% endfor %}
</body>
</html>
"""


@app.route("/")
def index():
    entries = list(connection.entries_table.get_entries())

    return render_template_string(HTML_TEMPLATE, entries=entries)


@app.route("/api/entries")
def api_entries():
    json_data = []
    entries = list(connection.entries_table.get_entries())
    for entry in entries:
        json_entry_data = {
           "link" : entry.link,
           "title" : entry.title,
        }
        json_data.append(json_entry_data)

    return jsonify(json_data)


if __name__ == "__main__":
    runner.start()

    app.run(debug=True)
