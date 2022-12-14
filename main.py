import json
import os
from argparse import ArgumentParser, Namespace

from dotenv import load_dotenv
from omegaconf import OmegaConf
from tqdm.auto import tqdm

from api.twitter import TwitterAPI


def run_parser() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--config-path", "-c", required=True, type=str, metavar="DIR", help="Path to config file")

    args = parser.parse_args()
    assert os.path.exists(args.config_path)
    return args


def main(args: Namespace) -> None:
    load_dotenv()
    cfg = OmegaConf.load(args.config_path)
    twitter_api = TwitterAPI(os.environ.get("BEARER_TOKEN", ""))

    # read inp/out path
    users_path = cfg.get("users_path", None)
    export_path = cfg.get("export_path", "output.json")
    cache_path = cfg.get("cache_path", ".cache")
    os.makedirs(cache_path, exist_ok=True)

    # load criteria
    criteria = cfg.get("criteria", {})
    min_followers = criteria.get("min_followers", 50)
    must_follow = criteria.get("follows", [])
    must_likes = criteria.get("likes", [])
    must_rtw = criteria.get("retweets", [])

    must_follow = [
        _usr.split("/")[-1]
        for _usr in must_follow]  # get uname

    # get must liked tweets
    
    # use cache to reduce request
    like_cache_path = f"{cache_path}/like.json"
    if os.path.exists(like_cache_path):
        with open(like_cache_path, "r") as fp:
            loaded_must_likes = json.load(fp)
    else:
        loaded_must_likes = {}

    for _twt in must_likes:
        if _twt not in loaded_must_likes.keys():
            loaded_must_likes[_twt] =  twitter_api.get_tweet_likes(_twt.split("/")[-1]) 
        
    must_likes = loaded_must_likes
    with open(like_cache_path, "w") as fp:
        json.dump(must_likes, fp)

    # get must retweeted tweets
    rtw_cache_path = f"{cache_path}/rtw.json"
    if os.path.exists(rtw_cache_path):
        with open(rtw_cache_path, "r") as fp:
            loaded_must_rtw = json.load(fp)
    else:
        loaded_must_rtw = {}

    for _twt in must_rtw:
        if _twt not in loaded_must_rtw.keys():
            loaded_must_rtw[_twt] =  twitter_api.get_tweet_retweets(_twt.split("/")[-1]) 

    must_rtw = loaded_must_rtw
    with open(rtw_cache_path, "w") as fp:
        json.dump(must_rtw, fp)

    # read users
    if users_path is None:
        raise ValueError(f"Make sure to provide users_path in config file")
    
    with open(users_path, "r") as fp:
        users_list = [
            _line.strip().split("\t")[0] 
            for _line in fp.readlines()]

    users_info = twitter_api.get_user_infos(users_list)
        
    # iterate over users
    results = []
    for user in tqdm(users_info):
        qualify = True

        # check min followers
        followers = twitter_api.get_followers(user["id"])
        if len(followers) < min_followers:
            qualify = False
            results.append(
                {
                    "user": user, 
                    "status": f"Min followers not reach. Expect {min_followers}, got {len(followers)}"})
        
        # check followings
        followings = twitter_api.get_following(user["id"])
        not_follow = []
        for _must_follow in must_follow:
            if _must_follow not in [_follow["username"] for _follow in followings]:
                qualify = False
                not_follow.append(_must_follow)
        
        # not pass criteria
        if len(not_follow) > 0:
            qualify = False
            results.append(
                {
                    "user": user, 
                    "status": f"Haven't followed {not_follow}"})

        # check likes
        for must_like_twt, likers in must_likes.items():
            if user["id"] not in [_liker["id"] for _liker in likers]:
                qualify = False
                results.append(
                {
                    "user": user, 
                    "status": f"Haven't like {must_like_twt}"})

        # check retweets
        for must_like_twt, retweeters in must_rtw.items():
            if user["id"] not in [_rtw["id"] for _rtw in retweeters]:
                qualify = False
                results.append(
                {
                    "user": user, 
                    "status": f"Haven't like {must_like_twt}"})

        if qualify:
            results.append({"user": user, "status": "Qualified"})

    # save results
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    export_path = ".".join(export_path.split(".")[:-1]) # remove ext
    with open(export_path + ".json", "w") as fp:
        json.dump(results, fp)



if __name__ == "__main__":
    args = run_parser()
    main(args)
