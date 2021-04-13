
import requests
from bs4 import BeautifulSoup

class RequestHandler:
    """
    docstring for RequestHandler.
    """

    def __init__(self):
        self.parser = "html.parser"

    def get_soup(self, url):
        try:
            response = requests.get(url)
        except Exception as err:
            print(f"Error: {err}")
            # raise err
            print(f"WITH FOLLOWING URL: {url=}")
            raise err
            return False
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, self.parser)
            # print(f"OK! Url: {url}")
            return soup
        else:
            print(f'Something went wrong. Got the following response code: {response.status_code}')
            return None
