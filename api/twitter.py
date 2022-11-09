from typing import List

import requests


class TwitterAPI(object):

    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token

    def get_user_infos(self, usernames: List[str]):
        usernames = usernames if isinstance(usernames, str) else ",".join(usernames)
        url = f"https://api.twitter.com/2/users/by"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
        }

        params = {
            "user.fields": "created_at,description",
            "usernames": usernames
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        data = response.json()["data"]
        return data

    def get_tweet_likes(self, tweets_id: str):
        url = f"https://api.twitter.com/2/tweets/{tweets_id}/liking_users"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "v2LikingUsersPython"
        }

        params = {
            "user.fields": "created_at"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        resp = response.json()

        likers = []
        while "data" in resp.keys():
            likers += resp["data"]
            if "next_token" not in resp["meta"].keys():
                break
            params["pagination_token"] = resp["meta"]["next_token"]
            response = requests.get(url, headers=headers, params=params)
            resp = response.json()

        return likers

    def get_tweet_retweets(self, tweets_id: str):
        url = f"https://api.twitter.com/2/tweets/{tweets_id}/retweeted_by"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "v2LikingUsersPython"
        }

        params = {
            "user.fields": "created_at"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        resp = response.json()

        retweeters = []
        while "data" in resp.keys():
            retweeters += resp["data"]
            if "next_token" not in resp["meta"].keys():
                break
            params["pagination_token"] = resp["meta"]["next_token"]
            response = requests.get(url, headers=headers, params=params)
            resp = response.json()

        return retweeters

    def get_following(self, user_id: int):
        url = f"https://api.twitter.com/2/users/{user_id}/following"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "v2FollowingLookupPython"
        }

        params = {
            "user.fields": "created_at,username",
            "max_results": 1000
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        resp = response.json()
        
        followings = []
        while "data" in resp.keys():
            followings += resp["data"]
            if "next_token" not in resp["meta"].keys():
                break
            params["pagination_token"] = resp["meta"]["next_token"]
            response = requests.get(url, headers=headers, params=params)
            resp = response.json()

        return followings

    def get_followers(self, user_id: int):
        url = f"https://api.twitter.com/2/users/{user_id}/followers"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "v2FollowerLookupPython"
        }

        params = {
            "user.fields": "created_at,username",
            "max_results": 1000
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise ConnectionError(response.text)

        resp = response.json()

        followers = []
        while "data" in resp.keys():
            followers += resp["data"]
            if "next_token" not in resp["meta"].keys():
                break
            params["pagination_token"] = resp["meta"]["next_token"]
            response = requests.get(url, headers=headers, params=params)
            resp = response.json()

        return followers
