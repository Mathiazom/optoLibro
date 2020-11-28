import requests
import re
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

'''
    Bear page acting as source for book URLs
'''
BOOK_URL_SOURCE = "https://foxtrot.bearblog.dev/bearbookslist/"

'''
    Adlibris website prefix
'''
BOOK_DATA_SOURCE_PREFIX = "https://www.adlibris.com/no/bok/"


'''
    Retrieve list of book urls from the defined Bear page
'''
def get_book_urls():

    print(f"Retrieving URLs from {BOOK_URL_SOURCE}")

    page = BeautifulSoup(requests.get(BOOK_URL_SOURCE).text, 'html.parser')

    list = page.find("div",{'id':'books'})

    suffixes = list.findAll("p")

    print(colored(f"Found {len(suffixes)} URLs","green"))

    return [BOOK_DATA_SOURCE_PREFIX + s.string.strip() for s in suffixes]


'''
    Extract the author of the book presented on the given page
    Author field is less accessable than the title and description,
    but can be retrieved from an inline Javascript variable
'''
def get_book_author_from_page(page):

    scripts = page.findAll("script")

    author = ""
    for s in scripts:

        if not s.contents:
            continue

        content = s.contents[0]

        authorMatch = re.search('"Authors":\[".*"\]',content)

        if not authorMatch:
            continue

        author_string = authorMatch.group()

        author = re.search('\[".*"\]',author_string).group()[2:-2]

    return author

'''
    Extract data about the book from the page on the given url
    returns book as tuple
'''
def get_book_from_url(url):

    page = BeautifulSoup(requests.get(url).text, 'html.parser')

    title = page.find('meta',{'property':'og:title'}).attrs['content']
    author = get_book_author_from_page(page)
    img_url = page.find('meta',{'property':'og:image:secure_url'}).attrs['content']
    url = page.find('meta',{'property':'og:url'}).attrs['content']
    description = page.find('meta',{'property':'og:description'}).attrs['content']

    print(title)

    return (title,author,url,img_url,description)

'''
    - Retrieve book URLs from defined Bear page
    - Extract book data from URLs
'''
def fetch_books():

    # Terminal colors
    init()

    # Retrieve book urls
    urls = get_book_urls()

    # Get adlibris data from URLs
    return [get_book_from_url(url) for url in urls]
