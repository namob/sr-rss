import requests
from datetime import date, timedelta, datetime
import re

lastBuildDate = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:sr="http://www.sverigesradio.se/podrss" xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
  <channel>
    <itunes:new-feed-url>https://api.sr.se/api/rss/pod/4892</itunes:new-feed-url>
    <atom:link href="https://api.sr.se/api/rss/pod/4892" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{lastBuildDate}</lastBuildDate>
    <image>
      <title>Mammas Nya Kille</title>
      <link>https://www.sverigesradio.se/mammasnyakille</link>
      <url>https://static-cdn.sr.se/images/2399/ba5436f2-ba5c-4723-b738-220396a27ff7.jpg?preset=api-itunes-presentation-image</url>
    </image>
    <itunes:image href="https://static-cdn.sr.se/images/2399/ba5436f2-ba5c-4723-b738-220396a27ff7.jpg?preset=api-itunes-presentation-image"/>
    <itunes:explicit>no</itunes:explicit>
    <itunes:summary>Norrländsk humor när den är som bäst. Ansvarig utgivare: Mark Malmström Fast</itunes:summary>
    <itunes:author>Sveriges Radio</itunes:author>
    <itunes:category text="Comedy"/>
    <itunes:owner>
      <itunes:name>Mammas Nya Kille</itunes:name>
      <itunes:email>podd@sverigesradio.se</itunes:email>
    </itunes:owner>
    <title>Mammas Nya Kille</title>
    <link>https://www.sverigesradio.se/mammasnyakille</link>
    <description>Norrländsk humor när den är som bäst. Ansvarig utgivare: Mark Malmström Fast</description>
    <language>sv</language>
    <copyright>Copyright Sveriges Radio 2025. All rights reserved.</copyright>
    <media:restriction type="country" relationship="allow">be bg cy dk ee fi fr gr ie it hr lv lt lu mt nl pl pt ro sk si es se cz de hu at is li no</media:restriction>"""

todate = date.today().isoformat()
fromdate = (date.today() - timedelta(days=360)).isoformat()

url = f"http://api.sr.se/api/v2/episodes/index?programid=2399&fromdate=2003-01-01&todate={todate}&audioquality=hi&format=json&size=300"
try:
  r = requests.get(url)
except Exception as e:
  print(f"Exception {e}")
if r.status_code == 200:
    episodes = r.json()["episodes"]
    for episode in episodes:
        title = episode["title"].replace("&","och")
        id = episode["id"]
        description = episode["description"].replace("&","och")
        url = episode["url"]
        imageurl = episode["imageurltemplate"]
        if "listenpodfile" in episode:
            audiourl = episode["listenpodfile"]["url"]
            audioduration = episode["listenpodfile"]["filesizeinbytes"]
        elif "downloadpodfile" in episode:
            audiourl = episode["downloadpodfile"]["url"]
            audioduration = episode["downloadpodfile"]["filesizeinbytes"]
        elif "broadcast" in episode:
            if "broadcastfiles" in episode["broadcast"]:
                audiourl = episode["broadcast"]["broadcastfiles"][0]["url"]
                audioduration = episode["broadcast"]["broadcastfiles"][0]["duration"]
        audiotype = episode["audiopriority"]
        pubdate = datetime.utcfromtimestamp(
            int(re.sub("[^0-9]", "", episode["publishdateutc"])[:-3])
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")
        if "mp3" in audiotype:
            audiotype = "audio/mpeg"
        else:
            audiotype = f"audio/{audiotype}"
        rss += f"""
        <item>
        <title>{title}</title>
        <description>{description}</description>
        <link>{url}</link>
        <guid isPermaLink="false">rss:sr.se/pod/eid/{id}</guid>
        <pubDate>{pubdate}</pubDate>
        <itunes:image href="{imageurl}?preset=api-itunes-presentation-image"/>
        <enclosure url="{audiourl}" length="{audioduration}" type="{audiotype}" />
        </item>"""
    rss += "\n</channel>\n</rss>"
    print(rss, file=open("mnk.rss", "w"))
else:
  print(f"Status code is {r.status_code}. Response: {r}")
