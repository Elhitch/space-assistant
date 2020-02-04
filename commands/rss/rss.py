import feedparser
import urlopen


def initialize(sentence):
    feed = feedparser.parse(
        'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en')

    headlines = []
    for i in range(5):
        headlines.append(feed['items'][i]['title'].split('-')[0])

    result = f'''
        1. {headlines[0]}.
        2. {headlines[1]}.
        3. {headlines[2]}.
        4. {headlines[3]}.
        5. {headlines[4]}.
    '''
    return result
