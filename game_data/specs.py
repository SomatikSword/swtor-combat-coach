COMBAT_STYLES = {
    # ===================================================
    # Empire / Force
    # ===================================================

    "Marauder": {
        "Annihilation": {
            "role": "DPS",
            "mirror": ("Sentinel", "Watchman"),
        },
        "Carnage": {
            "role": "DPS",
            "mirror": ("Sentinel", "Combat"),
        },
        "Fury": {
            "role": "DPS",
            "mirror": ("Sentinel", "Concentration"),
        },
    },

    "Juggernaut": {
        "Immortal": {
            "role": "TANK",
            "mirror": ("Guardian", "Defense"),
        },
        "Vengeance": {
            "role": "DPS",
            "mirror": ("Guardian", "Vigilance"),
        },
        "Rage": {
            "role": "DPS",
            "mirror": ("Guardian", "Focus"),
        },
    },

    "Assassin": {
        "Darkness": {
            "role": "TANK",
            "mirror": ("Shadow", "Kinetic Combat"),
        },
        "Deception": {
            "role": "DPS",
            "mirror": ("Shadow", "Infiltration"),
        },
        "Hatred": {
            "role": "DPS",
            "mirror": ("Shadow", "Serenity"),
        },
    },

    "Sorcerer": {
        "Corruption": {
            "role": "HEAL",
            "mirror": ("Sage", "Seer"),
        },
        "Lightning": {
            "role": "DPS",
            "mirror": ("Sage", "Telekinetics"),
        },
        "Madness": {
            "role": "DPS",
            "mirror": ("Sage", "Balance"),
        },
    },

    # ===================================================
    # Empire / Tech
    # ===================================================

    "Operative": {
        "Medicine": {
            "role": "HEAL",
            "mirror": ("Scoundrel", "Sawbones"),
        },
        "Concealment": {
            "role": "DPS",
            "mirror": ("Scoundrel", "Scrapper"),
        },
        "Lethality": {
            "role": "DPS",
            "mirror": ("Scoundrel", "Ruffian"),
        },
    },

    "Sniper": {
        "Marksmanship": {
            "role": "DPS",
            "mirror": ("Gunslinger", "Sharpshooter"),
        },
        "Engineering": {
            "role": "DPS",
            "mirror": ("Gunslinger", "Saboteur"),
        },
        "Virulence": {
            "role": "DPS",
            "mirror": ("Gunslinger", "Dirty Fighting"),
        },
    },

    "Mercenary": {
        "Bodyguard": {
            "role": "HEAL",
            "mirror": ("Commando", "Combat Medic"),
        },
        "Arsenal": {
            "role": "DPS",
            "mirror": ("Commando", "Gunnery"),
        },
        "Innovative Ordnance": {
            "role": "DPS",
            "mirror": ("Commando", "Assault Specialist"),
        },
    },

    "Powertech": {
        "Shield Tech": {
            "role": "TANK",
            "mirror": ("Vanguard", "Shield Specialist"),
        },
        "Advanced Prototype": {
            "role": "DPS",
            "mirror": ("Vanguard", "Tactics"),
        },
        "Pyrotech": {
            "role": "DPS",
            "mirror": ("Vanguard", "Plasmatech"),
        },
    },

    # ===================================================
    # Republic / Force
    # ===================================================

    "Sentinel": {
        "Watchman": {
            "role": "DPS",
            "mirror": ("Marauder", "Annihilation"),
        },
        "Combat": {
            "role": "DPS",
            "mirror": ("Marauder", "Carnage"),
        },
        "Concentration": {
            "role": "DPS",
            "mirror": ("Marauder", "Fury"),
        },
    },

    "Guardian": {
        "Defense": {
            "role": "TANK",
            "mirror": ("Juggernaut", "Immortal"),
        },
        "Vigilance": {
            "role": "DPS",
            "mirror": ("Juggernaut", "Vengeance"),
        },
        "Focus": {
            "role": "DPS",
            "mirror": ("Juggernaut", "Rage"),
        },
    },

    "Shadow": {
        "Kinetic Combat": {
            "role": "TANK",
            "mirror": ("Assassin", "Darkness"),
        },
        "Infiltration": {
            "role": "DPS",
            "mirror": ("Assassin", "Deception"),
        },
        "Serenity": {
            "role": "DPS",
            "mirror": ("Assassin", "Hatred"),
        },
    },

    "Sage": {
        "Seer": {
            "role": "HEAL",
            "mirror": ("Sorcerer", "Corruption"),
        },
        "Telekinetics": {
            "role": "DPS",
            "mirror": ("Sorcerer", "Lightning"),
        },
        "Balance": {
            "role": "DPS",
            "mirror": ("Sorcerer", "Madness"),
        },
    },

    # ===================================================
    # Republic / Tech
    # ===================================================

    "Scoundrel": {
        "Sawbones": {
            "role": "HEAL",
            "mirror": ("Operative", "Medicine"),
        },
        "Scrapper": {
            "role": "DPS",
            "mirror": ("Operative", "Concealment"),
        },
        "Ruffian": {
            "role": "DPS",
            "mirror": ("Operative", "Lethality"),
        },
    },

    "Gunslinger": {
        "Sharpshooter": {
            "role": "DPS",
            "mirror": ("Sniper", "Marksmanship"),
        },
        "Saboteur": {
            "role": "DPS",
            "mirror": ("Sniper", "Engineering"),
        },
        "Dirty Fighting": {
            "role": "DPS",
            "mirror": ("Sniper", "Virulence"),
        },
    },

    "Commando": {
        "Combat Medic": {
            "role": "HEAL",
            "mirror": ("Mercenary", "Bodyguard"),
        },
        "Gunnery": {
            "role": "DPS",
            "mirror": ("Mercenary", "Arsenal"),
        },
        "Assault Specialist": {
            "role": "DPS",
            "mirror": ("Mercenary", "Innovative Ordnance"),
        },
    },

    "Vanguard": {
        "Shield Specialist": {
            "role": "TANK",
            "mirror": ("Powertech", "Shield Tech"),
        },
        "Tactics": {
            "role": "DPS",
            "mirror": ("Powertech", "Advanced Prototype"),
        },
        "Plasmatech": {
            "role": "DPS",
            "mirror": ("Powertech", "Pyrotech"),
        },
    },
}


SPEC_INFO = {}

for combat_style, disciplines in COMBAT_STYLES.items():
    for discipline, info in disciplines.items():
        SPEC_INFO[(combat_style, discipline)] = {
            "class": combat_style,
            "discipline": discipline,
            "role": info["role"],
            "mirror": info["mirror"],
        }


def get_spec_info(player_class, discipline):
    return SPEC_INFO.get((player_class, discipline))


def get_role(player_class, discipline):
    spec_info = get_spec_info(player_class, discipline)

    if not spec_info:
        return "UNKNOWN"

    return spec_info["role"]


def get_mirror(player_class, discipline):
    spec_info = get_spec_info(player_class, discipline)

    if not spec_info:
        return None

    return spec_info["mirror"]


def is_known_spec(player_class, discipline):
    return (player_class, discipline) in SPEC_INFO


def get_all_specs():
    return SPEC_INFO