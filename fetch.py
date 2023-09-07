import requests


def get_books(subject):
    url = f"https://openlibrary.org/{subject}.json"
    res = requests.get(url)
    data = res.json()
    return data


def get_authors_details(key):
    url = f"https://openlibrary.org/{key}.json"
    res = requests.get(url)
    data = res.json()
    return data


def get_ratings_details(key):
    url = f"https://openlibrary.org/{key}/ratings.json"
    res = requests.get(url)
    data = res.json()
    return data


def search(value):
    url = f"https://openlibray.org/search.json?q = {value}"
    res = requests.get(url)
    data = res.json()
    return data


def author_works(key):
    url = f"https://openlibrary.org/{key}/works.json"
    res = requests.get(url)
    data = res.json()
    return data
