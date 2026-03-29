import rich
import yaml
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
import re
import copy

TEAM1 = set("qwert")
TEAM2 = set("asdfg")

SHOT_ACTIONS = {"1", "2", "3"}
NON_START_ACTIONS = {"4", "5", "6", "9"}

TOKEN_RE = re.compile(r"^([1-9])([=-]?)([qwertasdfg])$")

TEAM_1_P_KEYS = ["q", "w", "e", "r", "t"]
TEAM_2_P_KEYS = ["a", "s", "d", "f", "g"]

WIDTH = 50

IDENT_REG = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


IDENT_SUB = ";"

IDENT_CQ = "]"

IDENT_END = "."

IDENT_BACK = "`"

LOAD_STACK = []

def compute_percent(made, att):
    if att == 0:
        return "0.0%"
    return f"{(made / att) * 100:.1f}%"


def compute_ts(player):
    pts = player["pts"]
    fga = player["2pa"] + player["3pa"]
    fta = player["fta"]

    denom = 2 * (fga + 0.44 * fta)
    if denom == 0:
        return "0.0%"
    return f"{(pts / denom) * 100:.1f}%"


def build_team_table(team_name, roster):
    table = Table(title=team_name, expand=True)

    table.add_column("PLAYER", justify="left")
    table.add_column("PTS", justify="right")
    table.add_column("AST", justify="right")
    table.add_column("REB", justify="right")
    table.add_column("BLK", justify="right")
    table.add_column("TNO", justify="right")
    table.add_column("STL", justify="right")
    table.add_column("TS%", justify="right")
    table.add_column("FT%", justify="right")

    for num, player in roster.items():
        name = f"{num} {player['name']}"

        ts = compute_ts(player)
        ft = compute_percent(player["ftm"], player["fta"])

        table.add_row(
            name,
            str(player["pts"]),
            str(player["ast"]),
            str(player["reb"]),
            str(player["blk"]),
            str(player["tno"]),
            str(player["stl"]),
            ts,
            ft
        )

    return table


def print_stats(gamedata):
    console = Console()

    t1 = build_team_table(gamedata["team1"], gamedata["roster1"])
    t2 = build_team_table(gamedata["team2"], gamedata["roster2"])

    console.print(t1)
    console.print()  # spacing
    console.print(t2)

def load_roster(filepath):
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    def initialize_roster(roster):
        new_roster = {}
        for num, player in roster.items():
            new_roster[str(num)] = {
                "name": player["name"],
                "pts": 0,
                "reb": 0,
                "ast": 0,
                "blk": 0,
                "tno": 0,
                "fou": 0,
                "stl": 0,
                "2pa": 0,
                "2pm": 0,
                "3pa": 0,
                "3pm": 0,
                "fta": 0,
                "ftm": 0
            }
        return new_roster

    gamedata = {
        "qtr": 1,
        "team1": data["game"]["team1"],
        "team2": data["game"]["team2"],
        "team1_abb": data["game"]["team1_abb"],
        "team2_abb": data["game"]["team2_abb"],
        "pts1": 0,
        "pts2": 0,
        "roster1": initialize_roster(data["roster1"]),
        "roster2": initialize_roster(data["roster2"]),
        "cl1": {k: str(v) for k, v in data["cl1"].items()},
        "cl2": {k: str(v) for k, v in data["cl2"].items()},
        "last_event":"None"
    }

    return gamedata

def make_layout(gamedata):
    layout = Layout()
    layout.split_column(
        Layout(name="scorebug", size=3),
        Layout(name="stats", size=15),
        Layout(name="bottom"),
    )
    layout["stats"].split_row(
        Layout(name="team1", ratio=1),
        Layout(name="team2", ratio=1),
    )
    layout["team1"].split_column(
        Layout(name="q", size=3),
        Layout(name="w", size=3),
        Layout(name="e", size=3),
        Layout(name="r", size=3),
        Layout(name="t", size=3),
    )
    layout["team2"].split_column(
        Layout(name="a", size=3),
        Layout(name="s", size=3),
        Layout(name="d", size=3),
        Layout(name="f", size=3),
        Layout(name="g", size=3),
    )
    layout["bottom"].split_column(
        Layout(name="broadcast", size=3),
        Layout(name="help", size=27)
    )
    layout["help"].split_row(
        Layout(name="help_l", ratio=1),
        Layout(name="help_r", ratio=1),
    )

    layout["scorebug"].update(
        Panel(f"{gamedata['team1_abb']} {gamedata['pts1']} - {gamedata['pts2']} {gamedata['team2_abb']}")
    )

    for hkey in (TEAM_1_P_KEYS):
        nbr = gamedata['cl1'][hkey]
        left = f"{hkey} : {nbr} {gamedata['roster1'][nbr]['name']}"
        right = f"{gamedata['roster1'][nbr]['pts']}/{gamedata['roster1'][nbr]['ast']}/{gamedata['roster1'][nbr]['reb']}"
        layout[hkey].update(
            Panel(f"{left:<{WIDTH - len(right)}}{right}")
        )
    for hkey in (TEAM_2_P_KEYS):
        nbr = gamedata['cl2'][hkey]
        left = f"{hkey} : {nbr} {gamedata['roster2'][nbr]['name']}"
        right = f"{gamedata['roster2'][nbr]['pts']}/{gamedata['roster2'][nbr]['ast']}/{gamedata['roster2'][nbr]['reb']}"
        layout[hkey].update(
            Panel(f"{left:<{WIDTH - len(right)}}{right}")
        )

    layout["broadcast"].update(
        Panel(f"{gamedata['last_event']}")
    )
    layout["help_l"].update(
        Panel("""1 : Free Throw
2 : 2p
3 : 3p
4 : rebound
5 : assist
6 : block
7 : foul
8 : turnover
9 : steal
"""))
    layout["help_r"].update(
            Panel("""; : substitute
] : change qtr
. : end game
` : undo command                                    
    """)
    )
    return layout


def get_team(player):
    if player in TEAM1:
        return 1
    elif player in TEAM2:
        return 2
    return None


def parse_token(token):
    m = TOKEN_RE.match(token)
    if not m:
        return None
    action, result, player = m.groups()
    return {
        "action": action,
        "result": result if result else None,
        "player": player,
        "team": get_team(player)
    }


def validate_play(cmd):
    parts = cmd.split(",")

    parsed = []

    for i, part in enumerate(parts):
        token = parse_token(part.strip())
        if not token:
            return None

        action = token["action"]
        result = token["result"]


        if i == 0:
            if action in NON_START_ACTIONS:
                return None
        else:
            if action not in NON_START_ACTIONS and action != "8":
                return None

        if result and action not in SHOT_ACTIONS:
            return None

        if action in SHOT_ACTIONS and not result:
            return None

        parsed.append(token)

    first = parsed[0]
    first_team = first["team"]

    for token in parsed[1:]:
        action = token["action"]
        team = token["team"]

        if action == "4":
            if first["result"] != "-":
                return None

        elif action == "5":
            if first["result"] != "=":
                return None
            if team != first_team:
                return None 

        # block
        elif action == "6":
            if first["result"] != "-":
                return None
            if team == first_team:
                return None 

        elif action == "9":
            if first["action"] != "8":
                return None
            if team == first_team:
                return None 

    return parts

def parse_sub(cmd):
    m = re.match(r"^;([qwertasdfg]),(\d+)$", cmd)
    if not m:
        return None
    return [m.group(1), m.group(2)]

def parse_string(str, gamedata):
    
    if len(str) == 0:
        return False
    if str[0] in IDENT_REG:
        seq = validate_play(str)
        if seq == None:
            return False
        else:
            for p in seq:
                if p[0] == "1":
                    if p[1] == "=":
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["fta"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["ftm"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["pts"] += 1
                        gamedata[f"pts{get_team(p[2])}"] += 1
                    else:
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["fta"] += 1
                elif p[0] == "2":
                    if p[1] == "=":
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["2pa"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["2pm"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["pts"] += 2
                        gamedata[f"pts{get_team(p[2])}"] += 2
                    else:
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["2pa"] += 1
                elif p[0] == "3":
                    if p[1] == "=":
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["3pa"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["3pm"] += 1
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["pts"] += 3
                        gamedata[f"pts{get_team(p[2])}"] += 3
                    else:
                        gamedata[f"roster{get_team(p[2])}"][gamedata[f"cl{get_team(p[2])}"][p[2]]]["3pa"] += 1
                elif p[0] == "4":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["reb"] += 1
                elif p[0] == "5":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["ast"] += 1
                elif p[0] == "6":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["blk"] += 1
                elif p[0] == "7":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["fou"] += 1
                elif p[0] == "8":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["tno"] += 1
                elif p[0] == "9":
                    gamedata[f"roster{get_team(p[1])}"][gamedata[f"cl{get_team(p[1])}"][p[1]]]["stl"] += 1
    elif str[0] == IDENT_SUB:
        seq = parse_sub(str)
        if seq == None:
            return False
        else:
            off_sub = seq[0]
            on_sub = seq[1]
            team = get_team(off_sub)
            if team == 1:
                if on_sub in gamedata["roster1"]:
                    gamedata["cl1"][off_sub] = on_sub
                else:
                    return False
            if team == 2:
                if on_sub in gamedata["roster2"]:
                    gamedata["cl2"][off_sub] = on_sub
                else:
                    return False
    elif str[0] == IDENT_CQ:
        gamedata["qtr"] += 1
    elif str[0] == IDENT_END:
        
        return "END"
    elif str[0] == IDENT_BACK:
        if len(LOAD_STACK) <= 1:
            return False
        else:
            LOAD_STACK.pop() 
            prev = LOAD_STACK.pop() 
            gamedata.clear()
            gamedata.update(prev)
    else:
        return False
    return True

def main():
    console = Console()
    gamedata = load_roster("example.yaml")
    LOAD_STACK.append(copy.deepcopy(gamedata))
    with Live(make_layout(gamedata), auto_refresh=False, screen=False) as live:
        while True:
            cmd = console.input(">> ")
            flag = parse_string(cmd, gamedata)
            if flag == True:
                LOAD_STACK.append(copy.deepcopy(gamedata))
                gamedata["last_event"] = f"SUCCESSFUL REQUEST {cmd}"
            elif flag == False:
                gamedata["last_event"] = f"FAILED REQUEST {cmd}"
            else:
                live.stop()
                console.clear()
                print_stats(gamedata)
                break
            live.update(make_layout(gamedata), refresh=True)

if __name__ == "__main__":
    main()
