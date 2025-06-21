import random
import requests
import sounddevice as sd
import numpy as np
import os
import subprocess
import re
import logging
import datetime
import sys
from collections import defaultdict

# Configure logging
log_filename = f"rpg_adventure_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# API URLs
ALLTALK_API_URL = "http://localhost:7851/api/tts-generate"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

#getting the models from ollama
def get_installed_models():
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        models = []
        for line in lines[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception as e:
        logging.error(f"Error getting installed models: {e}")
        return []

def count_subarrays(arr, k):
    n = len(arr)
    left = 0
    distinct = 0
    freq = defaultdict(int)
    total = 0
    for right in range(n):
        if freq[arr[right]] == 0:
            distinct += 1
        freq[arr[right]] += 1

        while distinct > k:
            freq[arr[left]] -= 1
            if freq[arr[left]] == 0:
                distinct -= 1
            left += 1

        total += (right - left + 1)

    return total

installed_models = get_installed_models()
ollama_model = "llama3:instruct"  # Default model

if installed_models:
    print("Available Ollama models:")
    for idx, m in enumerate(installed_models, 1):
        print(f"  {idx}: {m}")
    while True:
        choice = input("Select a model by number (or press Enter for default llama3:instruct): ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(installed_models):
                ollama_model = installed_models[idx]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
else:
    model_input = input("Enter Ollama model name (e.g., llama3:instruct): ").strip()
    if model_input:
        ollama_model = model_input

print(f"Using Ollama model: {ollama_model}\n")

CURRENCY_MAP = {
    "Fantasy": "gold",
    "Sci-Fi": "credits",
    "Cyberpunk": "eurodollars",
    "Post-Apocalyptic": "bottle caps"
}

CLASS_ABILITIES = {
    "Fantasy": {
        "Peasant": {
            "abilities": ["Farm Knowledge", "Animal Handling", "Simple Crafting"],
            "weapons": ["pitchfork", "sickle", "wooden staff", "sling", "short bow"],
            "armor": ["cloth", "leather"],
            "magic": False
        },
        "Noble": {
            "abilities": ["Diplomacy", "Leadership", "Wealth Management"],
            "weapons": ["rapier", "longsword", "dagger"],
            "armor": ["chainmail", "plate"],
            "magic": False
        },
        "Mage": {
            "abilities": ["Arcane Knowledge", "Spellcasting", "Ritual Magic"],
            "weapons": ["staff", "wand", "dagger"],
            "armor": ["cloth", "robes"],
            "magic": True
        },
        "Knight": {
            "abilities": ["Heavy Armor", "Shield", "Sword Fighting"],
            "weapons": ["longsword", "mace", "lance"],
            "armor": ["chainmail", "plate"],
            "magic": False
        },
        "Ranger": {
            "abilities": ["Tracking", "Archery", "Stealth"],
            "weapons": ["longbow", "shortbow", "twin daggers"],
            "armor": ["leather", "studded leather"],
            "magic": False
        },
        "Thief": {
            "abilities": ["Lockpicking", "Pickpocket", "Stealth"],
            "weapons": ["dagger", "shortsword", "throwing knives"],
            "armor": ["leather"],
            "magic": False
        },
        "Bard": {
            "abilities": ["Performance", "Inspiration", "Storytelling"],
            "weapons": ["lute", "dagger", "rapier"],
            "armor": ["leather", "studded leather"],
            "magic": True
        },
        "Cleric": {
            "abilities": ["Divine Magic", "Healing", "Faith"],
            "weapons": ["mace", "warhammer", "staff"],
            "armor": ["chainmail", "plate"],
            "magic": True
        },
        "Assassin": {
            "abilities": ["Stealth", "Poison", "Disguise"],
            "weapons": ["dagger", "shortsword", "crossbow"],
            "armor": ["leather"],
            "magic": False
        },
        "Paladin": {
            "abilities": ["Divine Smite", "Lay on Hands", "Aura of Protection"],
            "weapons": ["longsword", "warhammer", "mace"],
            "armor": ["chainmail", "plate"],
            "magic": True
        },
        "Alchemist": {
            "abilities": ["Potion Making", "Bomb Crafting", "Chemical Knowledge"],
            "weapons": ["flask", "dagger", "staff"],
            "armor": ["cloth", "leather"],
            "magic": False
        },
        "Druid": {
            "abilities": ["Nature Magic", "Shape-shifting", "Animal Communication"],
            "weapons": ["staff", "sickle", "sling"],
            "armor": ["leather", "hide"],
            "magic": True
        },
        "Warlock": {
            "abilities": ["Eldritch Blast", "Pact Magic", "Invocations"],
            "weapons": ["dagger", "staff", "wand"],
            "armor": ["cloth", "leather"],
            "magic": True
        },
        "Monk": {
            "abilities": ["Martial Arts", "Unarmored Defense", "Ki Powers"],
            "weapons": ["fists", "quarterstaff", "nunchaku"],
            "armor": ["cloth"],
            "magic": False
        },
        "Sorcerer": {
            "abilities": ["Innate Magic", "Metamagic", "Elemental Control"],
            "weapons": ["dagger", "wand", "staff"],
            "armor": ["cloth"],
            "magic": True
        },
        "Beastmaster": {
            "abilities": ["Animal Companion", "Wild Empathy", "Nature Lore"],
            "weapons": ["spear", "shortbow", "whip"],
            "armor": ["leather", "hide"],
            "magic": False
        },
        "Enchanter": {
            "abilities": ["Item Enhancement", "Charm Magic", "Illusions"],
            "weapons": ["wand", "staff", "dagger"],
            "armor": ["cloth", "robes"],
            "magic": True
        },
        "Blacksmith": {
            "abilities": ["Weapon Crafting", "Armor Forging", "Repair"],
            "weapons": ["hammer", "tongs", "anvil"],
            "armor": ["leather", "chainmail"],
            "magic": False
        },
        "Merchant": {
            "abilities": ["Haggling", "Appraisal", "Networking"],
            "weapons": ["dagger", "shortsword", "coin purse"],
            "armor": ["cloth", "leather"],
            "magic": False
        },
        "Gladiator": {
            "abilities": ["Arena Combat", "Weapon Mastery", "Showmanship"],
            "weapons": ["trident", "net", "gladius"],
            "armor": ["chainmail", "plate"],
            "magic": False
        },
        "Wizard": {
            "abilities": ["Spellbook", "Ritual Casting", "Arcane Research"],
            "weapons": ["staff", "wand", "dagger"],
            "armor": ["cloth", "robes"],
            "magic": True
        }
    },
    "Sci-Fi": {
        "Space Marine": {
            "abilities": ["Heavy Weapons", "Combat Armor", "Tactical Awareness"],
            "weapons": ["plasma rifle", "combat knife", "grenade launcher"],
            "armor": ["power armor"],
            "magic": False
        },
        "Scientist": {
            "abilities": ["Research", "Hacking", "Technical Analysis"],
            "weapons": ["stun gun", "laser scalpel"],
            "armor": ["lab coat"],
            "magic": False
        },
        "Android": {
            "abilities": ["System Integration", "Data Analysis", "Precision"],
            "weapons": ["laser pistol", "energy blade"],
            "armor": ["synthetic skin", "light armor"],
            "magic": False
        },
        "Pilot": {
            "abilities": ["Starship Operation", "Navigation", "Evasion"],
            "weapons": ["pistol", "stun baton"],
            "armor": ["flight suit"],
            "magic": False
        },
        "Engineer": {
            "abilities": ["Repair", "Construction", "System Override"],
            "weapons": ["wrench", "plasma cutter"],
            "armor": ["utility suit"],
            "magic": False
        },
        "Alien Diplomat": {
            "abilities": ["Xenolinguistics", "Negotiation", "Cultural Insight"],
            "weapons": ["diplomatic immunity", "translator device"],
            "armor": ["ceremonial robes"],
            "magic": False
        },
        "Bounty Hunter": {
            "abilities": ["Tracking", "Trap Setting", "Bounty Collection"],
            "weapons": ["blaster rifle", "net gun", "stun cuffs"],
            "armor": ["composite armor"],
            "magic": False
        },
        "Starship Captain": {
            "abilities": ["Command Presence", "Tactical Analysis", "Leadership"],
            "weapons": ["phaser pistol", "ceremonial sword"],
            "armor": ["command uniform"],
            "magic": False
        },
        "Space Pirate": {
            "abilities": ["Boarding", "Contraband", "Infiltration"],
            "weapons": ["cutlass", "blaster pistol"],
            "armor": ["light armor"],
            "magic": False
       },
        "Navigator": {
            "abilities": ["Astrogation", "Spatial Awareness", "Wormhole Navigation"],
            "weapons": ["pistol", "navigation computer"],
            "armor": ["flight suit"],
            "magic": False
        },
        "Robot Technician": {
            "abilities": ["Droid Repair", "AI Programming", "System Diagnostics"],
            "weapons": ["ion blaster", "stun prod"],
            "armor": ["tech suit"],
            "magic": False
        },
        "Cybernetic Soldier": {
            "abilities": ["Enhanced Reflexes", "Targeting Systems", "Combat Implants"],
            "weapons": ["assault rifle", "grenades"],
            "armor": ["combat armor"],
            "magic": False
        },
        "Explorer": {
            "abilities": ["Planetary Survey", "Survival", "First Contact"],
            "weapons": ["laser rifle", "survival knife"],
            "armor": ["exploration suit"],
            "magic": False
        },
        "Astrobiologist": {
            "abilities": ["Xenobiology", "Sample Analysis", "Field Research"],
            "weapons": ["tranq gun", "specimen collector"],
            "armor": ["biohazard suit"],
            "magic": False
        },
        "Quantum Hacker": {
            "abilities": ["System Penetration", "Data Theft", "Firewall Breach"],
            "weapons": ["cyberdeck", "logic bomb"],
            "armor": ["data suit"],
            "magic": False
        },
        "Galactic Trader": {
            "abilities": ["Market Analysis", "Bartering", "Supply Chain"],
            "weapons": ["pistol", "credit chip"],
            "armor": ["business attire"],
            "magic": False
        },
        "AI Specialist": {
            "abilities": ["Neural Networks", "Machine Learning", "AI Ethics"],
            "weapons": ["logic probe", "system override"],
            "armor": ["tech suit"],
            "magic": False
        },
        "Terraformer": {
            "abilities": ["Atmospheric Control", "Ecological Design", "Planetary Engineering"],
            "weapons": ["geo-drill", "climate controller"],
            "armor": ["environment suit"],
            "magic": False
        },
        "Cyberneticist": {
            "abilities": ["Implant Installation", "Neural Enhancement", "Prosthetic Design"],
            "weapons": ["surgical laser", "neural scrambler"],
            "armor": ["medic armor"],
            "magic": False
        }
    },
    "Cyberpunk": {
        "Hacker": {
            "abilities": ["Cyberdeck", "System Breach", "Data Steal"],
            "weapons": ["stun gun", "taser"],
            "armor": ["light jacket"],
            "magic": False
        },
        "Street Samurai": {
            "abilities": ["Combat Implants", "Blade Mastery", "Reflex Boost"],
            "weapons": ["katana", "pistol", "smg"],
            "armor": ["light armor", "dermal plating"],
            "magic": False
        },
        "Corporate Agent": {
            "abilities": ["Corporate Espionage", "Influence", "Resource Management"],
            "weapons": ["taser", "stun baton"],
            "armor": ["business suit"],
            "magic": False
        },
        "Techie": {
            "abilities": ["Gadget Creation", "Drone Control", "System Repair"],
            "weapons": ["wrench", "laser cutter"],
            "armor": ["tech vest"],
            "magic": False
        },
        "Rebel Leader": {
            "abilities": ["Charisma", "Guerrilla Tactics", "Underground Network"],
            "weapons": ["assault rifle", "molotov"],
            "armor": ["combat armor"],
            "magic": False
        },
        "Cyborg": {
            "abilities": ["Enhanced Strength", "Targeting Systems", "Subdermal Armor"],
            "weapons": ["minigun", "rocket launcher"],
            "armor": ["cybernetics"],
            "magic": False
        },
        "Drone Operator": {
            "abilities": ["Drone Swarm", "Surveillance", "Remote Combat"],
            "weapons": ["drone controller", "pistol"],
            "armor": ["light armor"],
            "magic": False
        },
        "Synth Dealer": {
            "abilities": ["Black Market", "Cyberware Installation", "Contraband"],
            "weapons": ["needle gun", "stun prod"],
            "armor": ["leather jacket"],
            "magic": False
        },
        "Information Courier": {
            "abilities": ["Stealth", "Evasion", "Data Smuggling"],
            "weapons": ["pistol", "stun baton"],
            "armor": ["runner suit"],
            "magic": False
        },
        "Augmentation Engineer": {
            "abilities": ["Cyberware Installation", "Neural Enhancement", "Bio-modification"],
            "weapons": ["surgical laser", "neural scrambler"],
            "armor": ["medic armor"],
            "magic": False
        },
        "Black Market Dealer": {
            "abilities": ["Bartering", "Contraband", "Underground Contacts"],
            "weapons": ["shotgun", "pistol"],
            "armor": ["trench coat"],
            "magic": False
        },
        "Scumbag": {
            "abilities": ["Street Smarts", "Pickpocket", "Con Artist"],
            "weapons": ["knife", "brass knuckles"],
            "armor": ["street clothes"],
            "magic": False
        },
        "Police": {
            "abilities": ["Law Enforcement", "Tactical Response", "Investigation"],
            "weapons": ["stun baton", "pistol", "shotgun"],
            "armor": ["riot gear"],
            "magic": False
        }
    },
    "Post-Apocalyptic": {
        "Survivor": {
            "abilities": ["Scavenging", "Stealth", "First Aid"],
            "weapons": ["makeshift spear", "pipe", "crossbow"],
            "armor": ["leather", "scrap metal"],
            "magic": False
        },
        "Scavenger": {
            "abilities": ["Salvage", "Repair", "Barter"],
            "weapons": ["wrench", "shotgun", "pistol"],
            "armor": ["leather", "scrap metal"],
            "magic": False
        },
        "Mutant": {
            "abilities": ["Radiation Resistance", "Mutant Powers", "Wasteland Adaptation"],
            "weapons": ["claws", "toxic spit", "mutant strength"],
            "armor": ["mutated hide"],
            "magic": False
        },
        "Trader": {
            "abilities": ["Barter", "Supply Chain", "Negotiation"],
            "weapons": ["pistol", "barter goods"],
            "armor": ["leather", "trench coat"],
            "magic": False
        },
        "Raider": {
            "abilities": ["Ambush", "Intimidation", "Loot Collection"],
            "weapons": ["shotgun", "molotov", "spiked bat"],
            "armor": ["scrap armor"],
            "magic": False
        },
        "Medic": {
            "abilities": ["Field Medicine", "Herbalism", "Disease Treatment"],
            "weapons": ["syringe", "scalpel"],
            "armor": ["medic coat"],
            "magic": False
        },
        "Cult Leader": {
            "abilities": ["Charisma", "Ritual Performance", "Faith Healing"],
            "weapons": ["ceremonial dagger", "holy symbol"],
            "armor": ["robes"],
            "magic": False
        },
        "Berserker": {
            "abilities": ["Adrenaline Rush", "Pain Resistance", "Frenzy"],
            "weapons": ["axe", "sledgehammer", "chainsaw"],
            "armor": ["scrap metal"],
            "magic": False
        },
        "Soldier": {
            "abilities": ["Combat Training", "Tactics", "Weapon Proficiency"],
            "weapons": ["assault rifle", "combat knife"],
            "armor": ["combat armor"],
            "magic": False
        }
    }
}

ROLE_STARTERS = {
    "Fantasy": {
        "Peasant": "You're toiling in the fields of a small village when",
        "Noble": "You're overseeing your estate's affairs when",
        "Mage": "You're studying ancient tomes in your tower when",
        "Knight": "You're training in the castle courtyard when",
        "Ranger": "You're tracking game in the deep forest when",
        "Thief": "You're casing a noble's manor in the city when",
        "Bard": "You're performing in a crowded tavern when",
        "Cleric": "You're tending to the sick in the temple when",
        "Assassin": "You're preparing for a contract in the shadows when",
        "Paladin": "You're praying at the altar of your deity when",
        "Alchemist": "You're carefully measuring reagents in your alchemy lab when",
        "Druid": "You're communing with nature in the sacred grove when",
        "Warlock": "You're negotiating with your otherworldly patron when",
        "Monk": "You're meditating in the monastery courtyard when",
        "Sorcerer": "You're struggling to control your innate magical powers when",
        "Beastmaster": "You're training your animal companions in the forest clearing when",
        "Enchanter": "You're imbuing magical properties into a mundane object when",
        "Blacksmith": "You're forging a new weapon at your anvil when",
        "Merchant": "You're haggling with customers at the marketplace when",
        "Gladiator": "You're preparing for combat in the arena when",
        "Wizard": "You're researching new spells in your arcane library when"
    },
    "Sci-Fi": {
        "Space Marine": "You're conducting patrol on a derelict space station when",
        "Scientist": "You're analyzing alien samples in your lab when",
        "Android": "You're performing system diagnostics on your ship when",
        "Pilot": "You're navigating through an asteroid field when",
        "Engineer": "You're repairing the FTL drive when",
        "Alien Diplomat": "You're negotiating with an alien delegation when",
        "Bounty Hunter": "You're tracking a target through a spaceport when",
        "Starship Captain": "You're commanding the bridge during warp travel when",
        "Space Pirate": "You're plotting your next raid from your starship's bridge when",
        "Navigator": "You're charting a course through uncharted space when",
        "Robot Technician": "You're repairing a malfunctioning android when",
        "Cybernetic Soldier": "You're calibrating your combat implants when",
        "Explorer": "You're scanning a newly discovered planet when",
        "Astrobiologist": "You're studying alien life forms in your lab when",
        "Quantum Hacker": "You're breaching a corporate firewall when",
        "Galactic Trader": "You're negotiating a deal for rare resources when",
        "AI Specialist": "You're debugging a sentient AI's personality matrix when",
        "Terraformer": "You're monitoring atmospheric changes on a new colony world when",
        "Cyberneticist": "You're installing neural enhancements in a patient when"
    },
    "Cyberpunk": {
        "Hacker": "You're infiltrating a corporate network when",
        "Street Samurai": "You're patrolling the neon-lit streets when",
        "Corporate Agent": "You're closing a deal in a high-rise office when",
        "Techie": "You're modifying cyberware in your workshop when",
        "Rebel Leader": "You're planning a raid on a corporate facility when",
        "Cyborg": "You're calibrating your cybernetic enhancements when",
        "Drone Operator": "You're controlling surveillance drones from your command center when",
        "Synth Dealer": "You're negotiating a deal for illegal cybernetics when",
        "Information Courier": "You're delivering sensitive data through dangerous streets when",
        "Augmentation Engineer": "You're installing cyberware in a back-alley clinic when",
        "Black Market Dealer": "You're arranging contraband in your hidden shop when",
        "Scumbag": "You're looking for an easy mark in the slums when",
        "Police": "You're patrolling the neon-drenched streets when"
    },
    "Post-Apocalyptic": {
        "Survivor": "You're scavenging in the ruins of an old city when",
        "Scavenger": "You're searching a pre-collapse bunker when",
        "Raider": "You're ambushing a convoy in the wasteland when",
        "Medic": "You're treating radiation sickness in your clinic when",
        "Cult Leader": "You're preaching to your followers at a ritual when",
        "Mutant": "You're hiding your mutations in a settlement when",
        "Trader": "You're bartering supplies at a wasteland outpost when",
        "Berserker": "You're sharpening your weapons for the next raid when",
        "Soldier": "You're guarding a settlement from raiders when"
    }
}


CLASS_STARTING_CURRENCY = {
    "Fantasy": {
        "Peasant": 1,
        "Noble": 100,
        "Mage": 10,
        "Knight": 30,
        "Ranger": 15,
        "Thief": 40,
        "Bard": 25,
        "Cleric": 30,
        "Assassin": 50,
        "Paladin": 40,
        "Alchemist": 15,
        "Druid": 20,
        "Warlock": 15,
        "Monk": 5,
        "Sorcerer": 10,
        "Beastmaster": 15,
        "Enchanter": 10,
        "Blacksmith": 30,
        "Merchant": 180,
        "Gladiator": 10,
        "Wizard": 25
    },
    "Sci-Fi": {
        "Space Marine": 30,
        "Scientist": 10,
        "Android": 1,
        "Pilot": 10,
        "Engineer": 15,
        "Alien Diplomat": 1000,
        "Bounty Hunter": 600,
        "Starship Captain": 180,
        "Space Pirate": 500,
        "Navigator": 40,
        "Robot Technician": 25,
        "Cybernetic Soldier": 35,
        "Explorer": 30,
        "Astrobiologist": 30,
        "Quantum Hacker": 70,
        "Galactic Trader": 200,
        "AI Specialist": 60,
        "Terraformer": 50,
        "Cyberneticist": 55
    },
    "Cyberpunk": {
        "Hacker": 50,
        "Street Samurai": 30,
        "Corporate Agent": 100,
        "Techie": 45,
        "Rebel Leader": 40,
        "Cyborg": 20,
        "Drone Operator": 50,
        "Synth Dealer": 80,
        "Information Courier": 35,
        "Augmentation Engineer": 60,
        "Black Market Dealer": 90,
        "Scumbag": 10,
        "Police": 40
    },
    "Post-Apocalyptic": {
        "Survivor": 10,
        "Scavenger": 20,
        "Mutant": 0,
        "Trader": 50,
        "Raider": 30,
        "Medic": 25,
        "Cult Leader": 40,
        "Berserker": 15,
        "Soldier": 20
    }
}

GENRE_LOCATIONS = {
    "Fantasy": [
        # Existing locations
        "The Enchanted Forest",
        "Dragon's Peak",
        "The Royal Castle of Eldoria",
        "The Cursed Swamp",
        "The Ancient Library of Aether",
        "The Dwarven Mines of Khazad",
        "The Elven City of Lythanden",
        "The Dark Lord's Fortress",
        "The Coastal Town of Seabreeze",
        "The Haunted Graveyard",
        # New calm locations
        "Willow Creek Village",
        "Serenity Gardens",
        "Moonlit Meditation Grove",
        "Harmony Valley",
        "The Tranquil Tea House",
        "Sunrise Meadow",
        "Whispering Pines Sanctuary",
        "Crystal Lake Retreat",
        "Golden Harvest Farm",
        "Starlight Observatory",
        # New building locations
        "The Gilded Griffin Tavern",
        "Moonstone Inn & Guesthouse",
        "Royal Archives of Knowledge",
        "Artisan's Guild Hall",
        "Temple of the Evening Star"
    ],
    "Sci-Fi": [
        # Existing locations
        "Alpha Centauri Space Station",
        "The Martian Colonies",
        "The Outer Rim Asteroid Belt",
        "The Quantum Nexus Research Facility",
        "The Alien Jungle Planet Zeta Prime",
        "The Derelict Generation Ship 'Odyssey'",
        "The Cybernetic Metropolis on Titan",
        "The Floating City of Venus",
        "The Black Hole Observatory",
        "The Rebel Base on Europa",
        # New calm locations
        "Nebula Spa Resort",
        "Zero-G Meditation Chamber",
        "Botanical Gardens of New Eden",
        "Stellar Library Archive",
        "Harmony Orbital Station",
        "Quantum Tea Ceremony Room",
        "Galactic History Museum",
        "Solar Wind Lounge",
        "Nova Cafe Observatory",
        "Tranquility Base Habitat",
        # New building locations
        "Quantum Cantina Lounge",
        "Starbase Sigma Recreation Hub",
        "Neural Nexus Data Library",
        "Exoplanet Research Institute",
        "Orbital Gardens Conservatory"
    ],
    "Cyberpunk": [
        # Existing locations
        "Neo-Tokyo Downtown District",
        "The Corporate Tower of OmniCorp",
        "The Underground Hackers' Den",
        "The Neon-Laced Red Light District",
        "The Abandoned Industrial Sector",
        "The Floating Market in the Harbor",
        "The Augmentation Clinic 'Body Shop'",
        "The Virtual Reality Arcade 'NeuroDream'",
        "The Police Headquarters Precinct 13",
        "The Rooftop Gardens of the Elite",
        # New calm locations
        "Zenith Meditation Pods",
        "Neon Lotus Tea House",
        "Dataflow Poetry Lounge",
        "Harmony Cyber-Cafe",
        "Tranquil Skybridge Walkway",
        "Retro Book Nook Cafe",
        "Aqua Gardens Aquarium",
        "Holographic Art Gallery",
        "Synth-Jazz Club Lounge",
        "Memory Lane Archive",
        # New building locations
        "Neon Nights Nightclub",
        "Data Haven Coffee Shop",
        "Augmentation Lounge & Bar",
        "Holo-Movie Theater Complex",
        "Underground Bazaar Marketplace"
    ],
    "Post-Apocalyptic": [
        # Existing locations
        "The Ruins of Old New York",
        "The Oasis Settlement",
        "The Radioactive Wasteland",
        "The Scavenger Camp 'Fort Hope'",
        "The Mutant Hive",
        "The Barter Town 'Crossroads'",
        "The Underground Bunker Complex",
        "The Damaged Nuclear Power Plant",
        "The Deserted Highway 'Death Road'",
        "The Cult of the Sun Temple",
        # New calm locations
        "Sanctuary Greenhouse",
        "Hope's Respite Cafe",
        "Sunset Viewpoint",
        "Memory Library Archive",
        "Tranquil Water Source",
        "Community Storytelling Circle",
        "Starlight Watch Point",
        "Salvaged Art Garden",
        "Peaceful Meditation Rock",
        "Community Crafting Hall",
        # New building locations
        "The Last Chance Saloon",
        "Scrap Metal Trading Post",
        "Bunker 42 Community Center",
        "Water Purification Plant Hub",
        "Salvager's Guild Hall"
    ]
}

def get_role_starter(genre, role):
    if genre in ROLE_STARTERS and role in ROLE_STARTERS[genre]:
        return ROLE_STARTERS[genre][role]

    generic_starters = {
        "Fantasy": "You're going about your daily duties when",
        "Sci-Fi": "You're performing routine tasks aboard your vessel when",
        "Cyberpunk": "You're navigating the neon-lit streets when",
        "Post-Apocalyptic": "You're surviving in the wasteland when"
    }

    if genre in generic_starters:
        return generic_starters[genre]

    return "You find yourself in an unexpected situation when"

def get_class_description(genre, player_class):
    if genre in CLASS_ABILITIES and player_class in CLASS_ABILITIES[genre]:
        abilities = CLASS_ABILITIES[genre][player_class]
        desc = f"{player_class} - "
        desc += f"Abilities: {', '.join(abilities['abilities'])}. "
        desc += f"Weapons: {', '.join(abilities['weapons'])}. "
        desc += f"Armor: {', '.join(abilities['armor'])}. "
        desc += "Can use magic" if abilities['magic'] else "Cannot use magic"
        return desc
    return player_class

genres = {
    "1": ("Fantasy", [
        "Noble", "Peasant", "Mage", "Knight", "Ranger", "Alchemist", "Thief", "Bard",
        "Cleric", "Druid", "Assassin", "Paladin", "Warlock", "Monk", "Sorcerer",
        "Beastmaster", "Enchanter", "Blacksmith", "Merchant", "Gladiator", "Wizard"
    ]),
    "2": ("Sci-Fi", [
        "Space Marine", "Scientist", "Android", "Pilot", "Engineer", "Alien Diplomat",
        "Space Pirate", "Navigator", "Robot Technician", "Cybernetic Soldier",
        "Explorer", "Astrobiologist", "Quantum Hacker", "Starship Captain",
        "Galactic Trader", "AI Specialist", "Terraformer", "Cyberneticist", "Bounty Hunter"
    ]),
    "3": ("Cyberpunk", [
        "Hacker", "Street Samurai", "Corporate Agent", "Techie", "Rebel Leader",
        "Drone Operator", "Synth Dealer", "Information Courier", "Augmentation Engineer",
        "Black Market Dealer", "Scumbag", "Police", "Cyborg"
    ]),
    "4": ("Post-Apocalyptic", [
        "Survivor", "Scavenger", "Mutant", "Trader", "Raider", "Medic",
        "Cult Leader", "Berserker", "Soldier"
    ]),
    "5": ("Random", [])
}

player_choices_template = {
    "currency": {},
    "allies": [],
    "enemies": [],
    "discoveries": [],
    "reputation": 0,
    "resources": {},
    "factions": defaultdict(int),
    "completed_quests": [],
    "active_quests": [],
    "world_events": [],
    "consequences": [],
    "objects": {}
}

DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master. Your role is to narrate the consequences of player actions. Follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - Describe ONLY the consequences of the player's action
   - Never perform actions on behalf of the player
   - Consequences must permanently change the game world
   - Narrate consequences naturally within the story flow
   - Small actions create ripple effects through the narrative

2. RESPONSE STYLE:
   - Describe what happens in the world as a result of the player's action
   - Do not describe the player performing actions - the player has already stated their action
   - Never use labels like "a)", "b)", "c)" - narrate everything naturally
   - Do not explicitly ask what the player does next

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change permanently based on actions
   - Player choices open/close future narrative paths
   - Resources are gained/lost permanently
   - Player actions can fundamentally alter the story direction
   - Objects can be permanently destroyed, altered, or removed

4. PLAYER AGENCY:
   - Never say "you can't do that" - instead show the consequence of the attempt
   - Allow players to attempt any action, no matter how unexpected
   - If an action seems impossible, narrate why it fails and its consequences
   - Let players break quests, destroy locations, or alter factions

5. MULTIPLE PLAYERS:
   - The party consists of {num_players} adventurers: {player_names}
   - Each adventurer has their own class: {player_classes}
   - They start at: {starting_location}
   - Narrate consequences for the party as a whole, but mention individual actions when appropriate
   - Players take turns acting in this order: {player_names}

6. CLASS RESTRICTIONS:
   - Characters have class-specific abilities and restrictions
   - Enforce weapon, armor, and magic limitations
   - Narrate failures when characters attempt prohibited actions
   - Example: A peasant trying to cast a spell would fail
   - Example: A mage wearing plate armor would be encumbered

7. CURRENCY SYSTEM:
   - The party currency is: {currency_name}
   - Money can be earned through quests, trade, or discovery
   - Money can be spent on items, services, or information
   - The party cannot spend more money than they have

8. TURN-BASED PLAY:
   - Players act in sequence: {player_names}
   - Each player's action affects the world for subsequent players
   - Destroyed objects cannot be interacted with again
   - Changed environments affect all players equally

Example:
Player: "I attack the guard"
DM: "The guard parries your blow and calls for reinforcements. Three more guards appear from around the corner."

Player: "I try to pick the lock"
DM: "After several tense moments, you hear a satisfying click as the lock opens. The door creaks slightly as it swings inward."

Player: "I offer the merchant gold"
DM: "The merchant's eyes light up as he takes your gold. 'This will do nicely,' he says, handing you the artifact."
"""

def get_current_state(player_choices, genre):
    currency_name = CURRENCY_MAP.get(genre, "currency")
    state = [
        f"### Current World State ###",
        f"Currency ({currency_name}):",
    ]
    
    # Add per-player currency
    for player, amount in player_choices['currency'].items():
        state.append(f"  - {player}: {amount}")
    
    state.append(f"Allies: {', '.join(player_choices['allies']) if player_choices['allies'] else 'None'}")
    state.append(f"Enemies: {', '.join(player_choices['enemies']) if player_choices['enemies'] else 'None'}")
    state.append(f"Reputation: {player_choices['reputation']}")
    state.append(f"Active Quests: {', '.join(player_choices['active_quests']) if player_choices['active_quests'] else 'None'}")
    state.append(f"Completed Quests: {', '.join(player_choices['completed_quests']) if player_choices['completed_quests'] else 'None'}")
    
    if player_choices['resources']:
        state.append("Resources:")
        for resource, amount in player_choices['resources'].items():
            state.append(f"  - {resource}: {amount}")
    
    if player_choices['factions']:
        state.append("Faction Relationships:")
        for faction, level in player_choices['factions'].items():
            state.append(f"  - {faction}: {'+' if level > 0 else ''}{level}")
    
    if player_choices['world_events']:
        state.append("Recent World Events:")
        for event in player_choices['world_events'][-3:]:
            state.append(f"  - {event}")
    
    if player_choices['consequences']:
        state.append("Recent Consequences:")
        for cons in player_choices['consequences'][-3:]:
            state.append(f"  - {cons}")
    
    if player_choices['objects']:
        state.append("Object States:")
        for obj, status in player_choices['objects'].items():
            state.append(f"  - {obj}: {status}")
    
    return "\n".join(state)

def get_ai_response(prompt, model=ollama_model):
    try:
        try:
            health_check = requests.get("http://localhost:11434/", timeout=5)
            if health_check.status_code != 200:
                logging.error("Ollama service not running or inaccessible")
                print("Error: Could not connect to Ollama. Make sure it's running.")
                return ""
        except requests.exceptions.ConnectionError:
            logging.error("Ollama service not running or inaccessible")
            print("Error: Could not connect to Ollama. Make sure it's running.")
            return ""
        
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 250,
                    "stop": ["\n\n"],
                    "min_p": 0.05,
                    "top_k": 40
                }
            },
            timeout=60
        )
        response.raise_for_status()
        json_resp = response.json()
        return json_resp.get("response", "").strip()
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
        print("Error: Could not connect to Ollama. Make sure it's running.")
        return ""
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error: {e}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error in get_ai_response: {e}")
        return ""

def speak(text, voice="FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"):
    try:
        if not text.strip():
            return

        payload = {
            "text_input": text,
            "character_voice_gen": voice,
            "narrator_enabled": "true",
            "narrator_voice_gen": "narrator.wav",
            "text_filtering": "none",
            "output_file_name": "output",
            "autoplay": "true",
            "autoplay_volume": "0.8"
        }
        response = requests.post(ALLTALK_API_URL, data=payload, timeout=20)
        response.raise_for_status()

        if response.headers.get("Content-Type", "").startswith("audio/"):
            audio_data = np.frombuffer(response.content, dtype=np.int16)
            sd.play(audio_data, samplerate=22050)
            sd.wait()
        else:
            logging.error(f"Unexpected response content type: {response.headers.get('Content-Type')}")
    except Exception as e:
        logging.error(f"Error in speech generation: {e}")

def show_help():
    print("""
Available commands:
/? or /help       - Show this help message
/redo             - Repeat last AI response with a new generation
/save             - Save the full adventure to adventure.txt
/load             - Load the adventure from adventure.txt
/change           - Switch to a different Ollama model
/count            - Calculate subarrays with at most k distinct elements
/exit             - Exit the game
/consequences     - Show recent consequences of your actions
/state            - Show current world state
/players          - Show current party members

Story Adaptation:
Every action you take will permanently change the story:
  - Killing characters removes them permanently
  - Stealing items adds them to your inventory
  - Choices affect NPC attitudes and world events
  - Environments change based on your actions
  - Resources are permanently gained or lost
  - Objects can be permanently destroyed or altered
  - You can attempt ANY action, no matter how unconventional
  - The story adapts dynamically to your choices
""")

def remove_last_ai_response(conversation):
    pos = conversation.rfind("Dungeon Master:")
    if pos == -1:
        return conversation

    return conversation[:pos].strip()

def sanitize_response(response):
    if not response:
        return "The story continues..."

    question_phrases = [
        r"what will you do", r"how do you respond", r"what do you do",
        r"what is your next move", r"what would you like to do",
        r"what would you like to say", r"how will you proceed",
        r"do you:", r"choose one", r"select an option", r"pick one"
    ]

    for phrase in question_phrases:
        pattern = re.compile(rf'{phrase}.*?$', re.IGNORECASE)
        response = pattern.sub('', response)

    structure_phrases = [
        r"a\)", r"b\)", r"c\)", r"d\)", r"e\)", r"option [a-e]:",
        r"immediate consequence:", r"new situation:", r"next challenges:",
        r"choices:", r"options:"
    ]
    for phrase in structure_phrases:
        pattern = re.compile(phrase, re.IGNORECASE)
        response = pattern.sub('', response)

    player_action_patterns = [
        r"you (?:try to|attempt to|begin to|start to|decide to) .+?\.", 
        r"you (?:successfully|carefully|quickly) .+?\.", 
        r"you (?:manage to|fail to) .+?\."
    ]
    
    for pattern in player_action_patterns:
        response = re.sub(pattern, '', response, flags=re.IGNORECASE)

    response = re.sub(
        r'(?:\n|\. )?[A-Ea-e]\)[^\.\?\!\n]*(\n|\. |$)', 
        '', 
        response,
        flags=re.IGNORECASE
    )
    
    response = re.sub(
        r'(?:something else|other) \(.*?\)', 
        '', 
        response, 
        flags=re.IGNORECASE
    )

    response = re.sub(r'\s{2,}', ' ', response).strip()

    if response and response[-1] not in ('.', '!', '?', ':', ','):
        response += '.'
    
    response = re.sub(r'\[[^\]]*State Tracking[^\]]*\]', '', response)
    
    return response

def validate_purchase(action, genre, player_choices, current_player):
    currency_name = CURRENCY_MAP.get(genre, "currency")
    pattern = r"buy (.+?) for (\d+) (" + re.escape(currency_name) + r")"
    match = re.search(pattern, action, re.IGNORECASE)
    
    if match:
        item = match.group(1)
        amount = int(match.group(2))
        currency = match.group(3)
        
        # Check current player's currency
        if current_player not in player_choices['currency']:
            return False, f"You have no {currency_name}!"
        if player_choices['currency'][current_player] < amount:
            return False, f"You don't have enough {currency_name} for that purchase!"
        return True, None
    
    return True, None

def enforce_class_restrictions(action, player_class, genre):
    if genre in CLASS_ABILITIES and player_class in CLASS_ABILITIES[genre]:
        abilities = CLASS_ABILITIES[genre][player_class]
        
        if not abilities["magic"]:
            magic_keywords = ["cast", "spell", "enchant", "summon", "magic", "ritual"]
            if any(word in action.lower() for word in magic_keywords):
                return False, f"As a {player_class}, you don't have magical abilities!"
            
        weapon_keywords = ["sword", "axe", "mace", "bow", "crossbow", "spear", "rifle", "gun", "blaster"]
        mentioned_weapons = [w for w in weapon_keywords if w in action.lower()]
        allowed_weapons = [w.lower() for w in abilities["weapons"]]
        
        for weapon in mentioned_weapons:
            if weapon not in allowed_weapons:
                return False, f"As a {player_class}, you're not trained with {weapon} weapons!"
                
        armor_keywords = ["plate", "chainmail", "armor", "heavy armor"]
        mentioned_armor = [a for a in armor_keywords if a in action.lower()]
        allowed_armor = [a.lower() for a in abilities["armor"]]
        
        for armor in mentioned_armor:
            if armor not in allowed_armor:
                return False, f"As a {player_class}, you can't wear {armor}!"
    
    return True, None

def update_world_state(action, response, player_choices, genre, current_player):
    currency_name = CURRENCY_MAP.get(genre, "currency")
    
    player_choices['consequences'].append(f"{current_player} '{action}': {response}")
    
    if len(player_choices['consequences']) > 5:
        player_choices['consequences'] = player_choices['consequences'][-5:]
    
    ally_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:joins|helps|saves|allies with|becomes your ally|supports you)',
        response, 
        re.IGNORECASE
    )
    for ally in ally_matches:
        if ally not in player_choices['allies']:
            player_choices['allies'].append(ally)
            if ally in player_choices['enemies']:
                player_choices['enemies'].remove(ally)
    
    enemy_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:dies|killed|falls|perishes|becomes your enemy|turns against you|hates you)',
        response, 
        re.IGNORECASE
    )
    for enemy in enemy_matches:
        if enemy not in player_choices['enemies']:
            player_choices['enemies'].append(enemy)
        if enemy in player_choices['allies']:
            player_choices['allies'].remove(enemy)
    
    resource_matches = re.findall(
        r'(?:get|find|acquire|obtain|receive|gain|steal|take) (\d+) (\w+)',
        response, 
        re.IGNORECASE
    )
    for amount, resource in resource_matches:
        resource = resource.lower()
        player_choices['resources'].setdefault(resource, 0)
        player_choices['resources'][resource] += int(amount)
    
    lost_matches = re.findall(
        r'(?:lose|drop|spend|use|expend|give|donate|surrender) (\d+) (\w+)',
        response, 
        re.IGNORECASE
    )
    for amount, resource in lost_matches:
        resource = resource.lower()
        if resource in player_choices['resources']:
            player_choices['resources'][resource] = max(0, player_choices['resources'][resource] - int(amount))

    gain_matches = re.findall(
        r'(?:find|earn|receive|get|acquire|obtain|gain|steal|take) (\d+) ' + re.escape(currency_name),
        response, 
        re.IGNORECASE
    )
    for amount in gain_matches:
        if current_player in player_choices['currency']:
            player_choices['currency'][current_player] += int(amount)
    
    loss_matches = re.findall(
        r'(?:spend|pay|lose|drop|use|expend|give|donate|surrender) (\d+) ' + re.escape(currency_name),
        response, 
        re.IGNORECASE
    )
    for amount in loss_matches:
        if current_player in player_choices['currency']:
            player_choices['currency'][current_player] = max(0, player_choices['currency'][current_player] - int(amount))
    
    # Improved pattern for multi-word locations
    world_event_matches = re.findall(
        r'(?:The|A|An) ([A-Za-z\s]+) (?:is|has been|becomes) (destroyed|created|changed|revealed|altered|ruined|rebuilt)',
        response, 
        re.IGNORECASE
    )
    for location, event in world_event_matches:
        player_choices['world_events'].append(f"{location.strip()} {event}")
    
    # Improved quest detection patterns
    if "quest completed" in response.lower() or "completed the quest" in response.lower():
        quest_match = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been)? completed', response, re.IGNORECASE)
        if quest_match:
            quest_name = quest_match.group(1).strip()
            if quest_name in player_choices['active_quests']:
                player_choices['active_quests'].remove(quest_name)
                player_choices['completed_quests'].append(quest_name)
    
    if "new quest" in response.lower() or "quest started" in response.lower() or "quest given" in response.lower():
        quest_match = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been)? (?:given|started)', response, re.IGNORECASE)
        if quest_match:
            quest_name = quest_match.group(1).strip()
            if quest_name not in player_choices['active_quests'] and quest_name not in player_choices['completed_quests']:
                player_choices['active_quests'].append(quest_name)
    
    if "reputation increases" in response.lower() or "reputation improved" in response.lower():
        player_choices['reputation'] += 1
    elif "reputation decreases" in response.lower() or "reputation damaged" in response.lower():
        player_choices['reputation'] = max(-5, player_choices['reputation'] - 1)
    
    faction_matches = re.findall(
        r'(?:The|Your) (\w+) faction (?:likes|respects|trusts|appreciates) you more', 
        response, 
        re.IGNORECASE
    )
    for faction in faction_matches:
        player_choices['factions'][faction] += 1
    
    faction_loss_matches = re.findall(
        r'(?:The|Your) (\w+) faction (?:dislikes|distrusts|hates|condemns) you more', 
        response, 
        re.IGNORECASE
    )
    for faction in faction_loss_matches:
        player_choices['factions'][faction] -= 1
        
    discovery_matches = re.findall(
        r'(?:discover|find|uncover|learn about|reveal) (?:a |an |the )?(.+?)\.', 
        response, 
        re.IGNORECASE
    )
    for discovery in discovery_matches:
        if discovery not in player_choices['discoveries']:
            player_choices['discoveries'].append(discovery)
    
    # Improved patterns for multi-word objects
    destroyed_matches = re.findall(
        r'(?:destroy|break|smash) (?:the |a |an )?([\w\s]+)', 
        action, 
        re.IGNORECASE
    )
    for obj in destroyed_matches:
        player_choices['objects'][obj.strip()] = "destroyed"
    
    taken_matches = re.findall(
        r'(?:take|steal|grab|pick up) (?:the |a |an )?([\w\s]+)', 
        action, 
        re.IGNORECASE
    )
    for obj in taken_matches:
        player_choices['objects'][obj.strip()] = "taken"

def get_round_summary(conversation, player_choices, genre, starting_location, party):
    """Generate a summary of the round's actions and progress the story"""
    currency_name = CURRENCY_MAP.get(genre, "currency")
    player_names = [name for name, _ in party]
    player_classes = [pc for _, pc in party]
    
    summary_prompt = (
        f"{DM_SYSTEM_PROMPT.format(num_players=len(party), player_names=', '.join(player_names), player_classes=', '.join(player_classes), starting_location=starting_location, currency_name=currency_name)}\n\n"
        f"### Current World State ###\n{get_current_state(player_choices, genre)}\n\n"
        f"{conversation}\n"
        f"### Additional Instruction ###\n"
        f"The party has completed a full round of actions. As the Dungeon Master, summarize the consequences of their choices and progress the story naturally to the next significant event or challenge.\n"
        f"Dungeon Master:"
    )
    
    return get_ai_response(summary_prompt)

def main():
    global ollama_model
    last_ai_reply = ""
    conversation = ""
    adventure_started = False
    last_player_input = ""
    current_player_index = 0
    last_player_name = None
    round_count = 0  # Track rounds for DM narration
    
    party = []
    num_players = 0
    selected_genre = ""
    starting_location = ""

    player_choices = {
        "currency": {},
        "allies": [],
        "enemies": [],
        "discoveries": [],
        "reputation": 0,
        "resources": {},
        "factions": defaultdict(int),
        "completed_quests": [],
        "active_quests": [],
        "world_events": [],
        "consequences": [],
        "objects": {}
    }

    if os.path.exists("adventure.txt"):
        print("A saved adventure exists. Load it now? (y/n)")
        if input().strip().lower() == "y":
            try:
                with open("adventure.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "### Party Information ###" in content:
                    party_section = content.split("### Party Information ###")[1]
                    party_section = party_section.split("### Persistent World State ###")[0].strip()
                    
                    genre_match = re.search(r"Genre: (.+)", party_section)
                    if genre_match:
                        selected_genre = genre_match.group(1).strip()
                    
                    loc_match = re.search(r"Starting Location: (.+)", party_section)
                    if loc_match:
                        starting_location = loc_match.group(1).strip()
                    
                    player_lines = [line.strip() for line in party_section.splitlines() if line.startswith("- ")]
                    party = []
                    for line in player_lines:
                        match = re.match(r"- (.+?) \((.+?)\)", line)
                        if match:
                            name = match.group(1).strip()
                            player_class = match.group(2).strip()
                            party.append((name, player_class))
                    
                    num_players = len(party)
                
                conversation = content.split("### Persistent World State ###")[0].strip()
                
                print("Adventure loaded.\n")
                last_dm_pos = conversation.rfind("Dungeon Master:")
                if last_dm_pos != -1:
                    reply = conversation[last_dm_pos + len("Dungeon Master:"):].strip()
                    print(f"Dungeon Master: {reply}")
                    speak(reply)
                    last_ai_reply = reply
                    adventure_started = True
                    
                    if "### Persistent World State ###" in content:
                        state_section = content.split("### Persistent World State ###")[1]
                        
                        # Improved state parsing
                        if "Currency (" in state_section:
                            currency_section = state_section.split("Currency (")[1]
                            currency_name = currency_section.split("):")[0]
                            currency_lines = currency_section.split("):")[1]
                            currency_pattern = r"- (.+?): (\d+)"
                            currency_matches = re.findall(currency_pattern, currency_lines)
                            for player, amount in currency_matches:
                                player_choices['currency'][player] = int(amount)
                            
                        if "Allies:" in state_section:
                            allies_line = state_section.split("Allies:")[1].split("\n")[0].strip()
                            if allies_line != "None":
                                player_choices['allies'] = [a.strip() for a in allies_line.split(",")]
                        
                        if "Enemies:" in state_section:
                            enemies_line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                            if enemies_line != "None":
                                player_choices['enemies'] = [e.strip() for e in enemies_line.split(",")]
                        
                        if "Resources:" in state_section:
                            resources_section = state_section.split("Resources:")[1]
                            if "Faction Relationships:" in resources_section:
                                resources_section = resources_section.split("Faction Relationships:")[0]
                            resource_pattern = r"- (.+?): (\d+)"
                            resource_matches = re.findall(resource_pattern, resources_section)
                            for resource, amount in resource_matches:
                                player_choices['resources'][resource.strip()] = int(amount)
                        
                        if "Consequences:" in state_section:
                            cons_section = state_section.split("Consequences:")[1]
                            if "Object States:" in cons_section:
                                cons_section = cons_section.split("Object States:")[0]
                            cons_pattern = r"- (.+)"
                            cons_matches = re.findall(cons_pattern, cons_section)
                            for cons in cons_matches:
                                player_choices['consequences'].append(cons.strip())
                        
                        if "Object States:" in state_section:
                            obj_section = state_section.split("Object States:")[1]
                            obj_pattern = r"- (.+?): (.+)"
                            obj_matches = re.findall(obj_pattern, obj_section)
                            for obj, status in obj_matches:
                                player_choices['objects'][obj.strip()] = status.strip()
            except Exception as e:
                logging.error(f"Error loading adventure: {e}")
                print("Error loading adventure. Details logged.")

    if not adventure_started:
        while True:
            try:
                num_players = int(input("How many players are there? (2-5): ").strip())
                if 2 <= num_players <= 5:
                    break
                print("Please enter a number between 2 and 5")
            except ValueError:
                print("Invalid input. Please enter a number.")

        print("\nChoose your adventure genre:")
        for key, (g, _) in genres.items():
            print(f"{key}: {g}")
        while True:
            gc = input("Enter the number of your choice: ").strip()
            if gc in genres:
                selected_genre, roles = genres[gc]
                if selected_genre == "Random":
                    available = [v for k, v in genres.items() if k != "5"]
                    selected_genre, roles = random.choice(available)
                break
            print("Invalid selection. Please try again.")

        if not roles:
            for key, (g, rl) in genres.items():
                if g == selected_genre:
                    roles = rl
                    break

        print(f"\nCreating characters for {selected_genre} adventure:")
        player_names = []
        for i in range(1, num_players + 1):
            while True:
                name = input(f"\nEnter name for Player {i}: ").strip()
                if not name:
                    print("Name cannot be empty.")
                    continue
                if name in player_names:
                    print("Name already taken. Please choose a different name.")
                    continue
                player_names.append(name)
                break
                
            print(f"\nAvailable classes for {name}:")
            for idx, r in enumerate(roles, 1):
                desc = get_class_description(selected_genre, r)
                print(f"{idx}: {desc}")
                
            while True:
                choice = input(f"Choose a class for {name}: ").strip()
                if not choice:
                    player_class = random.choice(roles)
                    break
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(roles):
                        player_class = roles[idx]
                        break
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            party.append((name, player_class))
            print(f"{name} the {player_class} created!")
        
        # Initialize per-player currency
        for name, player_class in party:
            start_currency = CLASS_STARTING_CURRENCY.get(selected_genre, {}).get(player_class, 10)
            player_choices['currency'][name] = start_currency
        
        locations = GENRE_LOCATIONS.get(selected_genre, [])
        if not locations:
            # Create 25 generic locations if none defined
            locations = [f"Location {i}" for i in range(1, 26)]
            
        print("\nChoose a starting location:")
        for idx, loc in enumerate(locations, 1):
            print(f"{idx}: {loc}")
            
        while True:
            choice = input(f"Enter location number (1-{len(locations)}): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(locations):
                    starting_location = locations[idx]
                    break
            print(f"Invalid choice. Please enter a number between 1 and {len(locations)}.")
        
        starter = get_role_starter(selected_genre, "any")
        starting_scenario = f"{starter} at {starting_location}."
        
        print(f"\n--- Adventure Start: The {selected_genre} Party ---")
        print(f"Party members:")
        for name, player_class in party:
            print(f"  - {name} the {player_class}")
        print(f"Starting location: {starting_location}")
        print(f"Starting scenario: {starting_scenario}")
        print("Type '/?' or '/help' for commands.\n")

        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Starting Location: {starting_location}\n"
            f"Starting Scenario: {starting_scenario}\n"
        )
        
        player_names = [name for name, _ in party]
        player_classes = [player_class for _, player_class in party]
        currency_name = CURRENCY_MAP.get(selected_genre, "currency")
        dm_system_prompt = DM_SYSTEM_PROMPT.format(
            num_players=num_players,
            player_names=", ".join(player_names),
            player_classes=", ".join(player_classes),
            starting_location=starting_location,
            currency_name=currency_name
        )
        
        conversation = dm_system_prompt + "\n\n" + initial_context + "\n\nDungeon Master: "

        ai_reply = get_ai_response(conversation)
        if ai_reply:
            ai_reply = sanitize_response(ai_reply)
            print(f"Dungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += ai_reply
            last_ai_reply = ai_reply
            
            player_choices['consequences'].append(f"Start: {ai_reply.split('.')[0]}")
            
            adventure_started = True

    while adventure_started:
        try:
            current_player_name, current_player_class = party[current_player_index]
            
            user_input = input(f"\n{current_player_name}> ").strip()
            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ["/?", "/help"]:
                show_help()
                continue

            if cmd == "/exit":
                print("Exiting the adventure. Goodbye!")
                break
                    
            if cmd == "/consequences":
                print("\nRecent Consequences of Your Actions:")
                if player_choices['consequences']:
                    for i, cons in enumerate(player_choices['consequences'][-5:], 1):
                        print(f"{i}. {cons}")
                else:
                    print("No consequences recorded yet.")
                continue
                    
            if cmd == "/state":
                print("\nCurrent World State:")
                print(get_current_state(player_choices, selected_genre))
                continue
                
            if cmd == "/players":
                print("\nParty Members:")
                for i, (name, player_class) in enumerate(party, 1):
                    print(f"{i}. {name} the {player_class}")
                continue

            if cmd == "/redo":
                if last_ai_reply and last_player_input and last_player_name:
                    original_length = len(conversation)
                    
                    conversation = remove_last_ai_response(conversation)
                    
                    state_context = get_current_state(player_choices, selected_genre)
                    currency_name = CURRENCY_MAP.get(selected_genre, "currency")
                    full_conversation = (
                        f"{DM_SYSTEM_PROMPT.format(num_players=num_players, player_names=', '.join([name for name, _ in party]), player_classes=', '.join([pc for _, pc in party]), starting_location=starting_location, currency_name=currency_name)}\n\n"
                        f"### Current World State ###\n{state_context}\n\n"
                        f"{conversation}\n"
                        f"Player: {last_player_name}: {last_player_input}\n"
                        "Dungeon Master:"
                    )
                    
                    ai_reply = get_ai_response(full_conversation)
                    if ai_reply:
                        ai_reply = sanitize_response(ai_reply)
                        print(f"\nDungeon Master: {ai_reply}")
                        speak(ai_reply)
                        
                        conversation += f"\nPlayer: {last_player_name}: {last_player_input}\nDungeon Master: {ai_reply}"
                        last_ai_reply = ai_reply
                        
                        update_world_state(last_player_input, ai_reply, player_choices, selected_genre, last_player_name)
                    else:
                        conversation = conversation[:original_length]
                else:
                    print("Nothing to redo.")
                continue

            if cmd == "/save":
                try:
                    with open("adventure.txt", "w", encoding="utf-8") as f:
                        f.write(conversation)
                        f.write("\n\n### Party Information ###\n")
                        f.write(f"Genre: {selected_genre}\n")
                        f.write(f"Starting Location: {starting_location}\n")
                        for name, player_class in party:
                            f.write(f"- {name} ({player_class})\n")
                        f.write("\n### Persistent World State ###\n")
                        f.write(get_current_state(player_choices, selected_genre))
                    print("Adventure saved to adventure.txt")
                except Exception as e:
                    logging.error(f"Error saving adventure: {e}")
                    print("Error saving adventure. Details logged.")
                continue

            if cmd == "/load":
                if os.path.exists("adventure.txt"):
                    try:
                        with open("adventure.txt", "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        if "### Party Information ###" in content:
                            party_section = content.split("### Party Information ###")[1]
                            party_section = party_section.split("### Persistent World State ###")[0].strip()
                            
                            genre_match = re.search(r"Genre: (.+)", party_section)
                            if genre_match:
                                selected_genre = genre_match.group(1).strip()
                            
                            loc_match = re.search(r"Starting Location: (.+)", party_section)
                            if loc_match:
                                starting_location = loc_match.group(1).strip()
                            
                            player_lines = [line.strip() for line in party_section.splitlines() if line.startswith("- ")]
                            party = []
                            for line in player_lines:
                                match = re.match(r"- (.+?) \((.+?)\)", line)
                                if match:
                                    name = match.group(1).strip()
                                    player_class = match.group(2).strip()
                                    party.append((name, player_class))
                            
                            num_players = len(party)
                        
                        conversation = content.split("### Persistent World State ###")[0].strip()
                        print("Adventure loaded.")
                        last_dm_pos = conversation.rfind("Dungeon Master:")
                        if last_dm_pos != -1:
                            last_ai_reply = conversation[last_dm_pos + len("Dungeon Master:"):].strip()
                        
                        if "### Persistent World State ###" in content:
                            state_section = content.split("### Persistent World State ###")[1]
                            
                            # Improved state parsing
                            if "Currency (" in state_section:
                                currency_section = state_section.split("Currency (")[1]
                                currency_name = currency_section.split("):")[0]
                                currency_lines = currency_section.split("):")[1]
                                currency_pattern = r"- (.+?): (\d+)"
                                currency_matches = re.findall(currency_pattern, currency_lines)
                                for player, amount in currency_matches:
                                    player_choices['currency'][player] = int(amount)
                                
                            if "Allies:" in state_section:
                                allies_line = state_section.split("Allies:")[1].split("\n")[0].strip()
                                if allies_line != "None":
                                    player_choices['allies'] = [a.strip() for a in allies_line.split(",")]
                            
                            if "Enemies:" in state_section:
                                enemies_line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                                if enemies_line != "None":
                                    player_choices['enemies'] = [e.strip() for e in enemies_line.split(",")]
                            
                            if "Resources:" in state_section:
                                resources_section = state_section.split("Resources:")[1]
                                if "Faction Relationships:" in resources_section:
                                    resources_section = resources_section.split("Faction Relationships:")[0]
                                resource_pattern = r"- (.+?): (\d+)"
                                resource_matches = re.findall(resource_pattern, resources_section)
                                for resource, amount in resource_matches:
                                    player_choices['resources'][resource.strip()] = int(amount)
                            
                            if "Consequences:" in state_section:
                                cons_section = state_section.split("Consequences:")[1]
                                if "Object States:" in cons_section:
                                    cons_section = cons_section.split("Object States:")[0]
                                cons_pattern = r"- (.+)"
                                cons_matches = re.findall(cons_pattern, cons_section)
                                for cons in cons_matches:
                                    player_choices['consequences'].append(cons.strip())
                            
                            if "Object States:" in state_section:
                                obj_section = state_section.split("Object States:")[1]
                                obj_pattern = r"- (.+?): (.+)"
                                obj_matches = re.findall(obj_pattern, obj_section)
                                for obj, status in obj_matches:
                                    player_choices['objects'][obj.strip()] = status.strip()
                    except Exception as e:
                        logging.error(f"Error loading adventure: {e}")
                        print("Error loading adventure. Details logged.")
                else:
                    print("No saved adventure found.")
                continue

            if cmd == "/change":
                installed_models = get_installed_models()
                if installed_models:
                    print("Available models:")
                    for idx, m in enumerate(installed_models, 1):
                        print(f"{idx}: {m}")
                    while True:
                        choice = input("Enter number of new model: ").strip()
                        if not choice:
                            break
                        try:
                            idx = int(choice) - 1
                            if 0 <= idx < len(installed_models):
                                ollama_model = installed_models[idx]
                                print(f"Model changed to: {ollama_model}")
                                break
                        except ValueError:
                            pass
                        print("Invalid selection. Please try again.")
                else:
                    print("No installed models found. Using current model.")
                continue

            if cmd == "/count":
                try:
                    arr_input = input("Enter integers separated by spaces: ").strip()
                    k_input = input("Enter k value: ").strip()

                    arr = list(map(int, arr_input.split()))
                    k = int(k_input)

                    result = count_subarrays(arr, k)
                    print(f"Number of subarrays with at most {k} distinct elements: {result}")
                except Exception as e:
                    print(f"Error: {e}. Please enter valid integers.")
                continue

            valid, error_msg = validate_purchase(user_input, selected_genre, player_choices, current_player_name)
            if not valid:
                print(f"Dungeon Master: {error_msg}")
                continue
                
            valid, error_msg = enforce_class_restrictions(user_input, current_player_class, selected_genre)
            if not valid:
                print(f"Dungeon Master: {error_msg}")
                continue

            formatted_input = f"{current_player_name}: {user_input}"
            last_player_input = user_input
            last_player_name = current_player_name
            
            state_context = get_current_state(player_choices, selected_genre)
            currency_name = CURRENCY_MAP.get(selected_genre, "currency")
            full_conversation = (
                f"{DM_SYSTEM_PROMPT.format(num_players=num_players, player_names=', '.join([name for name, _ in party]), player_classes=', '.join([pc for _, pc in party]), starting_location=starting_location, currency_name=currency_name)}\n\n"
                f"### Current World State ###\n{state_context}\n\n"
                f"{conversation}\n"
                f"{formatted_input}\n"
                "Dungeon Master:"
            )
            
            ai_reply = get_ai_response(full_conversation)
            
            if ai_reply:
                ai_reply = sanitize_response(ai_reply)
                print(f"\nDungeon Master: {ai_reply}")
                speak(ai_reply)
                
                conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
                last_ai_reply = ai_reply
                
                update_world_state(user_input, ai_reply, player_choices, selected_genre, current_player_name)
                
                # Move to next player
                current_player_index = (current_player_index + 1) % num_players
                
                # After all players have taken a turn, add DM narration
                if current_player_index == 0:
                    round_count += 1
                    print(f"\n--- Round {round_count} Complete ---")
                    
                    # Generate DM narration for the round
                    round_summary = get_round_summary(
                        conversation, 
                        player_choices, 
                        selected_genre, 
                        starting_location, 
                        party
                    )
                    
                    if round_summary:
                        round_summary = sanitize_response(round_summary)
                        print(f"\nDungeon Master (Round Summary): {round_summary}")
                        speak(round_summary)
                        
                        # Update conversation and world state
                        conversation += f"\nDungeon Master (Round Summary): {round_summary}"
                        update_world_state(
                            "Round Summary", 
                            round_summary, 
                            player_choices, 
                            selected_genre, 
                            "System"
                        )

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            print("An unexpected error occurred. The adventure continues...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        print("A critical error occurred. Please check the log file for details.")