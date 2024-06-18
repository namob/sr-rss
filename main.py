import requests
from datetime import date, timedelta, datetime
import re

lastBuildDate = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:sr="http://www.sverigesradio.se/podrss" xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
  <channel>
    <itunes:new-feed-url>https://api.sr.se/api/rss/pod/3966</itunes:new-feed-url>
    <atom:link href="https://api.sr.se/api/rss/pod/3966" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{lastBuildDate}</lastBuildDate>
    <image>
      <title>P3 Dokumentär</title>
      <link>https://sverigesradio.se/p3dokumentar</link>
      <url>https://static-cdn.sr.se/images/2519/2639c08c-5d25-4e44-90a0-864c20e65f3b.jpg?preset=api-itunes-presentation-image</url>
    </image>
    <itunes:image href="https://static-cdn.sr.se/images/2519/2639c08c-5d25-4e44-90a0-864c20e65f3b.jpg?preset=api-itunes-presentation-image"/>
    <itunes:explicit>no</itunes:explicit>
    <itunes:summary><![CDATA[Sveriges största podd om vår tids mest spännande och viktiga händelser. Nya avsnitt från P3 Dokumentär hittar du först i Sveriges Radio Play. Ansvarig utgivare: Caroline Lagergren]]></itunes:summary>
    <itunes:author>Sveriges Radio</itunes:author>
    <itunes:category text="Society &amp; Culture"/>
    <itunes:owner>
      <itunes:name>P3 Dokumentär</itunes:name>
      <itunes:email>podd@sverigesradio.se</itunes:email>
    </itunes:owner>
    <title>P3 Dokumentär</title>
    <link>https://sverigesradio.se/p3dokumentar</link>
    <description><![CDATA[Sveriges största podd om vår tids mest spännande och viktiga händelser. <a href="https://sverigesradio.se/play/program/2519?utm_source=thirdparty&utm_medium=rss&utm_campaign=program_p3dokumentar">Nya avsnitt från P3 Dokumentär hittar du först i Sveriges Radio Play.</a>
Ansvarig utgivare: Caroline Lagergren]]></description>
    <language>sv</language>
    <copyright>Copyright Sveriges Radio 2023. All rights reserved.</copyright>
    <media:restriction type="country" relationship="allow">be bg cy dk ee fi fr gr ie it hr lv lt lu mt nl pl pt ro sk si es se cz de hu at is li no</media:restriction>"""

todate = date.today().isoformat()
fromdate = (date.today() - timedelta(days=360)).isoformat()
url = f"http://api.sr.se/api/v2/episodes/index?programid=2519&fromdate={fromdate}&todate={todate}&audioquality=hi&format=json&size=100"

r = requests.get(url)
if r.status_code == 200:
    episodes = r.json()["episodes"]
    for episode in episodes:
        title = episode["title"]
        if "Ny" in title and not "TIPS" in title and "broadcast" in episode:
            id = episode["id"]
            description = episode["description"]
            url = episode["url"]
            imageurl = episode["imageurltemplate"]
            audiourl = episode["listenpodfile"]["url"]
            audioduration = episode["listenpodfile"]["duration"]
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
    print(rss, file=open("p3dokumentar.rss", "w"))
