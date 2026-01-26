from flask import Flask, render_template_string, jsonify

from webtoolkitex import UrlEx


sources = [
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCJ0-OtVpF0wOKEqT2Z1HEtA',
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCQG4cX86zZ51IU2cerZgPSA',
]




class Runner(object):
    def __init__(self):
        self.entries = {}
        self.source_data = {}

    def run_item(self, source):
        url = UrlEx(url=source)
        response = url.get_response()
        if response.is_valid():
            #self.responses[source] = response
            self.entries[source] = url.get_entries()
            source_properties = url.get_properties()
            self.source_data[source] = source_properties

    def on_done(self, response):
        pass

    def start(self):
        for source in sources:
            self.run_item(source)

    def print_respones(self):
        for source in self.responses:
            response = self.responses[source]
            print(f"{source} {response}")

    def print(self):
        for source in self.entries:
            entries = self.entries[source]
            for entry in entries:
                self.print_entry(entry)

    def print_entry(self, entry):
        if "title" in entry:
            print(entry["title"])
        if "link" in entry:
            print(entry["link"])


app = Flask(__name__)
runner = Runner()


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

    {% for source, entries in data.items() %}
        <h2>{{ source }}</h2>
        <ul>
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
        </ul>
    {% endfor %}
</body>
</html>
"""


@app.route("/")
def index():
    runner.start()

    # normalize entries so templates don't explode
    data = {}
    for source, entries in runner.entries.items():
        data[source] = [
            {
                "title": entry.get("title"),
                "link": entry.get("link"),
            }
            for entry in entries
        ]

    return render_template_string(HTML_TEMPLATE, data=data)


@app.route("/api/entries")
def api_entries():
    runner.start()
    return jsonify(runner.entries)


if __name__ == "__main__":
    app.run(debug=True)
