"""
Simple RSS reader
"""
import os
import threading
import shutil
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, send_from_directory

from templates.templates import *
from src.taskrunner import TaskRunner
from src.dbconnection import DbConnection
from src.serializers import entry_to_json, source_to_json


page_size = 100

table_name = Path("data") / "table.db"
input_name = Path("data") / "input.db"

if not table_name.exists():
    print("Created db from scratch")
    shutil.copyfile(input_name, table_name)


app = Flask(__name__)
connection = DbConnection(table_name)
runner = TaskRunner(connection)


class PagePagination:
    def __init__(self, request):
        self.request = request

    def get_page(self):
        page = self.request.args.get("p", default=1, type=int)
        return max(page, 1)

    def get_offset(self):
        page = self.get_page()
        return (page - 1) * page_size

    def get_limit(self):
        return page_size


def get_entries_for_request(limit, offset):
    order_by = [
      connection.entries_table.get_table().c.date_published.desc()
    ]

    entries = list(connection.entries_table.get_where(limit=limit,
                                                      offset=offset,
                                                      order_by=order_by))
    return entries


def get_sources_for_request(limit, offset):
    order_by = [
      connection.sources_table.get_table().c.title.desc()
    ]

    sources = list(connection.sources_table.get_where(limit=limit,
                                                      offset=offset,
                                                      order_by=order_by))
    print(f"len {sources}")
    return sources


@app.route("/")
def index():
    return render_template_string(INDEX_TEMPLATE)


@app.route('/scripts/<path:filename>')
def scripts(filename):
    return send_from_directory("scripts/", filename)


@app.route('/styles/<path:filename>')
def styles(filename):
    return send_from_directory("styles/", filename)


@app.route("/entries")
def entries():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    entries = get_entries_for_request(limit, offset)

    return render_template_string(ENTRIES_LIST_TEMPLATE, entries=entries)


@app.route("/search")
def search():
    return render_template_string(PROJECT_TEMPLATE)


@app.route("/sources")
def list_sources():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    sources = get_sources_for_request(limit, offset)
    return render_template_string(SOURCES_LIST_TEMPLATE, sources=sources)


def read_sources_input(input_text):
    sources = [
        line.strip()
        for line in input_text.splitlines()
        if line.strip()
    ]

    return sources


@app.route("/add-sources", methods=["GET", "POST"])
def configure_sources():
    if request.method == "POST":
        raw_text = request.form.get("sources", "")

        sources = read_sources_input(raw_text)

        runner.add_sources(sources)

    sources = []
    return render_template_string(SET_SOURCES_TEMPLATE, sources=sources)

#### JSON

@app.route("/api/entries")
def api_entries():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    search = request.args.get("search")
    # TODO implement search

    json_entries = []
    entries = get_entries_for_request(limit, offset)

    for entry in entries:
        json_entry_data = entry_to_json(entry, with_id=True)
        json_entries.append(json_entry_data)

    json_data = {}
    json_data["entries"] = json_entries

    return jsonify(json_data)


@app.route("/api/sources")
def api_sources():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    json_sources = []
    sources = get_sources_for_request(limit, offset)

    for source in sources:
        json_data_source = source_to_json(source, with_id=True)
        json_sources.append(json_data_source)

    json_data = {}
    json_data["sources"] = json_sources

    return jsonify(json_data)


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        entries_len = connection.entries_table.count()
        sources_len = connection.sources_table.count()
        print(f"Entries: {entries_len}")
        print(f"Sources: {sources_len}")

        thread = threading.Thread(
            target=runner.start,
            args=(),
            daemon=True
        )

        thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
