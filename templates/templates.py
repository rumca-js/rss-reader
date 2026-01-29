PAGINATION="""
<div class="pagination">
    <a href="{{ entries_page }}?p={{ prev_page }}">&lt;</a>
    <a href="{{ entries_page }}?p={{ next_page }}">&gt;</a>
</div>
"""

def get_view(body, title=""):
    text = """
<!doctype html>
<html>
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h2 { margin-top: 30px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin-bottom: 10px; }
        a { text-decoration: none; color: #1a0dab; }
        textarea { width: 100%; height: 200px; }
        button { margin-top: 10px; padding: 10px 20px; }
    </style>
</head>
<body>
   {body}
</body>
</html>
"""
    text = text.replace("{title}", title)
    return text.replace("{body}", body)


INDEX_TEMPLATE = """
<h1>Entrypoints</h1>
<ul>
  <li><a href="/search">Search</a>
  <li><a href="/sources">Sources</a>
  <li><a href="/add-sources">Add sources</a>
  <li><a href="/remove-source">Remove sources</a>
  <li><a href="/remove-all-sources">Remove all sources</a>
  <li><a href="/entries">Entries</a>
  <li><a href="/remove-entry">Remove entry</a>
  <li><a href="/remove-all-entries">Remove all entries</a>
  <li><a href="/stats">Stats</a>
</ul>
"""


OK_TEMPLATE = """
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
OK
</body>
</html>
"""


ENTRIES_LIST_TEMPLATE = """
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
"""

SOURCES_LIST_TEMPLATE = """
<h1>Sources {{sources_length}}</h1>

<ul>
    {% for source in sources %}
        <li>
            <img src="{{source.favicon}}" style="max-width:10%"/>
            <div class="title">{{ source.title or "Untitled source" }}</div>
            <a href="{{ source.url }}" target="_blank">
                {{ source.url }}
            </a>
        </li>
    {% endfor %}
</ul>
{{pagination_text}}
"""

SET_SOURCES_TEMPLATE = """
<h1>Define Sources</h1>

<form method="post">
    <p>One source URL per line:</p>
    <textarea name="sources">
    </textarea>
    <br>
    <button type="submit">Save Sources</button>
</form>
"""


STATS_TEMPLATE = """
{% for stat_name, stat_counter in stats.items() %}
    <div>{{stat_name}} {{stat_counter}}</div>
{% endfor %}
"""

PROJECT_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Link viewer</title>
      
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/jszip/dist/jszip.min.js"></script>
        <script src="https://unpkg.com/sql.js@1.6.0/dist/sql-wasm.js"></script>

        <link  href="styles/viewerzip.css?i=90" rel="stylesheet" crossorigin="anonymous">
        <script  src="scripts/config_python.js?i=86"></script>
        <script  src="scripts/library.js?i=86"></script>
        <script  src="scripts/webtoolkit.js?i=86"></script>
        <script  src="scripts/entries_library.js?i=86"></script>
        <script src="scripts/events.js?i=86"></script>
        <script src="scripts/ui.js?i=86"></script>
        <script src="scripts/project.js?i=86"></script>
        <script src="scripts/search.js?i=86"></script>

    </head>
<body style="padding-bottom: 6em;">

<div id="projectNavbar">
</div>

<div class="container">

  <div id="statusLine">
  </div>

  <div id="helpPlace" style="display: none;">
      <p>
      This is offline search. It might sound unbelievable, even absurd, but it is true. This search, once initialized from JSON data, is totally offline.
      </p>
      <p>
      I always liked "awesome lists", or reddit megathreads. These are community-driven collections of resources—programs, tools, or knowledge—compiled manually or semi-automatically.
      </p>
      <p>
      The idea behind the Offline Search Initiative is to create similar curated lists, but tailored for domains and channels. This approach could simplify access to focused content without relying on intensive, online search infrastructure. It does, surely has it's downsides.
      </p>
      <p>
      Input supports any words, so you can enter "Google", or "Bing". If "LIKE" is part of the input, then it will be treated as a part of WHERE SQL clause.
      </p>
      <div id="version">
      </div>
  </div>

  <span id="progressBarElement">
  </span>
  
  <span id="listData">
  </span>

  <div id="pagination">
  </div>
</div>


<!--
Unfortunately, no one can be told what the Matrix is. You have to see it for yourself.
-->


<footer id="footer" class="text-center text-lg-start bg-body-tertiary text-muted fixed-bottom">
  <div id="footerLine" class="text-center p-1" style="background-color: rgba(0, 0, 0, 0);">
  </div>

  <div class="text-center p-1" style="background-color: rgba(0, 0, 0, 0);">
      <span style="white-space: nowrap;">
      Links repository
      <a href="https://github.com/rumca-js/Internet-Places-Database">Internet-Places-Database</a>.
      </span>
      
      <span style="white-space: nowrap;">
      Captured by 
      <a href="https://github.com/rumca-js/Django-link-archive">Django-link-archive</a>.
      </span>
  </div>
</footer>

    </body>
</html>
"""

