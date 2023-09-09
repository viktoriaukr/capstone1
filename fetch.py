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


def search(q):
    url = f"https://openlibrary.org/search.json?q={q}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            # Access the list of documents
            docs = data.get("docs", [])
            return docs
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            return []
    else:
        # Handle the API error here and print response content
        print(f"API Error: {response.status_code}")
        print(response.text)
        return []




def author_works(key):
    url = f"https://openlibrary.org/{key}/works.json"
    res = requests.get(url)
    data = res.json()
    return data
