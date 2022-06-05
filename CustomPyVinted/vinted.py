from urllib.parse import urlparse, parse_qsl
import requests
from CustomPyVinted.items.item import Item
from CustomPyVinted.items.items import Items
from CustomPyVinted.requester import requester


class Vinted:
    """
    This class is built to connect with the pyVinted API.

    It's main goal is to be able to retrieve items from a given url search.\n
    The items are then be returned in a json format
    """

    def __init__(self, domain="fr", proxy=None, gateway=None):
        """
        Args:
            domain (str): Domain to be used, example: "fr" for France, "de" for Germany...

        """
        requester.setCookies(domain)


        if proxy is not None:
            requester.session.proxies.update(proxy)

        if gateway is not None:
            requester.session.mount(f"https://www.vinted.{domain}", gateway)


        self.items = Items()

    # def login(self,username,password):
    #     requester.login(username=username, password=password)
    #     requester.message()
