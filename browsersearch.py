import webbrowser
import urllib.parse

def search_web(query):
    query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def search_youtube(query):
    query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

def search_wikipedia(query):
    query = urllib.parse.quote(query)
    url = f"https://en.wikipedia.org/wiki/{query}"
    webbrowser.open(url)
def search_microsoft(query):
    query = urllib.parse.quote(query)
    url = f"https://www.bing.com/search?q={query}"
    webbrowser.open(url)