import requests
import time
import json
import sys
import os
import os.path
from itertools import count
from tqdm import tqdm

def store_a_game(game_id,target_folder):
    try:
        r = requests.get("https://online-go.com/api/v1/games/{}/sgf".format(game_id))
    except requests.exceptions.RequestException as e:
        print("game request failed",e)
        return "error"
    if "detail" in r.text:
        return "throttled"
    with open(os.path.join(target_folder,f"{game_id}.sgf"),"w") as f:
        f.write(r.text)
    return "success"

def get_all_game_ids_and_opponents(player_id,wait=0.1):
    url = "https://online-go.com/api/v1/players/{}/games/?format=json".format(player_id)
    pids = set()
    gids = set()
    for _ in tqdm(count()):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("player request failed",e)
            break
        try:
            data = r.json()
        except Exception as e:
            print("failed to convert to JSON",e)
            try:
                print(r.text)
            except Exception as e:
                print(e)
            break
        if "detail" in data and data["detail"]=="Request was throttled.":
            wait*=1.5
            print("player request got throttled, increased wait time to {} and retrying in 10 seconds".format(wait))
            time.sleep(10)
            continue
        try:
            url = data["next"]
            results = data["results"]
            for res in results:
                if res["width"]!=9 or res["height"]!=9:
                    continue
                gids.add(res["id"])
                if res["players"]["white"]["id"] == player_id:
                    pids.add((res["players"]["black"]["id"],res["players"]["black"]["ratings"]["overall"]["rating"]))
                else:
                    pids.add((res["players"]["white"]["id"],res["players"]["white"]["ratings"]["overall"]["rating"]))
        except Exception as e:
            print("Data was corrupted",data,e)
            break
        if url is None:
            break
        time.sleep(wait)
    return gids,pids,wait

def get_alot_of_games(start_id=60399,game_folder="games",wait=0.1):
    os.makedirs(game_folder,exist_ok=True)
    already_gids = set()
    all_pids = set()
    already_pids = {start_id}
    already_pids.update(map(int,os.listdir(game_folder)))
    print(already_pids)
    curr_id = start_id
    while True:
        print(f"storing games from {curr_id}")
        gids,pids,wait = get_all_game_ids_and_opponents(curr_id,wait=wait)
        gids-=already_gids
        pid_folder = os.path.join(game_folder,str(curr_id))
        os.makedirs(pid_folder,exist_ok=True)
        for gid in tqdm(gids):
            result = "throttled"
            while result == "throttled":
                result = store_a_game(gid,pid_folder)
                if result == "throttled":
                    wait*=1.5
                    print("player request got throttled, increased wait time to {} and retrying in 10 seconds".format(wait))
                    time.sleep(10)
            time.sleep(wait)
        already_gids.update(gids)
        all_pids.update(pids)
        if len(all_pids)==0:
            break
        all_pids = set(filter(lambda x:x[0] not in already_pids, all_pids))
        curr_id = sorted(all_pids,key=lambda x:x[1])[-1][0]
        already_pids.add(curr_id)
if __name__ == "__main__":
    print(get_alot_of_games())