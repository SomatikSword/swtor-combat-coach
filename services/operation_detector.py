OPERATIONS = {

    "Eternity Vault": [
        "Annihilation Droid XRR-3",
        "Gharj",
        "Soa",
        "Rakata Eternal Guardian",
        "Perimeter Defense Cannon"
    ],

    "Explosive Conflict": [
        "Zorn",
        "Toth",
        "Firebrand",
        "Stormcaller",
        "Colonel Vorgath",
        "Warlord Kephess"
    ],

    "Explosive Conflict": [
        "Zorn",
        "Toth",
        "Firebrand",
        "Stormcaller",
        "Colonel Vorgath",
        "Warlord Kephess"
    ],

    "Terror From Beyond": [
        "The Writhing Horror",
        "Dread Guard",
        "Operator IX",
        "Kephess the Undying",
        "Terror From Beyond"
    ],

    "Scum & Villainy": [
        "Dash'roode",
        "Titan 6",
        "Thrasher",
        "Operations Chief",
        "Olok the Shadow",
        "Cartel Warlords",
        "Styrak"
    ],

    "Dread Fortress": [
        "Nefra",
        "Draxus",
        "Grob'thok",
        "Corruptor Zero",
        "Brontes"
    ],

    "Dread Palace": [
        "Bestia",
        "Tyrans",
        "Calphayus",
        "Raptus",
        "Council"
    ],

    "The Ravagers": [
        "Sparky",
        "Quartermaster Bulo",
        "Torque",
        "Blaster",
        "Master",
        "Coratanni"
    ],

    "Temple of Sacrifice": [
        "Malaphar",
        "Sword Squadron",
        "Underlurker",
        "Revanite Commanders",
        "Revan"
    ],

    "Gods from the Machine": [
        "Tyth",
        "Aivela",
        "Esne",
        "Nahut",
        "Scyva",
        "Izax"
    ],

    "Nature of Progress": [
        "Red",
        "Breach CI-004",
        "Trandoshan Squad",
        "The Huntmaster",
        "Apex Vanguard"
    ],
}


def detect_operation(boss_list):

    for operation_name, operation_bosses in OPERATIONS.items():

        matches = sum(
            1
            for boss in boss_list
            if any(boss.startswith(op_boss) for op_boss in operation_bosses)
        )

        if matches >= 2:
            return operation_name

    return "Не удалось определить"