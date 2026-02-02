# YAFR - Yet Another Feed Reader

A dead-simple, read-only RSS feed reader built for speed and portability.

YAFR does exactly one thing: reads RSS feeds.
No accounts, no sync logic, no opinions. Just feeds -> entries -> read.

# Why "Yet Another"?

Because it actually is - but it’s intentionally minimal.

YAFR focuses on:
 - Speed
 - Simplicity
 - Portability

No writing, starring, tagging, or social features. Just read.

Try it!
 - https://hub.docker.com/r/rozbujnik/yafr

You can use RSS links from https://rumca-js.github.io/feeds to initialize you RSS client!

# Features

 - SQLite database - Portable, easy to back up. Can be shared or copied between machines or tasks
 - Python + SQLAlchemy - Simple, explicit schema. Easy to inspect or extend
 - Flask server - Lightweight HTTP interface
 - No frontend framework required
 - Fast - Minimal processing. No unnecessary abstractions
 - Read-only - Feeds and entries only. No mutation beyond fetching and storing

# Endpoints

Allows to integrate your project with YAFR.

 - /search - search view
 - /sources - sources list
 - /stats - stats

 API
 - /api/entries - returns JSON about entries
 - /api/sources - returns JSON about sources

