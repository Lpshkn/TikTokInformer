from datetime import datetime as dt


class Tiktok:
    def __init__(self, tiktok_dict: dict):
        self._id = tiktok_dict['id']
        self._desc = tiktok_dict['desc']
        self._time = dt.fromtimestamp(tiktok_dict['createTime'])
        self._user_id = tiktok_dict['author']['uniqueId']

    @property
    def id(self):
        return self._id

    @property
    def desc(self):
        return self._desc

    @property
    def time(self):
        return self._time

    @property
    def user_id(self):
        return self._user_id
