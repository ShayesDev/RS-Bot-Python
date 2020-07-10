import json
import config as cfg

class Player:
    with open(cfg.PLAYER_DATA_FILE,"r") as f:
        data = json.load(f)
    
    def __init__(self,uuid=None,name=None,rank=None,token=None,
                 discord_id=None,last_join=None,_dict=None):
        self.uuid = uuid
        self.name = name
        self.rank = rank
        self.token = token
        self.discord_id = discord_id
        self.last_join = last_join
        
        if _dict:
            self.__dict__ = _dict

    def save(self):
        Player.data[self.uuid] = self.__dict__
        
        with open(cfg.PLAYER_DATA_FILE,"w") as f:
            json.dump(Player.data,f)

def get_players():
    return [Player(_dict=p) for p in Player.data.values()]

def get_player(uuid):
    if uuid in Player.data:
        return Player(_dict=Player.data[uuid])

def get_player_by_token(token):
    for pdata in Player.data.values():
        if token == pdata["token"]:
            return Player(_dict=pdata)

def get_player_by_id(discord_id):
    for pdata in Player.data.values():
        if discord_id == pdata["discord_id"]:
            return Player(_dict=pdata)

def get_player_by_name(name):
    for pdata in Player.data.values():
        if name == pdata["name"]:
            return Player(_dict=pdata)

if __name__ == "__main__":
    try:
        name = input("Player name: ")
        player = get_player_by_name(name)
        print(player.__dict__)
    except:
        print("That player could not be found!")

