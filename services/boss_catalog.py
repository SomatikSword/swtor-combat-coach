import re


def normalize_name(name: str) -> str:
    if not name:
        return ""

    name = name.lower()
    name = name.replace("’", "'")
    name = name.replace("-", " ")
    name = re.sub(r"[^a-z0-9' ]+", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


BOSS_CATALOG = {
    "Eternity Vault": {
        "Annihilation Droid XRR-3": {
            "boss_aliases": [
                "annihilation droid xrr 3",
                "xrr 3",
                "xrr-3",
            ],
            "encounter_aliases": [],
        },
        "Gharj": {
            "boss_aliases": [
                "gharj",
            ],
            "encounter_aliases": [],
        },
        "Ancient Pylons": {
            "boss_aliases": [
                "ancient pylon",
                "ancient pylons",
            ],
            "encounter_aliases": [],
        },
        "Infernal Council": {
            "boss_aliases": [
                "infernal council",
            ],
            "encounter_aliases": [],
        },
        "Soa": {
            "boss_aliases": [
                "soa",
                "soa the infernal one",
            ],
            "encounter_aliases": [],
        },
    },

    "Karagga's Palace": {
        "Bonethrasher": {
            "boss_aliases": [
                "bonethrasher",
            ],
            "encounter_aliases": [
                "wookiee mercenary",
            ],
        },
        "Jarg and Sorno": {
            "boss_aliases": [
                "jarg",
                "sorno",
                "jarg and sorno",
            ],
            "encounter_aliases": [],
        },
        "Foreman Crusher": {
            "boss_aliases": [
                "foreman crusher",
            ],
            "encounter_aliases": [],
        },
        "G4-B3 Heavy Fabricator": {
            "boss_aliases": [
                "g4 b3 heavy fabricator",
                "heavy fabricator",
                "fabricator",
            ],
            "encounter_aliases": [
                "hutt guardian droid",
            ],
        },
        "Karagga the Unyielding": {
            "boss_aliases": [
                "karagga the unyielding",
                "karagga",
            ],
            "encounter_aliases": [],
        },
    },

    "Explosive Conflict": {
        "Zorn and Toth": {
            "boss_aliases": [
                "zorn",
                "toth",
                "zorn and toth",
            ],
            "encounter_aliases": [],
        },
        "Firebrand and Stormcaller": {
            "boss_aliases": [
                "firebrand",
                "stormcaller",
                "firebrand and stormcaller",
            ],
            "encounter_aliases": [],
        },
        "Colonel Vorgath": {
            "boss_aliases": [
                "colonel vorgath",
                "vorgath",
            ],
            "encounter_aliases": [],
        },
        "Warlord Kephess": {
            "boss_aliases": [
                "warlord kephess",
                "kephess",
            ],
            "encounter_aliases": [],
        },
    },

    "Terror From Beyond": {
        "The Writhing Horror": {
            "boss_aliases": [
                "the writhing horror",
                "writhing horror",
            ],
            "encounter_aliases": [],
        },
        "Dread Guards": {
            "boss_aliases": [
                "dread guards",
                "ciphas",
                "heirad",
                "kel'sara",
                "kelsara",
            ],
            "encounter_aliases": [],
        },
        "Operator IX": {
            "boss_aliases": [
                "operator ix",
                "operator",
            ],
            "encounter_aliases": [],
        },
        "Kephess the Undying": {
            "boss_aliases": [
                "kephess the undying",
            ],
            "encounter_aliases": [],
        },
        "Terror From Beyond": {
            "boss_aliases": [
                "terror from beyond",
            ],
            "encounter_aliases": [],
        },
    },

    "Scum and Villainy": {
        "Dash'roode": {
            "boss_aliases": [
                "dash'roode",
                "dashroode",
            ],
            "encounter_aliases": [],
        },
        "Titan 6": {
            "boss_aliases": [
                "titan 6",
                "titan",
            ],
            "encounter_aliases": [],
        },
        "Thrasher": {
            "boss_aliases": [
                "thrasher",
            ],
            "encounter_aliases": [],
        },
        "Operations Chief": {
            "boss_aliases": [
                "operations chief",
            ],
            "encounter_aliases": [],
        },
        "Olok the Shadow": {
            "boss_aliases": [
                "olok the shadow",
                "olok",
            ],
            "encounter_aliases": [],
        },
        "Cartel Warlords": {
            "boss_aliases": [
                "cartel warlords",
            ],
            "encounter_aliases": [],
        },
        "Dread Master Styrak": {
            "boss_aliases": [
                "dread master styrak",
                "styrak",
            ],
            "encounter_aliases": [],
        },
    },

    "Dread Fortress": {
        "Nefra": {
            "boss_aliases": [
                "nefra",
                "nefra who bars the way",
            ],
            "encounter_aliases": [],
        },
        "Gate Commander Draxus": {
            "boss_aliases": [
                "gate commander draxus",
                "draxus",
            ],
            "encounter_aliases": [],
        },
        "Grob'thok": {
            "boss_aliases": [
                "grob'thok",
                "grobthok",
            ],
            "encounter_aliases": [],
        },
        "Corruptor Zero": {
            "boss_aliases": [
                "corruptor zero",
            ],
            "encounter_aliases": [],
        },
        "Dread Master Brontes": {
            "boss_aliases": [
                "dread master brontes",
                "brontes",
            ],
            "encounter_aliases": [],
        },
    },

    "Dread Palace": {
        "Dread Master Bestia": {
            "boss_aliases": [
                "dread master bestia",
                "bestia",
            ],
            "encounter_aliases": [],
        },
        "Dread Master Tyrans": {
            "boss_aliases": [
                "dread master tyrans",
                "tyrans",
            ],
            "encounter_aliases": [],
        },
        "Dread Master Calphayus": {
            "boss_aliases": [
                "dread master calphayus",
                "calphayus",
            ],
            "encounter_aliases": [],
        },
        "Dread Master Raptus": {
            "boss_aliases": [
                "dread master raptus",
                "raptus",
            ],
            "encounter_aliases": [],
        },
        "Dread Council": {
            "boss_aliases": [
                "dread council",
            ],
            "encounter_aliases": [],
        },
    },

    "The Ravagers": {
        "Sparky": {
            "boss_aliases": [
                "sparky",
            ],
            "encounter_aliases": [],
        },
        "Quartermaster Bulo": {
            "boss_aliases": [
                "quartermaster bulo",
                "bulo",
            ],
            "encounter_aliases": [],
        },
        "Torque": {
            "boss_aliases": [
                "torque",
            ],
            "encounter_aliases": [],
        },
        "Master and Blaster": {
            "boss_aliases": [
                "master",
                "blaster",
                "master and blaster",
            ],
            "encounter_aliases": [],
        },
        "Coratanni": {
            "boss_aliases": [
                "coratanni",
                "ruugar",
            ],
            "encounter_aliases": [],
        },
    },

    "Temple of Sacrifice": {
        "Malaphar the Savage": {
            "boss_aliases": [
                "malaphar the savage",
                "malaphar",
            ],
            "encounter_aliases": [],
        },
        "Sword Squadron": {
            "boss_aliases": [
                "sword squadron",
                "unit 1",
                "unit 2",
            ],
            "encounter_aliases": [],
        },
        "The Underlurker": {
            "boss_aliases": [
                "the underlurker",
                "underlurker",
            ],
            "encounter_aliases": [],
        },
        "Revanite Commanders": {
            "boss_aliases": [
                "revanite commanders",
            ],
            "encounter_aliases": [],
        },
        "Revan": {
            "boss_aliases": [
                "revan",
            ],
            "encounter_aliases": [],
        },
    },

    "Gods from the Machine": {
        "Tyth": {
            "boss_aliases": [
                "tyth",
            ],
            "encounter_aliases": [
                "preservation droid",
                "extermination droid",
            ],
        },
        "Aivela and Esne": {
            "boss_aliases": [
                "aivela",
                "esne",
                "aivela and esne",
            ],
            "encounter_aliases": [],
        },
        "Nahut": {
            "boss_aliases": [
                "nahut",
                "the son of shadow",
            ],
            "encounter_aliases": [
                "singularity chamber",
            ],
        },
        "Scyva": {
            "boss_aliases": [
                "scyva",
            ],
            "encounter_aliases": [
                "scyvan hunter",
                "immolation droid",
            ],
        },
        "Izax": {
            "boss_aliases": [
                "izax",
            ],
            "encounter_aliases": [
                "omega protocol droid",
            ],
        },
    },

    "Nature of Progress": {
    # "Red": {
    #     "boss_aliases": [
    #         "red",
    #     ],
    #     "encounter_aliases": [],
    # },
        "Breach CI-004": {
            "boss_aliases": [
                "breach ci 004",
                "breach",
            ],
            "encounter_aliases": [],
        },
        "Trandoshan Squad": {
            "boss_aliases": [
                "trandoshan squad",
            ],
            "encounter_aliases": [],
        },
        "Huntmaster": {
            "boss_aliases": [
                "huntmaster",
            ],
            "encounter_aliases": [],
        },
        "Apex Vanguard": {
            "boss_aliases": [
                "apex vanguard",
                "apex",
            ],
            "encounter_aliases": [],
        },
    },

    "R-4 Anomaly": {
        "IP-CPT": {
            "boss_aliases": [
                "ip cpt",
                "ipcpt",
                "ip-cpt",
            ],
            "encounter_aliases": [],
        },
        "Watchdog": {
            "boss_aliases": [
                "watchdog",
            ],
            "encounter_aliases": [],
        },
        "Lord Kanoth": {
            "boss_aliases": [
                "lord kanoth",
                "kanoth",
            ],
            "encounter_aliases": [],
        },
        "Lady Dominique": {
            "boss_aliases": [
                "lady dominique",
                "dominique",
            ],
            "encounter_aliases": [],
        },
    },
}


TRASH_NAMES = {
    "sniper",
    "strong sniper",
    "elite sniper",
    "mercenary",
    "wookiee mercenary",
    "hutt guardian droid",
}


def iter_catalog_entries():
    for operation_name, bosses in BOSS_CATALOG.items():
        for boss_name, data in bosses.items():
            yield operation_name, boss_name, data