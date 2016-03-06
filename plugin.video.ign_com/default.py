#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import xbmcplugin
import xbmcgui
import sys
import xbmcaddon
import base64
import socket


socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.video.ign_com')
translation = addon.getLocalizedString

live_stream = addon.getSetting("LiveStream")
live_stream_setting = False
if live_stream == "true":
    live_stream_setting = True

ign1 = addon.getSetting("IGN1")
ign1_setting = False
if ign1 == "true":
    ign1_setting = True

max_video_quality = addon.getSetting("maxVideoQualityRes")
force_view_mode = addon.getSetting("force_view_mode")
if force_view_mode == "true":
    force__view__mode = True
else:
    force_view_mode = False
viewMode = str(addon.getSetting("viewMode"))

max_video_height = [360, 540, 720, 1080][int(max_video_quality)]
max_video_bitrate = [500000, 1500000, 2500000, 5000000][int(max_video_quality)]
max_video_quality = [640, 960, 1280, 1920][int(max_video_quality)]


def index():
    if live_stream_setting:
        content = get_url("http://www.ign.com")
        match = re.compile('"m3uUrl":"(.+?).m3u8"}', re.DOTALL).findall(content)
        if len(match) > 0:
            video_url = match[0].replace("\\", "")
            title = re.compile('data-video-title="(.+?)"', re.DOTALL).findall(content)
            add_link("***IGN-LIVESTREAM: " + title[0] + "***", video_url + ".m3u8", 'play_live_stream', "", "", "LIVE")
    add_dir(translation(30002), "http://www.ign.com/videos/all/filtergalleryajax?filter=all", 'list_videos', "")
    add_dir("IGN Daily Fix", "http://www.ign.com/watch/daily-fix?category=videos&page=1", 'list_series_episodes', "")
    # addDir("IGN Live","http://www.ign.com/videos/series/ign-live",'list_videos',"")
    # addDir("IGN First","http://www.ign.com/videos/series/playstation-app-ign-first",'list_videos',"")
    add_dir(translation(30003), "http://www.ign.com/videos/all/filtergalleryajax?filter=games-review", 'list_videos', "")
    add_dir(translation(30004), "http://www.ign.com/videos/all/filtergalleryajax?filter=games-trailer", 'list_videos', "")
    add_dir(translation(30005), "http://www.ign.com/videos/all/filtergalleryajax?filter=movies-trailer", 'list_videos', "")
    add_dir("Podcasts", "", 'podcast_index', "")
    # addDir(translation(30007),"http://www.ign.com/videos/allseriesajax",'list_series',"")
    if ign1_setting:
        add_link("IGN1", "http://videochannel.ign.com/stitcher/now.m3u8", 'play_live_stream', "", "IGN1 - IGN's 24 hour streaming channel: Broadcasting the latest IGN original shows, live programming, gameplay footage, video reviews, previews and more", "LIVE")
    add_dir(translation(30008), "", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def podcast_index():
    add_dir("Up At Noon", "http://www.ign.com/watch/up-at-noon?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Game Scoop!", "http://www.ign.com/watch/game-scoop?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Beyond!", "http://www.ign.com/watch/beyond?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Unlocked", "http://www.ign.com/watch/unlocked?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Nintendo Voice Chat", "http://www.ign.com/watch/nintendo-voice-chat?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Esports Weekly", "http://www.ign.com/watch/esports-weekly?category=videos&page=1", 'list_series_episodes', "")
    add_dir("Fireteam Chat", "http://www.ign.com/watch/fireteam-chat?category=videos&page=1", 'list_series_episodes', "")
    add_dir("IGN Anime Club", "http://www.ign.com/watch/ign-anime-club?category=videos&page=1", 'list_series_episodes', "")
    add_dir("IGN Unfiltered", "http://www.ign.com/watch/ign-unfiltered?category=videos&page=1", 'list_series_episodes', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def list_videos(url):
    content = get_url(url)
    spl = content.split('<div class="grid_16 alpha bottom_2">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<li>(.+?)</li>', re.DOTALL).findall(entry)
        if len(match) > 0:
            length = match[0].replace(" mins","")
            l = length.split(':')
            length = int(l[0])*60 + int(l[1])
            match = re.compile('<p class="video-description">\n                    <span class="publish-date">(.+?)</span> -(.+?)</p>', re.DOTALL).findall(entry)
            date = match[0][0]
            desc = match[0][1]
            desc = clean_title(desc)
            match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            title = match[0]
            title = clean_title(title)
            match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url = match[0]
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb = ""
            if match:
                thumb = match[0].replace("_small.jpg", ".jpg")
            add_link(title, url, 'play_video', thumb, date + "\n" + desc, length)
    match_page = re.compile('<a id="moreVideos" href="(.+?)"', re.DOTALL).findall(content)
    page_count = re.compile('<a id="moreVideos" href=".+?page=(.+?).+?"', re.DOTALL).findall(content)
    if len(match_page) > 0:
        url_next = "http://www.ign.com"+match_page[0]
        add_dir(translation(30001) + " (" + str(page_count[0]) + ")", url_next, 'list_videos', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def list_series_episodes(url):
    content = get_url(url)
    match = re.compile('<a.+?class="video-link".+?href="(.+?)".+?data-title="(.+?)".+?>.+?<img src="(.+?)" />.+?<div class="video-title">(.+?)</div>.+?<div class="video-duration">(.+?)</div>.+?<div class="ago">(.+?)</div>', re.DOTALL).findall(content)
    for i in range(0,len(match),1):
        vidurl = "http://www.ign.com/"+match[i][0]
        description = match[i][1]
        thumb = match[i][2]
        title = match[i][3]
        dur_split = match[i][4].split(':')
        duration = int(dur_split[0])*60+int(dur_split[1])
        date = match[i][5]
        add_link(title, vidurl, 'play_video', thumb, date + "\n" + description, duration)
    match_page = re.compile('<a class="next" href="://(.+?)">Next&nbsp;&raquo;</a>', re.DOTALL).findall(content)
    page_count = re.compile('<a class="next" href="://.+?page=(.+?)">Next&nbsp;&raquo;</a>', re.DOTALL).findall(content)
    if len(page_count) > 0:
        add_dir(translation(30001) + " (" + str(page_count[0]) + ")", "http://www.ign.com" + match_page[0] + "&category=videos", 'list_series_episodes', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def list_series(url):
    content = get_url(url)
    spl = content.split('<div class="grid_16 alpha bottom_2">')
    for i in range(1,len(spl),1):
        entry = spl[i]
        match = re.compile('<li>(.+?)</li>', re.DOTALL).findall(entry)
        date = match[0]
        match = re.compile('<p class="video-description">(.+?)</p>', re.DOTALL).findall(entry)
        title = match[0]
        title = clean_title(title)
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = match[0]
        thumb = ""
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        if len(match)>0:
            thumb = match[0].replace("_small.jpg", ".jpg")
        add_dir(title, url, 'list_videos', thumb, date)
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def search():
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ","+")
        list_search_results('http://www.ign.com/search?q=' + search_string + '&page=0&count=10&type=video')


def list_search_results(url):
    url_main = url
    content = get_url(url)
    spl = content.split('<div class="search-item"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = ""
        if match:
            thumb = clean_url(match[0]).replace("_small.jpg", ".jpg")
        entry = entry[entry.find('<div class="search-item-title">'):]
        match = re.compile('<span class="duration">(.+?)<span>', re.DOTALL).findall(entry)
        length = ""
        if len(match) > 0:
            length = clean_title(match[0])
        match = re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
        url = match[0][0]
        title = match[0][1]
        title = clean_title(title)
        add_link(title, url, 'play_video', thumb, "", length)
    match = re.compile('data-page="(.+?)"', re.DOTALL).findall(content)
    page = int(match[0])
    match = re.compile('data-total="(.+?)"', re.DOTALL).findall(content)
    max_page = int(int(match[0])/10)
    url_next = url_main.replace("page="+str(page),"page="+str(page+1))
    if page < max_page:
        add_dir(translation(30001), url_next, 'list_search_results', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if force_view_mode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def play_video(url):
    content = get_url(url)
    match4 = re.compile("data-video='(.+?)'", re.DOTALL).findall(content)
    if match4 and 'div class="hero-poster instant-play"' not in content and 'div class="hero-unit-container"' not in content:
        list_of_urls = re.compile('"url":"(.+?)","height":(.+?),"', re.DOTALL).findall(match4[0])
        video_url = ""
        for x in range(0, len(list_of_urls)):
            if max_video_height >= int(list_of_urls[x][1]):
                video_url = list_of_urls[x][0]
        final_url = video_url.replace("\\", "")
    else:
        video_id = ""
        if 'div class="hero-unit-container"' in content:
            match1 = re.compile('<div class="hero-poster instant-play".+?data-slug=".+?".+? data-id="(.+?)".+?>', re.DOTALL).findall(content)
            video_id = match1[0]
        match2 = re.compile('data-id="(.+?)"', re.DOTALL).findall(content)
        match3 = re.compile('"video_id":"(.+?)"', re.DOTALL).findall(content)
        match4 = re.compile('data-video-id="(.+?)"', re.DOTALL).findall(content)
        if match1:
            video_id = match1[0]
        elif match2:
            video_id = match2[0]
        elif match3:
            video_id = match3[0]
        elif match4:
            video_id = match3[0]
        content = get_url("http://www.ign.com/videos/configs/id/" + video_id + ".config").replace("\\", "")
        match = re.compile('"url":"(.+?)/zencoder/(.+?)/(.+?)/(.+?)/(.+?)/(.+?)-(.+?)-(.+?)"', re.DOTALL).findall(content)
        start_url = match[0][0]
        date = match[0][1]+"/"+match[0][2]+"/"+match[0][3]
        resolution = int(match[0][4])
        vid_id = match[0][5]
        bitrate = match[0][6]
        ext = match[0][7]
        if max_video_quality < resolution:
            resolution = max_video_quality
            bitrate = max_video_bitrate
        final_url = start_url+"/zencoder/"+date+"/"+str(resolution)+"/"+vid_id+"-"+str(bitrate)+"-"+ext
    listitem = xbmcgui.ListItem(path=final_url)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def play_live_stream(url):
    listitem = xbmcgui.ListItem(path=url)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
          

def clean_title(title):
    title = title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
    title = title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
    title = title.replace("<em>","").replace("</em>","").strip()
    return title


def clean_url(title):
    title = title.replace("&#x3A;",":").replace("&#x2F;","/")
    return title


def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11')
    req.add_header('Cookie', 'i18n-ccpref=15-US-www-1')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def parameters_string_to_dict(parameters):
    """ Convert parameters encoded in a URL to a dict. """
    param_dict = {}
    if parameters:
        param_pairs = parameters[1:].split("&")
        for paramsPair in param_pairs:
            param_splits = paramsPair.split('=')
            if (len(param_splits)) == 2:
                param_dict[param_splits[0]] = param_splits[1]
    return param_dict


def add_link(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def add_dir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
         
params = parameters_string_to_dict(sys.argv[2])
mode = params.get('mode')
url = params.get('url')
if isinstance(url, str):
    url = urllib.unquote_plus(url)

if mode == 'list_videos':
    list_videos(url)
elif mode == 'list_series':
    list_series(url)
elif mode == 'list_search_results':
    list_search_results(url)
elif mode == 'play_video':
    play_video(url)
elif mode == 'list_series_episodes':
    list_series_episodes(url)
elif mode == 'podcast_index':
    podcast_index()
elif mode == 'play_live_stream':
    play_live_stream(url)
elif mode == 'search':
    search()
else:
    index()