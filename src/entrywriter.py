from pathlib import Path
from .system import System


class PagePagination:
    def __init__(self, page_num, page_size):
        self.page_num = page_num
        self.page_size = page_size

    def get_page(self):
        return self.page_num

    def get_offset(self):
        page = self.get_page()
        return (page - 1) * self.page_size

    def get_limit(self):
        return self.page_size


class EntryPageWriter(object):
    def __init__(self, connection, page_num=1, page_size=100):
        self.connection = connection
        self.page_num = page_num
        self.page_size = page_size

    def write(self):
        system = System.get_object()

        html = self.get_html()
        path = Path(system.get_export_dir())
        if not path.exists():
            path.mkdir()

        path = Path(self.get_file_name())
        path.write_text(html)

    def get_file_name(self):
        system = System.get_object()
        return Path(system.get_export_dir() / f"index_{self.page_num}.html"

    def get_entries(self):
        p = PagePagination(page_num=self.page_num, page_size=self.page_size)
        limit = p.get_limit()
        offset = p.get_offset()

        table = connection.entries_table.get_table()
        order_by = [
          table.c.date_published.desc()
        ]

        entries = list(connection.entries_table.get_where(limit=limit,
                                                          offset=offset,
                                                          order_by=order_by))
        return entries

    def get_html(self):
        entries = self.get_entries()

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


class EntryWriter(object):
    def __init__(self, connection, number_of_pages=10, page_size=100):
        self.connection = connection
        self.number_of_pages = number_of_pages
        self.page_size = page_size

    def write(self):
        for page in range(self.number_of_pages):
            w = EntryPageWriter(connection=self.connection,
                    page_num=page_num,
                    page_size=self.page_size)
            w.write()
