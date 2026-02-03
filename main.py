"""
Simple RSS reader
"""
import os
import sys
import threading
import shutil
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, send_from_directory

from templates.templates import *
from src.taskrunner import TaskRunner
from src.dbconnection import DbConnection
from src.serializers import entry_to_json, source_to_json
from src.controller import Controller
from src.system import System


page_size = 100

table_name = Path("data") / "table.db"
input_name = Path("data") / "input.db"

if not table_name.exists():
    print("Created db from scratch")
    shutil.copyfile(input_name, table_name)


runner = TaskRunner(table_name)
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
    table = connection.entries_table.get_table()
    order_by = [
      table.c.date_published.desc()
    ]

    if search and search != "":
        conditions = [
          table.c.title.ilike(f"%{search}%"),
          table.c.description.ilike(f"%{search}%"),
          table.c.link.ilike(f"%{search}%"),
          table.c.source_url.ilike(f"%{search}%"),
        ]
        entries = list(connection.entries_table.get_where(limit=limit,
                                                          offset=offset,
                                                          order_by=order_by,
                                                          conditions=conditions,
                                                          ))
    else:
        entries = list(connection.entries_table.get_where(limit=limit,
                                                          offset=offset,
                                                          order_by=order_by))
    return entries


def get_sources_for_request(connection, limit, offset, search=None):
    table = connection.sources_table.get_table()

    order_by = [
      connection.sources_table.get_table().c.title.desc()
    ]

    if search and search != "":
        conditions = [
          table.c.title.ilike(f"%{search}%"),
          table.c.url.ilike(f"%{search}%"),
        ]
        sources = list(connection.sources_table.get_where(limit=limit,
                                                          offset=offset,
                                                          order_by=order_by,
                                                          conditions=conditions))
    else:
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


@app.route("/search")
def search():
    return render_template_string(PROJECT_TEMPLATE, title="Yafr search")


@app.route("/sources")
def list_sources():
    connection = DbConnection(table_name)

    search = request.args.get("search")

    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    page = pagination.get_page()
    prev_page = page - 1
    next_page = page + 1

    pagination_text = "";
    pagination_text += '<div id="pagination">'
    pagination_text += '<nav>'
    pagination_text += '<ul class="pagination">'
    if page > 2:
        pagination_text += '<a href="?p=1" class="btnNavigation page-link">|&lt;</a>';
    if page > 1:
        pagination_text += f'<a href="?p={prev_page}" class="btnNavigation page-link">&lt;</a>';
    pagination_text += '<li class="page-item">'
    pagination_text += f'<a href="?p={next_page}" class="btnNavigation page-link" >&gt;</a>';
    pagination_text += '</li>'
    pagination_text += '</ul>'
    pagination_text += '</nav>'
    pagination_text += '</div>'

    sources_len = connection.sources_table.count()

    sources = get_sources_for_request(connection, limit, offset, search)
    template_text = SOURCES_LIST_TEMPLATE
    template_text = template_text.replace("{{pagination_text}}", pagination_text)

    html_text = get_view(template_text, title="Sources")

    return render_template_string(html_text, sources=sources, sources_length=sources_len)


@app.route("/add-sources", methods=["GET", "POST"])
def configure_sources():
    connection = DbConnection(table_name)

    if request.method == "POST":
        raw_text = request.form.get("sources", "")

        controller = Controller(connection)
        controller.add_sources_text(raw_text)

    html_text = get_view(ADD_SOURCES_TEMPLATE, title="Add sources")
    return render_template_string(html_text, raw_data="")


@app.route("/entry-rules", methods=["GET", "POST"])
def entry_rules():
    connection = DbConnection(table_name)
    controller = Controller(connection)

    if request.method == "POST":
        raw_text = request.form.get("sources", "")
        controller.add_entry_rules(raw_text)

    sources = []
    html_text = get_view(DEFINE_ENTRY_RULES_TEMPLATE, title="Set Entry Rules")

    urls = controller.get_rule_urls()
    raw_data = "\n".join(urls)
    return render_template_string(html_text, raw_data=raw_data)


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
        controller = Controller(connection)
        controller.remove_source(source)

        html_text = get_view(OK_TEMPLATE, title="Remove source")
        return render_template_string(html_text)
    else:
        html_text = get_view(NOK_TEMPLATE, title="Remove source")
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

    system = System.get_object()

    stats_map = {}
    stats_map["Entries"] = entries_len
    stats_map["Sources"] = sources_len
    stats_map["Entry rules"] = entry_rules_len
    stats_map["System state"] = system.is_system_ok()

    html_text = get_view(STATS_TEMPLATE, title="Stats")
    return render_template_string(html_text, stats=stats_map)


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


@app.route("/api/stats")
def api_stats():
    connection = DbConnection(table_name)

    entries_len = connection.entries_table.count()
    sources_len = connection.sources_table.count()
    entry_rules_len = connection.entry_rules.count()

    system = System.get_object()

    stats_map = {}
    stats_map["entries_len"] = entries_len
    stats_map["sources_len"] = sources_len
    stats_map["system_state"] = system.is_system_ok()

    return jsonify(stats_map)


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


def print_file(afile):
    path = Path(afile)
    text = path.read_text()
    lines = text.split("\n")
    lines=set(lines)
    return lines


if __name__ == "__main__":
    debug_mode = False

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        debug_mode = arg in ["true", "1", "yes", "on"]

    if (debug_mode and os.environ.get("WERKZEUG_RUN_MAIN") == "true") or not debug_mode:
        thread = threading.Thread(
            target=runner.start,
            args=(),
            daemon=True
        )

        thread.start()

    app.run(host="0.0.0.0", port=5000, debug=False)
