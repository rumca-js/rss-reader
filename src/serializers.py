
def entry_to_json(entry):
    json_entry = {}

    json_entry["title"] = entry.title
    json_entry["description"] = entry.description
    json_entry["link"] = entry.link
    json_entry["date_created"] = entry.date_created
    json_entry["date_published"] = entry.date_published
    json_entry["date_dead_since"] = entry.date_dead_since
    json_entry["date_update_last"] = entry.date_update_last
    json_entry["date_last_modified"] = entry.date_last_modified
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

    json_entry["source__title"] = ""
    json_entry["source__url"] = ""
    json_entry["backgroundcolor"] = None
    json_entry["alpha"] = 1.0

    #json_entry["status_code_str"] = status_code_to_text(entry.status_code)
    #json_entry["contents_hash"] = json_encode_field(entry.contents_hash)
    #json_entry["body_hash"] = json_encode_field(entry.body_hash)
    #json_entry["meta_hash"] = json_encode_field(entry.meta_hash)
    #json_entry["last_browser"] = ""

    return json_entry


def source_to_json(source):
    json_data = {
       "link" : source.url,
       "title" : source.title,
       "description" : source.description,
       "language" : source.language,
       "favicon" : source.favicon,
    }
    return json_data
