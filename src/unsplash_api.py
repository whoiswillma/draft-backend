import requests
import os
import json


def unsplash_search(query):
    try:
        response = requests.get(
            'https://api.unsplash.com/photos/random',
            headers={
                'Accept-Version': 'v1', 
                'Authorization': 'Client-ID ' + os.getenv('UNSPLASH_ACCESS_KEY')
            },
            params={
                'query': query,
                'per_page': 1
            }
        )
        return json.dumps(response.json())

    except Exception as e:
        return None
