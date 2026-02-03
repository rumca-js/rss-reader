from pathlib import Path
from .sources import Sources
from .system import System


class SourceWriter(object):
    def __init__(self, connection, source):
        self.connection = connection
        self.source = source

    def write(self):
        system = System.get_object()

        html = self.get_html()
        path = Path(system.get_export_dir())
        if not path.exists():
            path.mkdir()

        path = self.get_file_name()
        path.write_text(html)

    def get_file_name(self):
        sources = Sources(self.connection)
        path = Path(sources.get_file_name(self.source))
        return path

    def get_html(self):
        limit = 100
        offset = 0
        entries = self.connection.entries_table.get_where({"source_id" : self.source.id}, offset=offset, limit=limit)

        entries_html = ""

        for entry in entries:
            entries_html += self.get_entry_html(entry)

        text = f"""
        <html>
        <body>
            <div>
            {entries_html}
            </div>
        </body>
        </html>
        """

        return text

    def get_entry_html(self, entry):
        return f"""
        <div>
        {entry.link}
        {entry.title}
        </div>
        """
