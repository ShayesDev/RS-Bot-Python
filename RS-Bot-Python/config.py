import os

DIR_PATH = os.path.dirname(__file__) + "//"
TOKEN = ""
SERVER_ID = ""
CHATSTREAM_ID = ""
BOTLOG_ID = ""
CMD_PREFIX = "!"
PLAYER_DATA_FILE = "playerdata.json"
RANK_ROLES = ("Seniors","Builders","Regulars","Learners","Visitors")
INACTIVE_INTERVAL = 43200    # interval to check for inactive players in seconds
INACTIVE_DAYS = 30      # how many days until a player is considered inactive

LOCALHOST = 'localhost'
SENDPORT = 50009
SERVER_ADDR = (LOCALHOST, SENDPORT)
