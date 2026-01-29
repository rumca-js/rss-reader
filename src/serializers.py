def iso_z(dt):
    if dt:
        return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")

def entry_to_json(entry, with_id=False, source=None):
    json_entry = {}

    if with_id:
        json_entry["id"] = entry.id
    json_entry["title"] = entry.title
    json_entry["description"] = entry.description
    json_entry["link"] = entry.link
    json_entry["date_created"] = iso_z(entry.date_created)
    json_entry["date_published"] = iso_z(entry.date_published)
    json_entry["date_dead_since"] = iso_z(entry.date_dead_since)
    json_entry["date_update_last"] = iso_z(entry.date_update_last)
    json_entry["date_last_modified"] = iso_z(entry.date_last_modified)
    json_entry["bookmarked"] = entry.bookmarked
    json_entry["permanent"] = entry.permanent
    json_entry["author"] = entry.author
    json_entry["album"] = entry.album
    json_entry["language"] = entry.language
    json_entry["page_rating_contents"] = entry.page_rating_contents
    json_entry["page_rating_votes"] = entry.page_rating_votes
    json_entry["page_rating_visits"] = entry.page_rating_visits
    json_entry["page_rating"] = entry.page_rating
    json_entry["age"] = entry.age
    json_entry["status_code"] = entry.status_code
    json_entry["thumbnail"] = entry.thumbnail

    json_entry["source_title"] = ""
    json_entry["source_url"] = entry.source_url
    if source:
        json_entry["source_title"] = source.title
        json_entry["source"] = source_to_json(source)

    json_entry["backgroundcolor"] = None
    json_entry["alpha"] = 1.0

    #json_entry["status_code_str"] = status_code_to_text(entry.status_code)
    #json_entry["contents_hash"] = json_encode_field(entry.contents_hash)
    #json_entry["body_hash"] = json_encode_field(entry.body_hash)
    #json_entry["meta_hash"] = json_encode_field(entry.meta_hash)
    #json_entry["last_browser"] = ""

    return json_entry


def source_to_json(source, with_id=False):
    json_data = {
       "link" : source.url,
       "title" : source.title,
       "language" : source.language,
       "favicon" : source.favicon,
    }

    json_data["id"] = source.id
    return json_data
