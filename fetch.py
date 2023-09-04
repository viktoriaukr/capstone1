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
