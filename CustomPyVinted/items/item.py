from datetime import datetime, timezone
from CustomPyVinted.requester import requester


class Item:
    def __init__(self, data):
        self.id = data["id"]
        self.title = data["title"]
        self.brand_title = data["brand_title"]
        self.size_title = data["size_title"]
        self.currency = data["currency"]
        self.price = data["price"]
        self.photo = data["photo"]["url"]
        self.url = data["url"]
        self.created_at_ts = datetime.fromtimestamp(
            data["photo"]["high_resolution"]["timestamp"], tz=timezone.utc
        )

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def isNewItem(self, minutes=3):
        delta = datetime.now(timezone.utc) - self.created_at_ts
        print(delta)
        return delta.seconds < minutes * 60

