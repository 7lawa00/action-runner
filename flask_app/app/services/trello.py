import os
import requests
from typing import Any, Dict, List

class TrelloClient:
    def __init__(self):
        self.key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.base = 'https://api.trello.com/1'

    def has_keys(self) -> bool:
        return bool(self.key and self.token)

    def get_boards(self) -> List[Dict[str, Any]]:
        if not self.has_keys():
            # Fallback to JSONPlaceholder
            resp = requests.get('https://jsonplaceholder.typicode.com/users', timeout=10)
            boards = resp.json()
            return [{
                'id': b['id'],
                'name': b['name'],
                'fallback': True
            } for b in boards]
        params = {'key': self.key, 'token': self.token}
        resp = requests.get(f'{self.base}/members/me/boards', params=params, timeout=15)
        return resp.json()
