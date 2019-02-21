# -*- coding: utf-8 -*-

import json
import requests


class Slack():
    def __init__(self, url="",**kwargs):
        self.url = url
        self.setting = kwargs

    def send(self, **kwargs):
        kwargs.update(self.setting)
        payload_json = json.dumps(kwargs)
        requests.post(self.url, data=payload_json)