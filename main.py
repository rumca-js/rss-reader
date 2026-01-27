"""
Simple RSS reader
"""
from flask import Flask, render_template_string, jsonify
import threading

from src.taskrunner import TaskRunner
from src.dbconnection import DbConnection


init_sources = [
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCJ0-OtVpF0wOKEqT2Z1HEtA',
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCQG4cX86zZ51IU2cerZgPSA',
]


app = Flask(__name__)
connection = DbConnection("table.db")
runner = TaskRunner(connection)


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
        <textarea name="sources">{% for s in sources %}{{ s }}\n{% endfor %}</textarea>
        <br>
        <button type="submit">Save Sources</button>
    </form>
</body>
</html>
"""


@app.route("/")
def index():
    entries = list(connection.entries_table.get_entries())

    return render_template_string(ENTRIES_LIST_TEMPLATE, entries=entries)


@app.route("/entries")
def index():
    entries = list(connection.entries_table.get_entries())

    return render_template_string(ENTRIES_LIST_TEMPLATE, entries=entries)


@app.route("/sources")
def list_sources():
    sources = list(connection.sources_table.get_sources())
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

        return redirect(url_for("configure_sources"))

    sources = connection.sources_table.get_sources()
    return render_template_string(SET_SOURCES_TEMPLATE, sources=sources)

#### JSON

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


@app.route("/api/sources")
def api_sources():
    json_data = []
    sources = list(connection.sources_table.get_sources())

    for source in sources:
        json_data.append({
            "url": source.url,
            "title": source.title,
        })

    return jsonify(json_data)


if __name__ == "__main__":
    thread = threading.Thread(
        target=runner.start,
        args=(),
        daemon=True
    )

    thread.start()

    app.run(debug=True)
