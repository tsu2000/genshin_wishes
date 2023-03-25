def char_event_5star(x: int):
    if x < 74:
        return 0.006
    elif x >= 74 and x < 90:
        return round((x - 73) * 0.06 + 0.006, 3)
    else:
        return 1

char_roll_5star = {num: char_event_5star(num) for num in range(1, 91)}

def char_event_4star(x: int):
    if x < 9:
        return 0.051
    elif x == 9:
        return 0.561
    else:
        return 1

char_roll_4star = {num: char_event_4star(num) for num in range(1, 11)}

def weap_event_5star(x: int):
    if x < 63:
        return 0.007
    elif x >= 63 and x < 77:
        return round((x - 62) * 0.07 + 0.007, 3)
    else:
        return 1

weap_roll_5star = {num: weap_event_5star(num) for num in range(1, 78)}

def weap_event_4star(x: int):
    if x < 8:
        return 0.06
    elif x == 8:
        return 0.66
    else:
        return 1

weap_roll_4star = {num: weap_event_4star(num) for num in range(1, 10)}