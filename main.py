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
from src.controller import Controller


page_size = 100

table_name = Path("data") / "table.db"
input_name = Path("data") / "input.db"

if not table_name.exists():
    print("Created db from scratch")
    shutil.copyfile(input_name, table_name)


#engine = DbConnection.create_engine(table_name)
app = Flask(__name__)


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


def get_entries_for_request(connection, limit, offset, search=None):
    order_by = [
      connection.entries_table.get_table().c.date_published.desc()
    ]

    # TODO implement search

    entries = list(connection.entries_table.get_where(limit=limit,
                                                      offset=offset,
                                                      order_by=order_by))
    return entries


def get_sources_for_request(connection, limit, offset):
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
    html_text = get_view(INDEX_TEMPLATE, title="YAFR - Yet another feed reader")
    return render_template_string(html_text)


@app.route('/scripts/<path:filename>')
def scripts(filename):
    return send_from_directory("scripts/", filename)


@app.route('/styles/<path:filename>')
def styles(filename):
    return send_from_directory("styles/", filename)


@app.route("/entries")
def entries():
    connection = DbConnection(table_name)

    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    entries = get_entries_for_request(connection, limit, offset)

    html_text = get_view(ENTRIES_LIST_TEMPLATE, title="Entries")

    return render_template_string(html_text, entries=entries)


@app.route("/search")
def search():
    return render_template_string(PROJECT_TEMPLATE, title="Yafr search")


@app.route("/sources")
def list_sources():
    connection = DbConnection(table_name)

    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    page = pagination.get_page()
    prev_page = page - 1
    next_page = page + 1

    pagination_text = "";
    if page > 2:
        pagination_text += '<a href="?p=1">|&lt;</a>';
    pagination_text += f'<a href="?p={prev_page}">&lt;</a>';
    pagination_text += f'<a href="?p={next_page}">&gt;</a>';

    sources_len = connection.sources_table.count()

    sources = get_sources_for_request(connection, limit, offset)
    template_text = SOURCES_LIST_TEMPLATE
    template_text = template_text.replace("{{pagination_text}}", pagination_text)

    html_text = get_view(SOURCES_LIST_TEMPLATE, title="Sources")

    return render_template_string(html_text, sources=sources, sources_length=sources_len)


@app.route("/add-sources", methods=["GET", "POST"])
def configure_sources():
    connection = DbConnection(table_name)

    if request.method == "POST":
        raw_text = request.form.get("sources", "")

        controller = Controller(connection)
        controller.add_sources_text(raw_text)

    sources = []
    html_text = get_view(SET_SOURCES_TEMPLATE, title="Add sources")
    return render_template_string(html_text, sources=sources)


@app.route("/entry-rules", methods=["GET", "POST"])
def entry_rules():
    connection = DbConnection(table_name)

    if request.method == "POST":
        raw_text = request.form.get("sources", "")

        controller = Controller(connection)
        controller.add_entry_rules(raw_text)

    sources = []
    html_text = get_view(SET_SOURCES_TEMPLATE, title="Add Entry Rules")
    return render_template_string(html_text, sources=sources)


#### JSON

@app.route("/api/entries")
def api_entries():
    connection = DbConnection(table_name)

    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    search = request.args.get("search")

    json_entries = []
    entries = get_entries_for_request(connection, limit, offset, search)

    for entry in entries:
        if entry.source_id:
            entry_source = connection.sources_table.get(id=entry.source_id)
            json_entry_data = entry_to_json(entry, with_id=True, source=entry_source)
            json_entries.append(json_entry_data)

    json_data = {}
    json_data["entries"] = json_entries

    return jsonify(json_data)


@app.route("/remove-all-entries")
def remove_all_entries():
    connection = DbConnection(table_name)

    connection.entries_table.truncate()

    html_text = get_view(OK_TEMPLATE, title="Remove all entries")
    return render_template_string(html_text)


@app.route("/remove-all-sources")
def remove_all_sources():
    connection = DbConnection(table_name)

    connection.sources_table.truncate()
    html_text = get_view(OK_TEMPLATE, title="Remove all sources")
    return render_template_string(html_text)


@app.route("/remove-source")
def remove_source():
    connection = DbConnection(table_name)

    source_id = request.args.get("id")

    source = connection.sources_table.get(id=source_id)
    if source:
        connection.entries_table.delete_where({"source_id" : source.id})

    html_text = get_view(OK_TEMPLATE, title="Remove source")
    return render_template_string(html_text)


@app.route("/remove-entry")
def remove_entry():
    connection = DbConnection(table_name)

    entry_id = request.args.get("id")

    entry = connection.entries_table.get(id=entry_id)
    if source:
        connection.entries_table.delete_where({"id" : entry.id})

    html_text = get_view(OK_TEMPLATE, title="Remove entry")
    return render_template_string(html_text)


@app.route("/stats")
def stats():
    connection = DbConnection(table_name)

    entries_len = connection.entries_table.count()
    sources_len = connection.sources_table.count()
    entry_rules_len = connection.entry_rules.count()

    stats_map = {}
    stats_map["Entries"] = entries_len
    stats_map["Sources"] = sources_len
    stats_map["Entry rules"] = entry_rules_len

    html_text = get_view(STATS_TEMPLATE, title="Stats")
    return render_template_string(html_text, stats=stats_map)


@app.route("/api/sources")
def api_sources():
    connection = DbConnection(table_name)

    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    json_sources = []
    sources = get_sources_for_request(connection, limit, offset)

    for source in sources:
        json_data_source = source_to_json(source, with_id=True)
        json_sources.append(json_data_source)

    json_data = {}
    json_data["sources"] = json_sources

    return jsonify(json_data)


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        runner = TaskRunner(table_name)

        thread = threading.Thread(
            target=runner.start,
            args=(),
            daemon=True
        )

        thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
