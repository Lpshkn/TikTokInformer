class User:
    def __init__(self, user_dict: dict):
        self._unique_id = user_dict['uniqueId']
        self._nickname = user_dict['userInfo']['user']['nickname']
        self._followers = user_dict['userInfo']['stats']['followerCount']
        self._following = user_dict['userInfo']['stats']['followingCount']
        self._heart_count = user_dict['userInfo']['stats']['heartCount']
        self._video_count = user_dict['userInfo']['stats']['videoCount']

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def nickname(self):
        return self._nickname

    @property
    def followers(self):
        return self._followers

    @property
    def following(self):
        return self._following

    @property
    def heart_count(self):
        return self._heart_count

    @property
    def video_count(self):
        return self._video_count
