TANK_CONFIG = {
    # ---------------- Republic tanks ----------------

    ("Shadow", "Kinetic Combat"): {
        "taunts": [
            "Mind Control",
            "Mass Mind Control",
        ],
        "defensives": [
            "Kinetic Ward",
            "Deflection",
            "Battle Readiness",
            "Resilience",
            "Force Cloak",
            "Force Speed",
        ],
        "tracked_effects": [
            "Kinetic Ward",
            "Deflection",
            "Battle Readiness",
            "Resilience",
        ],
        "maintenance_effects": [
            "Kinetic Ward",
        ],
    },

    ("Guardian", "Defense"): {
        "taunts": [
            "Taunt",
            "Challenging Call",
        ],
        "defensives": [
            "Saber Ward",
            "Warding Call",
            "Enure",
            "Saber Reflect",
            "Focused Defense",
        ],
        "tracked_effects": [
            "Saber Ward",
            "Warding Call",
            "Enure",
            "Saber Reflect",
            "Focused Defense",
        ],
        "maintenance_effects": [],
    },

    ("Vanguard", "Shield Specialist"): {
        "taunts": [
            "Neural Jolt",
            "Sonic Round",
        ],
        "defensives": [
            "Reactive Shield",
            "Adrenaline Rush",
            "Riot Gas",
            "Hold the Line",
            "Power Yield",
        ],
        "tracked_effects": [
            "Reactive Shield",
            "Adrenaline Rush",
            "Riot Gas",
            "Hold the Line",
            "Power Yield",
        ],
        "maintenance_effects": [],
    },

    # ---------------- Empire tanks ----------------

    ("Assassin", "Darkness"): {
        "taunts": [
            "Mind Control",
            "Mass Mind Control",
        ],
        "defensives": [
            "Dark Ward",
            "Deflection",
            "Overcharge Saber",
            "Force Shroud",
            "Force Cloak",
            "Force Speed",
        ],
        "tracked_effects": [
            "Dark Ward",
            "Deflection",
            "Overcharge Saber",
            "Force Shroud",
        ],
        "maintenance_effects": [
            "Dark Ward",
        ],
    },

    ("Juggernaut", "Immortal"): {
        "taunts": [
            "Taunt",
            "Threatening Scream",
        ],
        "defensives": [
            "Saber Ward",
            "Invincible",
            "Endure Pain",
            "Saber Reflect",
            "Enraged Defense",
        ],
        "tracked_effects": [
            "Saber Ward",
            "Invincible",
            "Endure Pain",
            "Saber Reflect",
            "Enraged Defense",
        ],
        "maintenance_effects": [],
    },

    ("Powertech", "Shield Tech"): {
        "taunts": [
            "Neural Dart",
            "Sonic Missile",
        ],
        "defensives": [
            "Energy Shield",
            "Kolto Overload",
            "Oil Slick",
            "Hydraulic Overrides",
            "Power Yield",
        ],
        "tracked_effects": [
            "Energy Shield",
            "Kolto Overload",
            "Oil Slick",
            "Hydraulic Overrides",
            "Power Yield",
        ],
        "maintenance_effects": [],
    },
}


def get_tank_config(player_class, discipline):
    return TANK_CONFIG.get(
        (player_class, discipline),
        {
            "taunts": [],
            "defensives": [],
            "tracked_effects": [],
            "maintenance_effects": [],
        }
    )