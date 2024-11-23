import logging
import os

import requests

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')

class Users:
    def __init__(self):
        self.base_url = 'https://1acgpw2vfg.execute-api.us-east-1.amazonaws.com/api'
        self.api_key = 'nwrysmZnvl2ZV1pFajp7j8vmxYK3naFsavKb2Nsy'

    def get_user_by_sub_or_none(self, user_sub):
        headers = {
            'x-api-key': self.api_key
        }
        try:
            response = requests.get(f"{self.base_url}/user/{user_sub}", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            LOGGER.error("get user error", e)
            return None


class MicroservicesFacade:
    def __init__(self):
        self.users_service = Users()

    def get_user(self, user_sub):
        return self.users_service.get_user_by_sub_or_none(user_sub)
