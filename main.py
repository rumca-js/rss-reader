"""
Simple RSS reader
"""
import os
import threading
from flask import Flask, render_template_string, jsonify, request

from src.taskrunner import TaskRunner
from src.dbconnection import DbConnection
from src.serializers import entry_to_json, source_to_json


init_sources = [
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCJ0-OtVpF0wOKEqT2Z1HEtA',
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCQG4cX86zZ51IU2cerZgPSA',
]
page_size = 400


app = Flask(__name__)
connection = DbConnection("table.db")
runner = TaskRunner(connection)


PAGINATION="""
<div class="pagination">
    {% if page > 1 %}
        <a href="{{ url_for('api_entries') }}?p={{ page - 1 }}">« Previous</a>
    {% else %}
        <span>« Previous</span>
    {% endif %}

    <span>Page {{ page }}</span>

    {% if has_next %}
        <a href="{{ url_for('api_entries') }}?p={{ page + 1 }}">Next »</a>
    {% else %}
        <span>Next »</span>
    {% endif %}
</div>
"""


ENTRIES_LIST_TEMPLATE = """
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

<ul>
{% for entry in entries %}
    <li class="entry">
    <img src="{{entry.thumbnail}}"/>
        <div class="title">
            {% if entry.link %}
                <a href="{{ entry.link }}" target="_blank" rel="noopener">
                    {{ entry.title or "Untitled entry" }}
                </a>
            {% else %}
                {{ entry.title or "Untitled entry" }}
            {% endif %}
        </div>

        <div class="meta">
            {% if entry.author %}By {{ entry.author }}{% endif %}
            {% if entry.album %} • Album: {{ entry.album }}{% endif %}
            {% if entry.language %} • Language: {{ entry.language }}{% endif %}
            {% if entry.status_code %} • HTTP {{ entry.status_code }}{% endif %}
        </div>

        {% if entry.description %}
            <div class="description">
                {{ entry.description }}
            </div>
        {% endif %}

        <div class="stats">
            {% if entry.page_rating is not none %}
                Rating: {{ entry.page_rating }}
            {% endif %}
            {% if entry.page_rating_votes %}
                • Votes: {{ entry.page_rating_votes }}
            {% endif %}
            {% if entry.page_rating_visits %}
                • Visits: {{ entry.page_rating_visits }}
            {% endif %}
            {% if entry.age %}
                • Age: {{ entry.age }}
            {% endif %}
        </div>

        <div class="flags">
            {% if entry.bookmarked %}
                <span class="bookmarked">★ Bookmarked</span>
            {% endif %}
            {% if entry.permanent %}
                <span class="permanent">Permanent</span>
            {% endif %}
        </div>

        <div class="dates">
            {% if entry.date_published %}
                Published: {{ entry.date_published }}
            {% endif %}
            {% if entry.date_created %}
                • Created: {{ entry.date_created }}
            {% endif %}
            {% if entry.date_update_last %}
                • Updated: {{ entry.date_update_last }}
            {% endif %}
            {% if entry.date_last_modified %}
                • Modified: {{ entry.date_last_modified }}
            {% endif %}
            {% if entry.date_dead_since %}
                • Dead since: {{ entry.date_dead_since }}
            {% endif %}
        </div>
    </li>
{% endfor %}
</ul>
</body>
</html>
"""

SOURCES_LIST_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Sources</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin-bottom: 12px; }
        a { color: #1a0dab; text-decoration: none; }
        .title { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Sources</h1>

    <ul>
        {% for source in sources %}
            <li>
                <div class="title">{{ source.title or "Untitled source" }}</div>
                <a href="{{ source.url }}" target="_blank">
                    {{ source.url }}
                </a>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

SET_SOURCES_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Configure Sources</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        textarea { width: 100%; height: 200px; }
        button { margin-top: 10px; padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>Define Sources</h1>

    <form method="post">
        <p>One source URL per line:</p>
        <textarea name="sources">
        </textarea>
        <br>
        <button type="submit">Save Sources</button>
    </form>
</body>
</html>
"""


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


@app.route("/")
def index():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    entries = list(connection.entries_table.get_entries(limit=limit, offset=offset))

    return render_template_string(ENTRIES_LIST_TEMPLATE, entries=entries)


@app.route("/entries")
def entries():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    entries = list(connection.entries_table.get_entries(limit=limit, offset=offset))

    return render_template_string(ENTRIES_LIST_TEMPLATE, entries=entries)


@app.route("/sources")
def list_sources():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    sources = list(connection.sources_table.get_sources(limit=limit, offset=offset))
    return render_template_string(SOURCES_LIST_TEMPLATE, sources=sources)


def read_sources_input(input_text):
    sources = [
        line.strip()
        for line in input_text.splitlines()
        if line.strip()
    ]

    return sources


@app.route("/set-sources", methods=["GET", "POST"])
def configure_sources():
    if request.method == "POST":
        raw_text = request.form.get("sources", "")

        sources = read_sources_input(raw_text)

        runner.set_sources(sources)

        #return redirect(url_for("configure_sources"))

    sources = []
    return render_template_string(SET_SOURCES_TEMPLATE, sources=sources)

#### JSON

@app.route("/api/entries")
def api_entries():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    json_data = []
    entries = list(connection.entries_table.get_entries(limit=limit, offset=offset))
    for entry in entries:
        json_entry_data = entry_to_json(entry)
        json_data.append(json_entry_data)

    return jsonify(json_data)


@app.route("/api/sources")
def api_sources():
    pagination = PagePagination(request)
    limit = pagination.get_limit()
    offset = pagination.get_offset()

    json_data = []
    sources = list(connection.sources_table.get_sources(limit=limit, offset=offset))

    for source in sources:
        json_data_source = source_to_json(source)
        json_data.append(json_data_source)

    return jsonify(json_data)


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        thread = threading.Thread(
            target=runner.start,
            args=(),
            daemon=True
        )

        thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True)
