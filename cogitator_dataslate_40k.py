#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEXICANUM COGITATOR // MK.IX DATASLATE (Standalone Python Desktop Application)
Warhammer 40,000 Worldbuilding Organizer & Scriptorium Writing Suite

Zero external dependencies required — runs natively on Python 3 using standard
library `tkinter`, `json`, `os`, `sys`, and `pathlib`.

Features:
- True native OS desktop window (no browser tab required).
- Automatic Local Hard-Drive Persistence (`cogitator_databanks_40k.json` saved
  automatically alongside this script on every edit and when closing the window).
- Exact Session Place Restoration: Reopens to the exact Project, Workspace Mode,
  Category Filter, Dossier/Scene, Pinned Reference Slate, and text cursor position.
- 5 Structured 40K Worldbuilding Categories:
    I.   Factions & Warbands
    II.  Worlds & Astrography
    III. Dramatis Personae (Characters)
    IV.  Wargear, Relics & Voidships
    V.   Creed, Lore & Inquisitorial Dossiers
- Side-by-Side Pinned Reference Slate + Persistent Vox-Scratchpad while writing.
- Interactive Hololithic Sub-Sector Map (Canvas with draggable planetary nodes).
- Imperial Dating System Calculator (`Check.Fraction.Year.Mxx`) & Chronology.
- Lexmechanic Lore & Name Forge (High/Low Gothic, Voidships, Worlds, Epigraphs).
- One-Click "Create Desktop Icon Shortcut" built right into the top hardware bar.
"""

import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    TK_AVAILABLE = True
except ImportError:
    tk = None
    filedialog = messagebox = ttk = None
    TK_AVAILABLE = False

# =============================================================================
# 1. COLOR THEMES (40K DATA-SLATE PHOSPHOR PALETTES)
# =============================================================================
THEMES = {
    "AUSPEX GREEN": {
        "bg_void": "#070b09",
        "bg_panel": "#0d1512",
        "bg_card": "#13201b",
        "bg_input": "#090f0d",
        "border_dim": "#1f382e",
        "accent_main": "#10b981",
        "accent_bright": "#6ee7b7",
        "brass": "#d97706",
        "brass_bright": "#fbbf24",
        "text_main": "#e2f1eb",
        "text_muted": "#7aa392",
        "danger": "#ef4444",
    },
    "INQUISITOR AMBER": {
        "bg_void": "#0b0806",
        "bg_panel": "#15100b",
        "bg_card": "#1f1710",
        "bg_input": "#0e0a07",
        "border_dim": "#3d2c1d",
        "accent_main": "#f59e0b",
        "accent_bright": "#fcd34d",
        "brass": "#d97706",
        "brass_bright": "#fde68a",
        "text_main": "#fef3c7",
        "text_muted": "#b49264",
        "danger": "#ef4444",
    },
    "MARS CRIMSON": {
        "bg_void": "#0a0607",
        "bg_panel": "#160b0e",
        "bg_card": "#211115",
        "bg_input": "#0d0608",
        "border_dim": "#421d25",
        "accent_main": "#e11d48",
        "accent_bright": "#fda4af",
        "brass": "#c89d54",
        "brass_bright": "#fcd34d",
        "text_main": "#ffe4e6",
        "text_muted": "#b57c86",
        "danger": "#f87171",
    },
    "ADMINISTRATUM SLATE": {
        "bg_void": "#0c0e12",
        "bg_panel": "#13171f",
        "bg_card": "#1b222d",
        "bg_input": "#0e1117",
        "border_dim": "#2d3748",
        "accent_main": "#eab308",
        "accent_bright": "#fde047",
        "brass": "#caa458",
        "brass_bright": "#fef08a",
        "text_main": "#f1f5f9",
        "text_muted": "#94a3b8",
        "danger": "#ef4444",
    },
}

ALLEGIANCES = [
    "ALL",
    "IMPERIUM",
    "CHAOS",
    "AELDARI",
    "NECRONS",
    "ORKS",
    "TAU",
    "TYRANIDS",
    "UNALIGNED",
]

CLEARANCES = [
    "VERMILION",
    "MAGENTA",
    "OBSIDIAN",
    "EXTERMINATUS",
    "SANCTIONED",
]

# =============================================================================
# 2. ORGANIZATIONAL WORLDBUILDING SCHEMA
# =============================================================================
CATEGORY_SCHEMA = {
    "factions": {
        "id": "factions",
        "label": "I. Factions & Warbands",
        "short": "FACTIONS",
        "fields": [
            ("subType", "Force Classification"),
            ("founding", "Founding / Origin Era"),
            ("homeworld", "Homeworld / Base of Ops"),
            ("geneSeedOrCreed", "Progenitor Gene-Seed / Creed"),
            ("heraldry", "Heraldry & Colors"),
            ("battleCry", "Battle Cry / War Litany"),
        ],
        "compartments": [
            ("sec1", "1. Identity, Origins & Founding Myth"),
            ("sec2", "2. Command Structure, Culture & Rituals"),
            ("sec3", "3. Combat Doctrine, Strengths & Fleet Assets"),
            ("sec4", "4. Flaws, Schisms & Inquisitorial Secrets"),
        ],
    },
    "worlds": {
        "id": "worlds",
        "label": "II. Worlds & Astrography",
        "short": "WORLDS",
        "fields": [
            ("planetClass", "Administratum Class"),
            ("segmentum", "Segmentum & Sub-Sector"),
            ("titheGrade", "Tithe Grade"),
            ("population", "Population & Primary Hive"),
            ("ruler", "Planetary Governor / Ruler"),
            ("warpStability", "Warp Route & Mandeville Status"),
        ],
        "compartments": [
            ("sec1", "1. Biosphere, Sky & Sensory Atmosphere"),
            ("sec2", "2. Key Locations, Spires & Underhive"),
            ("sec3", "3. Tithe Economy, Politics & Noble Houses"),
            ("sec4", "4. Active Warzones, Cults & Plot Hooks"),
        ],
    },
    "characters": {
        "id": "characters",
        "label": "III. Dramatis Personae",
        "short": "PERSONAE",
        "fields": [
            ("rankTitle", "Rank / Honorific Title"),
            ("affiliation", "Primary Faction / Retinue"),
            ("narrativeRole", "Role in Narrative"),
            ("augmeticsPsy", "Augmetics & Psychic Rating"),
            ("loadout", "Signature Wargear & Relics"),
            ("voiceStyle", "Speech Cadence & Mannerisms"),
        ],
        "compartments": [
            ("sec1", "1. Physical Presence, Scars & Augmetics"),
            ("sec2", "2. Psychology, Conviction & Dialogue Voice"),
            ("sec3", "3. Service Record, Past Campaigns & Ghosts"),
            ("sec4", "4. Story Goal, Moral Line & Dark Secret"),
        ],
    },
    "wargear": {
        "id": "wargear",
        "label": "IV. Wargear, Relics & Ships",
        "short": "WARGEAR/SHIPS",
        "fields": [
            ("assetClass", "Asset Classification"),
            ("forgeOrigin", "Forge World / Shipyard Origin"),
            ("patternMark", "Pattern / Hull Mark"),
            ("machineSpirit", "Machine Spirit Temperament"),
            ("custodian", "Current Wielder / Captain"),
            ("powerRating", "Destructive Yield / Rarity"),
        ],
        "compartments": [
            ("sec1", "1. Visual Aesthetics, Runes & Sensory Cues"),
            ("sec2", "2. Combat Capabilities & Tactical Edge"),
            ("sec3", "3. Machine Spirit Quirks & Maintenance Rites"),
            ("sec4", "4. Provenance, Bloodline & Narrative Role"),
        ],
    },
    "lore": {
        "id": "lore",
        "label": "V. Creed, Lore & Dossiers",
        "short": "LORE/CREED",
        "fields": [
            ("dossierType", "Dossier Classification"),
            ("inquisitorialOrdo", "Reviewing Ordo / Authority"),
            ("authorSource", "In-Universe Chronicler / Source"),
            ("dateLogged", "Imperial Date Logged"),
            ("veracity", "Veracity & Censorship Status"),
            ("associatedWorld", "Primary Locus / World"),
        ],
        "compartments": [
            ("sec1", "1. Public Dogma vs. Imperial Propaganda"),
            ("sec2", "2. The Unvarnished Grimdark Truth"),
            ("sec3", "3. Rituals, Cultural Habits & Lexicon"),
            ("sec4", "4. Mystery Clues & Reveals for the Reader"),
        ],
    },
}

FORGE_TABLES = {
    "highGothic": {
        "title": "High Gothic / Astartes / Noble Names",
        "category": "characters",
        "first": [
            "Malakor", "Thalassa", "Cassian", "Vespera", "Severin", "Valerius",
            "Octavia", "Tiberon", "Kaelen", "Mordecai", "Aurelia", "Dravok",
            "Corvin", "Isolde", "Helbrecht", "Cyprian",
        ],
        "second": [
            "Venn", "Vane", "Thorne", "Kravon", "Valtier", "Solyaris", "Morn",
            "Volkov", "Harkon", "Castell", "Drazen", "Voss", "Antioch", "Krieg",
        ],
        "epithet": [
            "the Unforged", "of the Iron Chalice", "Lord-Vigilant",
            "Preceptor-Prime", "Warden of the Breach", "Oath-Keeper",
            "Voice of Mars", "the Ash-Crowned",
        ],
    },
    "lowGothic": {
        "title": "Low Gothic / Guard / Underhive Operatives",
        "category": "characters",
        "first": [
            "Garrick", "Sael", "Jex", "Kora", "Bram", "Tarn", "Nyx", "Dax",
            "Rooks", "Hester", "Varn", "Zira", "Cobb", "Mire",
        ],
        "second": [
            '"Cinder-Lung"', '"Dead-Eye"', '"Fuse"', '"Sump-Dog"', '"Ratchet"',
            '"Six-Las"', '"Trench"', '"Ash-Born"', '"Spire-Fall"', '"Vox"',
        ],
        "epithet": [
            "412th Voltigeurs", "Sump-Sector 9 Scav", "Corp-Grinder Veteran",
            "Munitorum Gunner", "Inquisitorial Acolyte", "Void-Born Bosun",
        ],
    },
    "voidships": {
        "title": "Voidships, Strike Cruisers & Relics",
        "category": "wargear",
        "first": [
            "Litany of", "Spear of", "His Wrathful", "Covenant of", "Iron",
            "Obsidian", "Relentless", "Sovereign of", "Weeping", "Eternal",
        ],
        "second": [
            "Penance", "Absolution", "Verdict", "Nocturne", "Sacrament",
            "Vengeance", "Ashes", "Martyrdom", "Calvary", "Tribunal",
        ],
        "epithet": [
            "Lunar-Class Cruiser", "Dauntless Light Cruiser",
            "Astartes Strike Cruiser", "Dictator-Class Carrier",
            "Cobra Destroyer", "Master-Crafted Relic Blade",
        ],
    },
    "worlds": {
        "title": "Worlds, Hives & Warzone Theatres",
        "category": "worlds",
        "first": [
            "Veridian", "Kravon", "Tartarus", "Stygia", "Golgotha", "Valkyr",
            "Cinder", "Mordian", "Acheron", "Solstice", "Kharon", "Basilica",
        ],
        "second": [
            "IV", "Prime", "Minoris", "Secundus", "IX", "Spire", "Reach",
            "Purgatory", "Crucible", "Gate",
        ],
        "epithet": [
            "Sulfur Hive World", "Quarantined Forge-Moon", "Orbital Bastion",
            "Cathedral Shrine World", "Rad-Scoured Mining World",
            "Promethium Refinery Hub",
        ],
    },
    "factions": {
        "title": "Custom Factions, Chapters & Warbands",
        "category": "factions",
        "first": [
            "Order of the", "Sons of the", "Blades of", "Brotherhood of",
            "Choir of the", "Covenant of", "Wardens of the", "Disciples of",
        ],
        "second": [
            "Ashen Chalice", "Rusted Cog", "Iron Thorn", "Crimson Vigil",
            "Shattered Aquila", "Obsidian Pyre", "Weeping Star", "Silent Anvil",
        ],
        "epithet": [
            "Ultima Founding Chapter", "Order Militant", "Siege Regiment",
            "Heretek Scrap-Cult", "Rogue Trader Dynasty", "Inquisitorial Cabal",
        ],
    },
    "epigraphs": {
        "title": "Inquisitorial Epigraphs & Thoughts for the Day",
        "category": "lore",
        "quotes": [
            '"++ Thought for the Day: An open mind is like a fortress with its gates unbarred and unguarded. ++"',
            '"Mercy is an accounting error corrected by the Commissariat." — Regimental Tactica, Vol. IX',
            '"We do not ask if the machine spirit is willing; we anoint the gears in blood until it obeys." — Magos Dominus Septimus-9',
            '"There are no innocents in the underhive—only subjects we have not yet had time to interrogate." — Lord Inquisitor Venn',
            '"When the stars bleed emerald, lock the Gellar dampers and shoot anyone who claims they hear singing." — Void-Farer\'s Maxim',
            '"A lasgun cell holds sixty shots. Save the fifty-ninth for the heretic and the sixtieth for yourself." — 412th Veridian Trench Cant',
            '"History in the Imperium is not written by the victors; it is redacted by the survivors."',
        ],
    },
}


# =============================================================================
# 3. DEFAULT STARTER DATA (SUB-SECTOR ACHILUS)
# =============================================================================
def create_starter_state():
    proj_id = "proj_achilus_40k"
    return {
        "theme": "AUSPEX GREEN",
        "activeProjectId": proj_id,
        "activeMainTab": 0,
        "activeCategoryFilter": "all",
        "activeAllegianceFilter": "ALL",
        "codexSearch": "",
        "selectedEntryId": "ent_faction_ashen",
        "activeSceneId": "scn_ch1",
        "mapSelectedWorldId": "ent_world_veridian",
        "pinnedReferenceIds": [
            "ent_char_vance",
            "ent_world_veridian",
            "ent_faction_ashen",
        ],
        "activeRefId": "ent_char_vance",
        "cursorPositions": {},
        "lastEditedPointer": {
            "type": "codex",
            "id": "ent_faction_ashen",
            "title": "Order of the Ashen Chalice",
            "timestamp": "0.814.999.M41",
        },
        "projects": [
            {
                "id": proj_id,
                "name": "Sub-Sector Achilus: The Ashes of Veridian IV",
                "sector": "Segmentum Obscurus // Achilus Sub-Sector",
                "era": "Era Indomitus • 0.814.999.M41",
                "wordGoal": 15000,
                "description": (
                    "A grimdark novel & worldbuilding bible chronicling the siege of "
                    "Hive World Veridian IV as Warp-storms isolate the sub-sector and "
                    "an ancient Mechanicus data-vault awakens beneath Hive Tartarus."
                ),
                "scratchpad": (
                    "++ CONTINUITY REMINDERS ++\n"
                    "- Low Gothic slang on Veridian IV: 'Cinder-lung' (ash-waste miner), "
                    "'Lumen-tithe' (shift tax), 'Glassed' (orbital lance strike).\n"
                    "- Strike Cruiser 'Litany of Penance' has a damaged starboard plasma "
                    "macro-battery from Act I.\n"
                    "- Inquisitor Venn speaks through a silver vox-augment."
                ),
                "entries": [
                    {
                        "id": "ent_faction_ashen",
                        "category": "factions",
                        "allegiance": "IMPERIUM",
                        "clearance": "VERMILION",
                        "starred": True,
                        "title": "Order of the Ashen Chalice",
                        "subtitle": "Order Militant of the Adepta Sororitas // Wardens of Veridian",
                        "epigraph": (
                            '"We do not pray for deliverance from the fire; we ask only '
                            'that our promethium burns hotter than their heresy." '
                            "— Canoness Preceptor Thalassa Vane"
                        ),
                        "tags": ["Adepta Sororitas", "Imperium", "Veridian IV"],
                        "updatedAt": 1761090000,
                        "coords": {"x": 45, "y": 40},
                        "fields": {
                            "subType": "Adepta Sororitas Order Minoris",
                            "founding": "M38 // Scouring of Saint Sabbat's Reliquary",
                            "homeworld": "Veridian IV — Convent of the Obsidian Basilica",
                            "geneSeedOrCreed": "Lectitio Divinitatus // Purifying Immolation",
                            "heraldry": "Soot-black ceramite, burnished brass trim, crimson robes",
                            "battleCry": '"Drink of the Ash! Burn for the Throne!"',
                        },
                        "compartments": {
                            "sec1": (
                                "Founded in late M38 to guard the bone-crypts of Saint Kaelen "
                                "on [[Hive World Veridian IV]], the Order of the Ashen Chalice "
                                "has spent three millennia policing the Achilus Sub-Sector."
                            ),
                            "sec2": (
                                "Led by [[Canoness Preceptor Thalassa Vane]], the Sisters "
                                "collect ash from burned heretics and mix it with blessed "
                                "unguents to anoint their boltgun casings."
                            ),
                            "sec3": (
                                "Specializes in close-quarters urban purge operations inside "
                                "cramped Hive under-levels using heavy flamers and Immolators."
                            ),
                            "sec4": (
                                "Secretly guards the 'Cinder Vault' beneath the Obsidian "
                                "Basilica—an archeotech chamber sought by [[Lord Inquisitor Malakor Venn]]."
                            ),
                        },
                        "body": (
                            "The Order of the Ashen Chalice stands at a breaking point. "
                            "Reduced to four hundred battle-sisters after the Warp-storm "
                            "Gorgon's Maw cut off reinforcements, [[Canoness Preceptor Thalassa Vane]] "
                            "must decide whether to obey [[Lord Inquisitor Malakor Venn]] "
                            "or hold the promethium viaducts."
                        ),
                    },
                    {
                        "id": "ent_world_veridian",
                        "category": "worlds",
                        "allegiance": "IMPERIUM",
                        "clearance": "MAGENTA",
                        "starred": True,
                        "title": "Hive World Veridian IV",
                        "subtitle": "Primary Munitions & Promethium Hub of the Achilus Sub-Sector",
                        "epigraph": (
                            '"From orbit, Veridian IV looks like an emerald cracked by veins '
                            "of molten brass. On the ground, you realize the green is toxic "
                            'sulfur-fog." — Rogue Trader Cassian Thorne'
                        ),
                        "tags": ["Hive World", "Hive Tartarus", "Siege Theatre"],
                        "updatedAt": 1761089000,
                        "coords": {"x": 48, "y": 52},
                        "fields": {
                            "planetClass": "Industrial Hive World (Class-IV Sulphur Biosphere)",
                            "segmentum": "Segmentum Obscurus // Achilus Sub-Sector",
                            "titheGrade": "Exactis Extremis (Munitorum Shells & Promethium)",
                            "population": "64 Billion across 5 Hive Clusters (Hive Tartarus)",
                            "ruler": "Lord-Governor Hyrcan Vance",
                            "warpStability": "Critical — Warp Rift expanding at Mandeville Point",
                        },
                        "compartments": {
                            "sec1": (
                                "Choked in perpetual yellow-green sulfur clouds. Ash-storms "
                                "scour the equatorial salt flats between hives at 180 kph."
                            ),
                            "sec2": (
                                "- Hive Tartarus: Capital spire housing 19 billion souls.\n"
                                "- The Slag-Trench: 400km open-pit promethium strip-mine.\n"
                                "- Sump-Town Nine: Flooded basin where the [[Choir of the Rusted Cog]] rises."
                            ),
                            "sec3": (
                                "Produces 40% of the heavy artillery shells and plasma flasks "
                                "for the surrounding sub-sector."
                            ),
                            "sec4": (
                                "The underhive manufactorums have begun stamping eight-pointed "
                                "runes inside artillery casings under scrap-code influence."
                            ),
                        },
                        "body": (
                            "[[Hive World Veridian IV]] is the linchpin of the Achilus Sub-Sector. "
                            "If its orbital defense lasers fall to the [[Choir of the Rusted Cog]], "
                            "neighboring worlds will starve of ammunition within a month."
                        ),
                    },
                    {
                        "id": "ent_world_khorvath",
                        "category": "worlds",
                        "allegiance": "IMPERIUM",
                        "clearance": "VERMILION",
                        "starred": False,
                        "title": "Forge-Moon Kravon Minor",
                        "subtitle": "Orbital Mechanicus Foundry & Dockyard of Veridian IV",
                        "epigraph": (
                            '"Flesh tires after sixteen hours on the assembly line. Servitors '
                            'tire only when their bearings melt." — Magos Septimus-9'
                        ),
                        "tags": ["Forge World", "Adeptus Mechanicus", "Shipyard"],
                        "updatedAt": 1761085000,
                        "coords": {"x": 72, "y": 28},
                        "fields": {
                            "planetClass": "Satellite Forge-Moon (Airless / Orbitally Caged)",
                            "segmentum": "Segmentum Obscurus // Veridian System",
                            "titheGrade": "Aptus Non (Adeptus Mechanicus Treaty Exempt)",
                            "population": "1.2 Billion Tech-Thralls, 400,000 Skitarii",
                            "ruler": "Archmagos-Fabricator Septimus-9",
                            "warpStability": "Tethered via grav-anchor corridor to Veridian IV",
                        },
                        "compartments": {
                            "sec1": "Encased in a lattice of rusted iron orbital drydocks and plasma vents.",
                            "sec2": "Home to the Cradle of Mars repair slip refitting [[Strike Cruiser Litany of Penance]].",
                            "sec3": "Trades firearm pattern rights for raw sulfur-ore from [[Hive World Veridian IV]].",
                            "sec4": "Lower noosphere data-stacks are infected by scrap-code from [[World of Malice: Sektoth]].",
                        },
                        "body": "[[Forge-Moon Kravon Minor]] maintains strict quarantine protocols over the system.",
                    },
                    {
                        "id": "ent_world_sektoth",
                        "category": "worlds",
                        "allegiance": "CHAOS",
                        "clearance": "EXTERMINATUS",
                        "starred": False,
                        "title": "World of Malice: Sektoth",
                        "subtitle": "Quarantined Daemon-Touched World on the Sub-Sector Rim",
                        "epigraph": (
                            '"Do not turn your auspex toward the fifth planet. The static '
                            'speaks back in your mother\'s voice." — Void-Watch Order 44'
                        ),
                        "tags": ["Daemon World", "Chaos", "Quarantined"],
                        "updatedAt": 1761082000,
                        "coords": {"x": 22, "y": 76},
                        "fields": {
                            "planetClass": "Quarantined Dead / Daemon-Touched World",
                            "segmentum": "Segmentum Obscurus // Rimward Edge",
                            "titheGrade": "Excommunicate Traitoris",
                            "population": "Unknown (Dark Mechanicum covens & warbands)",
                            "ruler": "Arch-Heretic Vorx the Rust-Tongued",
                            "warpStability": "Submerged inside Gorgon's Maw Warp Anomaly",
                        },
                        "compartments": {
                            "sec1": "Continents of fused black glass and brass bone-spires.",
                            "sec2": "The Screaming Foundry births daemon engines for the [[Choir of the Rusted Cog]].",
                            "sec3": "Sustained by slave-raids and captured Munitorum transports.",
                            "sec4": "Source of the scrap-code transmission corrupting [[Hive World Veridian IV]].",
                        },
                        "body": "Marked for Exterminatus three centuries ago, [[World of Malice: Sektoth]] survived when the fleet vanished.",
                    },
                    {
                        "id": "ent_char_vance",
                        "category": "characters",
                        "allegiance": "IMPERIUM",
                        "clearance": "VERMILION",
                        "starred": True,
                        "title": "Lord Inquisitor Malakor Venn",
                        "subtitle": "Ordo Hereticus // Conclave of the Iron Thorn",
                        "epigraph": '"Mercy is a luxury budgeted by men who have never looked into a Warp-breach."',
                        "tags": ["Inquisitor", "Ordo Hereticus", "POV Character"],
                        "updatedAt": 1761091000,
                        "coords": {"x": 50, "y": 50},
                        "fields": {
                            "rankTitle": "Lord Inquisitor of the Ordo Hereticus",
                            "affiliation": "Ordo Hereticus // Veridian Defense Council",
                            "narrativeRole": "Co-Protagonist / Ruthless Investigator",
                            "augmeticsPsy": "Silvered vox-larynx implant, augmetic left eye, Delta-Psyker",
                            "loadout": "Master-crafted inferno pistol 'Sinner's Eulogy', Rosarius",
                            "voiceStyle": "Metallic whisper; quotes Imperial legal codes before executions",
                        },
                        "compartments": {
                            "sec1": "Tall, gaunt, draped in a storm-coat of grox-hide. Lower jaw replaced with silver vox-tubing.",
                            "sec2": "Unsentimental yet haunted by the apprentice he had to execute ten years ago.",
                            "sec3": "Forty years in the Ordo Hereticus; uncovered the Scrap-Schism.",
                            "sec4": "Suspects the relic beneath [[Order of the Ashen Chalice]]'s basilica is a Dark Age psychic resonator.",
                        },
                        "body": (
                            "[[Lord Inquisitor Malakor Venn]] arrived in orbit aboard the "
                            "[[Strike Cruiser Litany of Penance]] forty-eight hours before "
                            "the Warp storm sealed the system."
                        ),
                    },
                    {
                        "id": "ent_char_thalassa",
                        "category": "characters",
                        "allegiance": "IMPERIUM",
                        "clearance": "VERMILION",
                        "starred": True,
                        "title": "Canoness Preceptor Thalassa Vane",
                        "subtitle": "Commander of the Order of the Ashen Chalice",
                        "epigraph": '"Hold the stairwell. Let the brass of our empty shells pave the road to the Golden Throne."',
                        "tags": ["Adepta Sororitas", "POV Character", "Commander"],
                        "updatedAt": 1761088000,
                        "coords": {"x": 50, "y": 50},
                        "fields": {
                            "rankTitle": "Canoness Preceptor",
                            "affiliation": "Order of the Ashen Chalice (Adepta Sororitas)",
                            "narrativeRole": "Primary POV Protagonist",
                            "augmeticsPsy": "Ceramite-plated augmetic right hand, high faith aura",
                            "loadout": "Relic Power Halberd 'Pyre-Cleaver', Condemnor Boltgun",
                            "voiceStyle": "Resonant contralto; mixes Ecclesiarchal verse with trench orders",
                        },
                        "compartments": {
                            "sec1": "Cropped iron-grey hair, comet-shaped burn scar on left temple, soot-blackened armor.",
                            "sec2": "Protective of common factorum workers who keep shrines in the sump levels.",
                            "sec3": "Rose from Celestian ranks during the Ork Waaagh! of Sub-Sector Achilus.",
                            "sec4": "Must choose between obeying [[Lord Inquisitor Malakor Venn]]'s purge order or defending Hive Tartarus.",
                        },
                        "body": "[[Canoness Preceptor Thalassa Vane]] commands the defense of the Obsidian Basilica.",
                    },
                    {
                        "id": "ent_faction_rusted",
                        "category": "factions",
                        "allegiance": "CHAOS",
                        "clearance": "EXTERMINATUS",
                        "starred": False,
                        "title": "Choir of the Rusted Cog",
                        "subtitle": "Dark Mechanicum & Scrap-Cult Insurgency",
                        "epigraph": '"01000010 01001100 01000101 01000101 01000100 — The Omnissiah is a corpse caged in Mars."',
                        "tags": ["Chaos", "Dark Mechanicum", "Antagonist"],
                        "updatedAt": 1761087000,
                        "coords": {"x": 30, "y": 70},
                        "fields": {
                            "subType": "Dark Mechanicum Heretek Coven & Cult",
                            "founding": "997.M41 // Seeded from Sektoth Warp-transmissions",
                            "homeworld": "World of Malice: Sektoth & Sump-Town Nine",
                            "geneSeedOrCreed": "Logic-Plague of Vashtorr & Iron Within",
                            "heraldry": "Corroded copper, weeping black oil, broken 8-toothed cog",
                            "battleCry": '"Static in the Blood! Rust on the Throne!"',
                        },
                        "compartments": {
                            "sec1": "Overworked factorum laborers driven mad by contaminated vox-static and renegade Tech-Priests.",
                            "sec2": "Led by Deacon-Magos Krol, whose vocal cords broadcast binary hymns that hijack servitors.",
                            "sec3": "Uses weaponized mining walkers, corrupted cargo-servitors, and sonic scrap-cannons.",
                            "sec4": "Their true goal is cracking open the Cinder Vault beneath the [[Order of the Ashen Chalice]] convent.",
                        },
                        "body": "The [[Choir of the Rusted Cog]] grows stronger every time the hive generators surge.",
                    },
                    {
                        "id": "ent_wargear_litany",
                        "category": "wargear",
                        "allegiance": "IMPERIUM",
                        "clearance": "MAGENTA",
                        "starred": False,
                        "title": "Strike Cruiser Litany of Penance",
                        "subtitle": "Inquisitorial & Sororitas Void-Vessel in Low Veridian Orbit",
                        "epigraph": '"Her decks smell of old incense, ozone, and three thousand years of recycled grief."',
                        "tags": ["Voidship", "Imperium", "Orbital Support"],
                        "updatedAt": 1761086000,
                        "coords": {"x": 50, "y": 50},
                        "fields": {
                            "assetClass": "Modified Dauntless-Class Light Cruiser",
                            "forgeOrigin": "Cypra Mundi Shipyards // Refitted at Kravon Minor",
                            "patternMark": "Cypra-IV Armored Prow Pattern",
                            "machineSpirit": "Melancholic & Vigilant — chimes mourning bells before Warp jumps",
                            "custodian": "Lord Inquisitor Malakor Venn & Shipmistress Hespera",
                            "powerRating": "2x Dorsal Lance Batteries, 4x Macro-Cannon Broadsides",
                        },
                        "compartments": {
                            "sec1": "Four-kilometer cathedral-hulled warship with stained-armaglass domes.",
                            "sec2": "Capable of surgical orbital lance strikes and drop-chapel deployment.",
                            "sec3": "Navigator Lady Celestine is slowly going blind from staring into the local Warp rift.",
                            "sec4": "Trapped in low orbit over [[Hive World Veridian IV]], acting as final command bastion.",
                        },
                        "body": "The [[Strike Cruiser Litany of Penance]] serves as the setting for orbital strategy scenes.",
                    },
                    {
                        "id": "ent_lore_cinder_vault",
                        "category": "lore",
                        "allegiance": "IMPERIUM",
                        "clearance": "OBSIDIAN",
                        "starred": True,
                        "title": "Dossier: The Cinder Vault Anomaly",
                        "subtitle": "Inquisitorial Seal Obsidian-IX // Eyes Only",
                        "epigraph": '"++ REDACTED BY ORDER OF THE CONCLAVE OF THORNS ++"',
                        "tags": ["Inquisitorial Dossier", "Mystery", "Archeotech"],
                        "updatedAt": 1761084000,
                        "coords": {"x": 50, "y": 50},
                        "fields": {
                            "dossierType": "Classified Archeotech & Warp-Resonance File",
                            "inquisitorialOrdo": "Ordo Hereticus & Ordo Machinum Joint File",
                            "authorSource": "Lord Inquisitor Malakor Venn",
                            "dateLogged": "0.811.999.M41",
                            "veracity": "Verified High-Threat — Eyes Only",
                            "associatedWorld": "Hive World Veridian IV (Sub-Level 00-Omega)",
                        },
                        "compartments": {
                            "sec1": "Ecclesiarchal history claims Saint Kaelen sealed the ashes of ten thousand martyrs beneath the Basilica.",
                            "sec2": "Seismic auspex scans reveal the vault predates the Great Crusade—a noctilith dampening chamber.",
                            "sec3": "Every cycle at midnight local spire-time, the vault emits a pulse that calms or summons the Warp.",
                            "sec4": "In Act III, [[Lord Inquisitor Malakor Venn]] and [[Canoness Preceptor Thalassa Vane]] breach the vault.",
                        },
                        "body": "Central mystery dossier linking [[Lord Inquisitor Malakor Venn]], [[Canoness Preceptor Thalassa Vane]], and the [[Choir of the Rusted Cog]].",
                    },
                ],
                "scenes": [
                    {
                        "id": "scn_ch1",
                        "title": "Chapter I: Sulfur and Sanctity",
                        "status": "REVISED",
                        "imperialDate": "0.812.999.M41",
                        "povEntryId": "ent_char_thalassa",
                        "locationEntryId": "ent_world_veridian",
                        "epigraph": (
                            '"Faith is not measured in the cathedral when the choir sings. '
                            "It is measured in the sump-trench when the promethium tank "
                            'runs dry." — Sermons of Saint Kaelen, Verse IV'
                        ),
                        "synopsis": (
                            "Canoness Thalassa Vane inspects the fortified promethium viaducts "
                            "of Hive Tartarus as the first scrap-code broadcast drives a column "
                            "of cargo-servitors berserk. Lord Inquisitor Venn arrives by Valkyrie."
                        ),
                        "content": (
                            "The acid rain of [[Hive World Veridian IV]] tasted of copper and dead centuries.\n\n"
                            "[[Canoness Preceptor Thalassa Vane]] stood atop the northern buttress of the Obsidian "
                            "Basilica, her soot-darkened ceramite gauntlet resting on the warm brass housing of a "
                            "heavy bolter emplacement. Three hundred meters below, the Great Promethium Viaduct cut "
                            "through the yellow sulfur-smog like an artery of rusted iron, carrying fuel trains from "
                            "the Slag-Trench into the belly of Hive Tartarus.\n\n"
                            '"Sister-Superior Miria," Thalassa spoke into her helm vox. "Report on the Sump-Gate barricades."\n\n'
                            "Static hissed—sharp, rhythmic, and wrong. Not the usual atmospheric interference from the "
                            "orbital cloud-deck, but a serrated pulse that made the teeth ache in Thalassa's jaw. Down "
                            "on the viaduct platform, forty industrial loader-servitors froze in unison. Their ocular "
                            "lenses flickered from dull amber to a jagged, strobing crimson.\n\n"
                            '"Canoness," Miria\'s voice crackled back, tight with controlled alarm. "The manufactorum '
                            "shrines on Level Twelve just went dark. And the servitors—Throne preserve us, they're "
                            'welding the blast doors shut from the inside."\n\n'
                            "Above the basilica spires, the clouds parted in a wash of roaring thruster-fire. An "
                            "obsidian-hulled Inquisitorial Valkyrie bearing the sigil of [[Lord Inquisitor Malakor Venn]] "
                            "descended from the [[Strike Cruiser Litany of Penance]], its searchlights slicing through "
                            "the falling ash."
                        ),
                        "updatedAt": 1761092000,
                    },
                    {
                        "id": "scn_ch2",
                        "title": "Chapter II: The Inquisitor's Audit",
                        "status": "FIRST DRAFT",
                        "imperialDate": "0.813.999.M41",
                        "povEntryId": "ent_char_vance",
                        "locationEntryId": "ent_world_veridian",
                        "epigraph": '"++ Vox-Transcript 99-Beta: Interrogation of Factorum Overseer Helv ++"',
                        "synopsis": (
                            "Inquisitor Venn reveals the intercepted scrap-code signal from Sektoth "
                            "and demands entry to the sealed Cinder Vault beneath the Sororitas convent."
                        ),
                        "content": (
                            "The silver vox-grille at [[Lord Inquisitor Malakor Venn]]'s throat clicked twice before "
                            "translating his breath into cold High Gothic.\n\n"
                            '"Your devotion is noted in the sector ledger, Canoness," Venn said, laying a hololithic '
                            "slate across the tactical table of the Obsidian Basilica. Green wireframe runes flickered "
                            "upward, projecting the subterranean geometry of [[Dossier: The Cinder Vault Anomaly]]. "
                            '"But the [[Choir of the Rusted Cog]] is not marching on your cathedral to burn saintly '
                            'bones. They are marching here to wake whatever is buried four hundred meters beneath your altar."'
                        ),
                        "updatedAt": 1761090500,
                    },
                ],
                "relations": [
                    {
                        "id": "rel_1",
                        "sourceId": "ent_faction_ashen",
                        "targetId": "ent_char_vance",
                        "stance": "INQUISITORIAL SCRUTINY",
                        "note": "Venn demands access to the Order's sealed Cinder Vault; Thalassa distrusts his methods.",
                    },
                    {
                        "id": "rel_2",
                        "sourceId": "ent_faction_ashen",
                        "targetId": "ent_faction_rusted",
                        "stance": "EXCOMMUNICATE / PURGE",
                        "note": "Total urban war across the lower levels of Hive Tartarus.",
                    },
                    {
                        "id": "rel_3",
                        "sourceId": "ent_world_veridian",
                        "targetId": "ent_world_khorvath",
                        "stance": "UNEASY COALITION",
                        "note": "Mutual resource dependency strained by Archmagos Septimus-9's quarantine blockade.",
                    },
                ],
                "timeline": [
                    {
                        "id": "evt_1",
                        "imperialDate": "0.112.014.M31",
                        "era": "M30-M31 // GREAT CRUSADE & HERESY",
                        "title": "Compliance of 88-14 (Veridian System)",
                        "desc": "Expeditionary Fleet 194 brings Veridian IV into Imperial Compliance. Blackstone chamber sealed.",
                    },
                    {
                        "id": "evt_2",
                        "imperialDate": "3.640.412.M38",
                        "era": "M32-M40 // AGE OF IMPERIUM",
                        "title": "Consecration of the Order of the Ashen Chalice",
                        "desc": "Following the martyrdom of Saint Kaelen, the Obsidian Basilica is raised atop the vault.",
                    },
                    {
                        "id": "evt_3",
                        "imperialDate": "9.798.999.M41",
                        "era": "M41 // TIME OF ENDING",
                        "title": "Eruption of the Gorgon's Maw Warp Storm",
                        "desc": "Violent Warp eddies cut the Achilus Sub-Sector off from astropathic reinforcement.",
                    },
                    {
                        "id": "evt_4",
                        "imperialDate": "0.812.999.M41",
                        "era": "M42 // ERA INDOMITUS",
                        "title": "Uprising of the Choir of the Rusted Cog (Chapter I)",
                        "desc": "Lord Inquisitor Malakor Venn makes planetfall hours before the scrap-cult assault.",
                    },
                ],
            }
        ],
    }


# =============================================================================
# 4. HELPER UTILITIES (IMPERIAL DATE & WINDOWS .ICO GENERATOR)
# =============================================================================
def compute_imperial_date(check_num: int, year: int, month: int, day: int) -> str:
    check = max(0, min(9, int(check_num)))
    full_year = max(1000, int(year))
    m = max(1, min(12, int(month)))
    d = max(1, min(31, int(day)))

    millennium = ((full_year - 1) // 1000) + 1
    year_in_mill = f"{full_year % 1000:03d}"
    day_of_year = (m - 1) * 30.4375 + d
    fraction = max(1, min(999, round((day_of_year / 365.25) * 1000)))
    return f"{check}.{fraction:03d}.{year_in_mill}.M{millennium}"


def count_words(text: str) -> int:
    if not text or not text.strip():
        return 0
    return len(text.strip().split())


def write_40k_cog_ico(ico_path: Path):
    """
    Generates a genuine 32x32 32-bit RGBA Windows .ICO file depicting a
    Warhammer 40K Mechanicus Brass/Emerald Cogwheel & Auspex Reticle using
    pure Python byte packing (no Pillow required!).
    """
    width, height = 32, 32
    pixels = bytearray(width * height * 4)
    cx, cy = 15.5, 15.5

    for y in range(height):
        # BMP rows in ICO are stored bottom-to-top
        bmp_y = height - 1 - y
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)

            r, g, b, a = 7, 11, 9, 0  # Transparent outside

            # Outer cogwheel teeth
            tooth = math.cos(angle * 8) > 0.25
            outer_limit = 14.8 if tooth else 12.2

            if dist <= outer_limit:
                # Dark obsidian backing
                r, g, b, a = 12, 22, 18, 255
                # Brass cog rim
                if dist >= 9.5:
                    r, g, b = 194, 155, 72
                # Inner emerald phosphor ring
                elif 5.8 <= dist <= 7.8:
                    r, g, b = 16, 185, 129
                # Center skull/auspex core
                elif dist <= 3.2:
                    r, g, b = 110, 231, 183

                # Crosshair reticle lines
                if (abs(dx) < 0.9 or abs(dy) < 0.9) and 3.5 < dist < 11.5:
                    r, g, b = 52, 211, 153

            idx = (bmp_y * width + x) * 4
            pixels[idx : idx + 4] = bytes((b, g, r, a))

    # AND mask (1 bit per pixel, padded to 32-bit boundaries = 4 bytes per row)
    and_mask = bytes(4 * height)

    # BITMAPINFOHEADER (40 bytes)
    import struct

    bih = struct.pack(
        "<IIIHHIIIIII",
        40,              # biSize
        width,           # biWidth
        height * 2,      # biHeight (includes AND mask)
        1,               # biPlanes
        32,              # biBitCount
        0,               # biCompression
        len(pixels) + len(and_mask),
        0,
        0,
        0,
        0,
    )

    image_data = bih + bytes(pixels) + and_mask
    # ICONDIR (6 bytes) + ICONDIRENTRY (16 bytes)
    icondir = struct.pack("<HHH", 0, 1, 1)
    icondirentry = struct.pack(
        "<BBBBHHII",
        width,
        height,
        0,
        0,
        1,
        32,
        len(image_data),
        6 + 16,
    )

    with open(ico_path, "wb") as f:
        f.write(icondir + icondirentry + image_data)


# =============================================================================
# 5. MAIN STANDALONE TKINTER APPLICATION CLASS
# =============================================================================
class LexicanumCogitatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "LEXICANUM COGITATOR // MK.IX DATASLATE — 40K Worldbuilding & Scriptorium"
        )
        self.root.geometry("1460x900")
        self.root.minsize(1100, 700)

        # Persistent JSON file stored right alongside the script (or user home fallback)
        try:
            base_dir = Path(__file__).resolve().parent
        except Exception:
            base_dir = Path.home()
        self.save_file = base_dir / "cogitator_databanks_40k.json"
        self.icon_file = base_dir / "cogitator_40k.ico"

        self._is_loading_ui = False
        self.forge_results = {}
        self.spec_entries = {}
        self.compartment_texts = {}
        self._dragging_world_id = None

        # Load state from disk or initialize default
        self.restored_from_disk = self.load_state()

        # Set window icon
        self._setup_window_icon()

        # Build UI
        self._build_ui()
        self.apply_theme()
        self.refresh_all_views()

        # Restore exact tab & cursor position
        self._restore_session_place()

        # Bind clean exit hook so closing window always saves exact place
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)

    # -------------------------------------------------------------------------
    # PERSISTENCE ENGINE
    # -------------------------------------------------------------------------
    def load_state(self) -> bool:
        if self.save_file.exists():
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data.get("projects"):
                    self.state = data
                    return True
            except Exception as exc:
                print(f"[Cogitator Warning] Could not read {self.save_file}: {exc}")
        self.state = create_starter_state()
        self.save_state(quiet=True)
        return False

    def save_state(self, quiet: bool = False):
        if self._is_loading_ui:
            return
        self._capture_cursor_positions()
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            if not quiet and hasattr(self, "status_label"):
                now_str = time.strftime("%H:%M:%S")
                self.status_label.config(
                    text=f"● NOOSPHERE MEMORY AUTO-SAVED [{now_str}] → {self.save_file.name}"
                )
        except Exception as exc:
            if hasattr(self, "status_label"):
                self.status_label.config(text=f"⚠ SAVE ERROR: {exc}")

    def _capture_cursor_positions(self):
        if not hasattr(self, "codex_body_text") or not hasattr(self, "scene_prose_text"):
            return
        cursors = self.state.setdefault("cursorPositions", {})
        entry = self.get_active_entry()
        if entry:
            try:
                cursors[f"entry_{entry['id']}"] = self.codex_body_text.index(tk.INSERT)
            except Exception:
                pass
        scene = self.get_active_scene()
        if scene:
            try:
                cursors[f"scene_{scene['id']}"] = self.scene_prose_text.index(tk.INSERT)
            except Exception:
                pass

    def _restore_session_place(self):
        tab_idx = int(self.state.get("activeMainTab", 0))
        if 0 <= tab_idx < self.notebook.index("end"):
            self.notebook.select(tab_idx)

        cursors = self.state.get("cursorPositions", {})
        entry = self.get_active_entry()
        if entry and f"entry_{entry['id']}" in cursors:
            try:
                pos = cursors[f"entry_{entry['id']}"]
                self.codex_body_text.mark_set(tk.INSERT, pos)
                self.codex_body_text.see(pos)
            except Exception:
                pass

        scene = self.get_active_scene()
        if scene and f"scene_{scene['id']}" in cursors:
            try:
                pos = cursors[f"scene_{scene['id']}"]
                self.scene_prose_text.mark_set(tk.INSERT, pos)
                self.scene_prose_text.see(pos)
            except Exception:
                pass

        ptr = self.state.get("lastEditedPointer", {})
        if ptr and hasattr(self, "ribbon_label"):
            self.ribbon_label.config(
                text=(
                    f"BOOKMARKED PLACE RESTORED // [{ptr.get('type', 'CODEX').upper()}] "
                    f"{ptr.get('title', '')}"
                )
            )

    def on_close_window(self):
        try:
            self.state["activeMainTab"] = self.notebook.index(self.notebook.select())
        except Exception:
            pass
        self.save_state(quiet=True)
        self.root.destroy()

    # -------------------------------------------------------------------------
    # ACTIVE DATA GETTERS
    # -------------------------------------------------------------------------
    def get_active_project(self) -> dict:
        pid = self.state.get("activeProjectId")
        for p in self.state["projects"]:
            if p["id"] == pid:
                return p
        self.state["activeProjectId"] = self.state["projects"][0]["id"]
        return self.state["projects"][0]

    def get_active_entry(self):
        proj = self.get_active_project()
        eid = self.state.get("selectedEntryId")
        for e in proj["entries"]:
            if e["id"] == eid:
                return e
        if proj["entries"]:
            self.state["selectedEntryId"] = proj["entries"][0]["id"]
            return proj["entries"][0]
        return None

    def get_active_scene(self):
        proj = self.get_active_project()
        sid = self.state.get("activeSceneId")
        for s in proj["scenes"]:
            if s["id"] == sid:
                return s
        if proj["scenes"]:
            self.state["activeSceneId"] = proj["scenes"][0]["id"]
            return proj["scenes"][0]
        return None

    # -------------------------------------------------------------------------
    # ICON & DESKTOP SHORTCUT GENERATOR
    # -------------------------------------------------------------------------
    def _setup_window_icon(self):
        try:
            if not self.icon_file.exists():
                write_40k_cog_ico(self.icon_file)
            if platform.system() == "Windows":
                self.root.iconbitmap(default=str(self.icon_file))
        except Exception:
            pass

    def create_desktop_shortcut(self):
        """
        Creates a double-clickable Desktop shortcut with the custom 40K Cogwheel
        icon so the user can launch the standalone desktop app directly from
        their Desktop without opening a browser or terminal.
        """
        try:
            write_40k_cog_ico(self.icon_file)
            script_path = Path(__file__).resolve()
            desktop_dir = Path.home() / "Desktop"
            if not desktop_dir.exists():
                desktop_dir = Path.home()

            sys_name = platform.system()
            if sys_name == "Windows":
                # Also write a .pyw launcher so Windows opens it with zero console flash
                pyw_path = script_path.with_suffix(".pyw")
                if script_path.suffix.lower() != ".pyw":
                    try:
                        pyw_path.write_text(
                            script_path.read_text(encoding="utf-8"), encoding="utf-8"
                        )
                    except Exception:
                        pyw_path = script_path

                lnk_path = desktop_dir / "Lexicanum Cogitator 40K.lnk"
                vbs_path = script_path.parent / "_create_40k_shortcut.vbs"
                pythonw_exe = Path(sys.executable).with_name("pythonw.exe")
                if not pythonw_exe.exists():
                    pythonw_exe = Path(sys.executable)

                vbs_code = (
                    'Set oWS = WScript.CreateObject("WScript.Shell")\n'
                    f'sLinkFile = "{lnk_path}"\n'
                    "Set oLink = oWS.CreateShortcut(sLinkFile)\n"
                    f'oLink.TargetPath = "{pythonw_exe}"\n'
                    f'oLink.Arguments = """{pyw_path}"""\n'
                    f'oLink.WorkingDirectory = "{script_path.parent}"\n'
                    f'oLink.IconLocation = "{self.icon_file}, 0"\n'
                    'oLink.Description = "Lexicanum Cogitator Mk.IX — 40K Worldbuilding & Scriptorium"\n'
                    "oLink.Save\n"
                )
                vbs_path.write_text(vbs_code, encoding="utf-8")
                subprocess.run(["cscript", "//Nologo", str(vbs_path)], check=False)
                try:
                    vbs_path.unlink()
                except Exception:
                    pass
                messagebox.showinfo(
                    "++ DESKTOP SHORTCUT CONSECRATED ++",
                    f"Created desktop icon shortcut:\n{lnk_path}\n\n"
                    "Double-click 'Lexicanum Cogitator 40K' on your Desktop anytime "
                    "to open this standalone app directly!",
                )
            elif sys_name == "Darwin":
                cmd_file = desktop_dir / "Lexicanum_Cogitator_40K.command"
                cmd_file.write_text(
                    f'#!/bin/bash\ncd "{script_path.parent}"\n"{sys.executable}" "{script_path}" &\n',
                    encoding="utf-8",
                )
                os.chmod(cmd_file, 0o755)
                messagebox.showinfo(
                    "++ DESKTOP LAUNCHER CREATED ++",
                    f"Created double-clickable macOS launcher on Desktop:\n{cmd_file}",
                )
            else:
                desktop_file = desktop_dir / "Lexicanum_Cogitator_40K.desktop"
                desktop_file.write_text(
                    "[Desktop Entry]\n"
                    "Type=Application\n"
                    "Name=Lexicanum Cogitator 40K\n"
                    "Comment=40K Worldbuilding & Scriptorium Dataslate\n"
                    f'Exec="{sys.executable}" "{script_path}"\n'
                    f"Path={script_path.parent}\n"
                    f"Icon={self.icon_file}\n"
                    "Terminal=false\n",
                    encoding="utf-8",
                )
                os.chmod(desktop_file, 0o755)
                messagebox.showinfo(
                    "++ DESKTOP LAUNCHER CREATED ++",
                    f"Created desktop launcher:\n{desktop_file}",
                )
        except Exception as exc:
            messagebox.showerror("Shortcut Error", f"Could not create shortcut:\n{exc}")

    # -------------------------------------------------------------------------
    # UI CONSTRUCTION
    # -------------------------------------------------------------------------
    def _build_ui(self):
        # Top Hardware Bar
        self.top_bar = tk.Frame(self.root, bd=1, relief=tk.RIDGE, padx=10, pady=6)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        brand_frame = tk.Frame(self.top_bar)
        brand_frame.pack(side=tk.LEFT)
        self.title_lbl = tk.Label(
            brand_frame,
            text="⚙ LEXICANUM COGITATOR // MK.IX DATASLATE",
            font=("Georgia", 13, "bold"),
        )
        self.title_lbl.pack(side=tk.TOP, anchor="w")
        self.status_label = tk.Label(
            brand_frame,
            text=f"● NOOSPHERE MEMORY ACTIVE → {self.save_file.name}",
            font=("Consolas", 9),
        )
        self.status_label.pack(side=tk.TOP, anchor="w")

        # Project Selector Controls
        proj_ctrl = tk.Frame(self.top_bar, padx=14)
        proj_ctrl.pack(side=tk.LEFT)
        tk.Label(proj_ctrl, text="CRUSADE / PROJECT:", font=("Consolas", 9, "bold")).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(
            proj_ctrl, textvariable=self.project_var, state="readonly", width=34
        )
        self.project_combo.pack(side=tk.LEFT, padx=3)
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_switched)

        self.btn_new_proj = tk.Button(
            proj_ctrl,
            text="+ NEW PROJECT",
            font=("Consolas", 9, "bold"),
            command=self.open_new_project_dialog,
            padx=8,
            pady=2,
        )
        self.btn_new_proj.pack(side=tk.LEFT, padx=3)

        self.btn_cfg_proj = tk.Button(
            proj_ctrl,
            text="CFG",
            font=("Consolas", 9),
            command=self.open_project_settings_dialog,
            padx=6,
            pady=2,
        )
        self.btn_cfg_proj.pack(side=tk.LEFT, padx=2)

        # Right-hand Controls: Theme, Desktop Icon Creator, Export/Backup
        right_ctrl = tk.Frame(self.top_bar)
        right_ctrl.pack(side=tk.RIGHT)

        tk.Label(right_ctrl, text="PHOSPHOR:", font=("Consolas", 9)).pack(
            side=tk.LEFT, padx=3
        )
        self.theme_var = tk.StringVar(value=self.state.get("theme", "AUSPEX GREEN"))
        self.theme_combo = ttk.Combobox(
            right_ctrl,
            textvariable=self.theme_var,
            values=list(THEMES.keys()),
            state="readonly",
            width=18,
        )
        self.theme_combo.pack(side=tk.LEFT, padx=3)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_changed)

        self.btn_shortcut = tk.Button(
            right_ctrl,
            text="⚙ CREATE DESKTOP ICON",
            font=("Consolas", 9, "bold"),
            command=self.create_desktop_shortcut,
            padx=8,
            pady=2,
        )
        self.btn_shortcut.pack(side=tk.LEFT, padx=4)

        self.btn_export_md = tk.Button(
            right_ctrl,
            text="📜 EXPORT .MD BIBLE",
            font=("Consolas", 9, "bold"),
            command=self.export_markdown_compilation,
            padx=8,
            pady=2,
        )
        self.btn_export_md.pack(side=tk.LEFT, padx=3)

        self.btn_backup = tk.Button(
            right_ctrl,
            text="💾 BACKUP / LOAD .JSON",
            font=("Consolas", 9, "bold"),
            command=self.open_backup_dialog,
            padx=8,
            pady=2,
        )
        self.btn_backup.pack(side=tk.LEFT, padx=3)

        # Telemetry & Session Bookmark Ribbon
        self.ribbon_bar = tk.Frame(self.root, padx=12, pady=4, bd=1, relief=tk.SOLID)
        self.ribbon_bar.pack(side=tk.TOP, fill=tk.X)

        self.ribbon_label = tk.Label(
            self.ribbon_bar,
            text="BOOKMARKED PLACE: Resumed last active session state.",
            font=("Consolas", 9),
        )
        self.ribbon_label.pack(side=tk.LEFT)

        self.btn_jump_last = tk.Button(
            self.ribbon_bar,
            text="JUMP TO LAST EDITED DOSSIER / SCENE →",
            font=("Consolas", 9, "bold"),
            command=self.jump_to_last_edited,
            padx=8,
            pady=1,
        )
        self.btn_jump_last.pack(side=tk.RIGHT, padx=4)

        self.telemetry_stats_lbl = tk.Label(
            self.ribbon_bar, text="0 Dossiers • 0 Words", font=("Consolas", 9)
        )
        self.telemetry_stats_lbl.pack(side=tk.RIGHT, padx=12)

        # Main Horizontal Split: Left/Center Primary Workspace + Right Pinned Reference Slate
        self.main_paned = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashwidth=6, bd=0
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.left_workspace = tk.Frame(self.main_paned)
        self.right_ref_drawer = tk.Frame(self.main_paned, bd=1, relief=tk.RIDGE)

        self.main_paned.add(self.left_workspace, stretch="always", minsize=760)
        self.main_paned.add(self.right_ref_drawer, stretch="never", minsize=330, width=370)

        # Notebook inside Left Workspace for the 5 Primary Modes
        self.notebook = ttk.Notebook(self.left_workspace)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_main_tab_changed)

        self.tab_codex = tk.Frame(self.notebook)
        self.tab_scriptorium = tk.Frame(self.notebook)
        self.tab_astrography = tk.Frame(self.notebook)
        self.tab_chronology = tk.Frame(self.notebook)
        self.tab_forge = tk.Frame(self.notebook)

        self.notebook.add(self.tab_codex, text="  I. CODEX DATABANKS  ")
        self.notebook.add(self.tab_scriptorium, text="  II. SCRIPTORIUM (WRITE)  ")
        self.notebook.add(self.tab_astrography, text="  III. SECTOR MAP & MATRIX  ")
        self.notebook.add(self.tab_chronology, text="  IV. CHRONOLOGY (M30–M42)  ")
        self.notebook.add(self.tab_forge, text="  V. LORE & NAME FORGE  ")

        self._build_codex_tab()
        self._build_scriptorium_tab()
        self._build_astrography_tab()
        self._build_chronology_tab()
        self._build_forge_tab()
        self._build_reference_drawer()

    # -------------------------------------------------------------------------
    # TAB I: CODEX DATABANKS UI
    # -------------------------------------------------------------------------
    def _build_codex_tab(self):
        pane = tk.PanedWindow(self.tab_codex, orient=tk.HORIZONTAL, sashwidth=5)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left_col = tk.Frame(pane, padx=6, pady=6)
        right_col = tk.Frame(pane, padx=8, pady=6)
        pane.add(left_col, width=320, minsize=270)
        pane.add(right_col, stretch="always")

        # Search + New Dossier
        search_row = tk.Frame(left_col)
        search_row.pack(fill=tk.X, pady=(0, 6))
        self.codex_search_var = tk.StringVar()
        self.codex_search_var.trace_add("write", lambda *_: self.refresh_codex_list())
        self.codex_search_entry = tk.Entry(
            search_row, textvariable=self.codex_search_var, font=("Consolas", 10)
        )
        self.codex_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_new_entry = tk.Button(
            search_row,
            text="+ NEW DOSSIER",
            font=("Consolas", 9, "bold"),
            command=self.create_new_codex_entry,
            padx=8,
            pady=2,
        )
        self.btn_new_entry.pack(side=tk.RIGHT)

        # Organizational Category Filter Buttons (2x3 Grid)
        tk.Label(
            left_col, text="ORGANIZATIONAL CATEGORIES:", font=("Consolas", 8, "bold")
        ).pack(anchor="w", pady=(2, 2))
        self.cat_btn_frame = tk.Frame(left_col)
        self.cat_btn_frame.pack(fill=tk.X, pady=(0, 6))
        self.cat_filter_buttons = {}
        cat_defs = [
            ("all", "ALL DOSSIERS"),
            ("factions", "I. FACTIONS"),
            ("worlds", "II. WORLDS"),
            ("characters", "III. PERSONAE"),
            ("wargear", "IV. WARGEAR"),
            ("lore", "V. LORE/CREED"),
        ]
        for idx, (cid, clabel) in enumerate(cat_defs):
            b = tk.Button(
                self.cat_btn_frame,
                text=clabel,
                font=("Consolas", 8, "bold"),
                command=lambda c=cid: self.set_category_filter(c),
                pady=3,
            )
            b.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=2, pady=2)
            self.cat_filter_buttons[cid] = b
        self.cat_btn_frame.columnconfigure(0, weight=1)
        self.cat_btn_frame.columnconfigure(1, weight=1)

        # Grand Allegiance Filter
        alleg_row = tk.Frame(left_col)
        alleg_row.pack(fill=tk.X, pady=(0, 6))
        tk.Label(alleg_row, text="ALLEGIANCE:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT
        )
        self.alleg_filter_var = tk.StringVar(value="ALL")
        self.alleg_filter_combo = ttk.Combobox(
            alleg_row,
            textvariable=self.alleg_filter_var,
            values=ALLEGIANCES,
            state="readonly",
            width=16,
        )
        self.alleg_filter_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        self.alleg_filter_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.set_allegiance_filter(self.alleg_filter_var.get()),
        )

        # Listbox of Codex Entries
        self.codex_list_heading = tk.Label(
            left_col, text="DATABANK DOSSIERS", font=("Consolas", 9, "bold")
        )
        self.codex_list_heading.pack(anchor="w", pady=(2, 2))

        list_frame = tk.Frame(left_col)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self.codex_listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            activestyle="none",
            exportselection=False,
        )
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.codex_listbox.yview)
        self.codex_listbox.config(yscrollcommand=sb.set)
        self.codex_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.codex_listbox.bind("<<ListboxSelect>>", self.on_codex_listbox_select)

        # Right Column: Structured Dossier Editor (Scrollable Canvas)
        toolbar = tk.Frame(right_col, pady=4)
        toolbar.pack(fill=tk.X)

        tk.Label(toolbar, text="CATEGORY:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT
        )
        self.entry_cat_var = tk.StringVar()
        self.entry_cat_combo = ttk.Combobox(
            toolbar,
            textvariable=self.entry_cat_var,
            values=list(CATEGORY_SCHEMA.keys()),
            state="readonly",
            width=12,
        )
        self.entry_cat_combo.pack(side=tk.LEFT, padx=4)
        self.entry_cat_combo.bind("<<ComboboxSelected>>", self.on_entry_meta_changed)

        tk.Label(toolbar, text="ALLEGIANCE:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        self.entry_alleg_var = tk.StringVar()
        self.entry_alleg_combo = ttk.Combobox(
            toolbar,
            textvariable=self.entry_alleg_var,
            values=ALLEGIANCES[1:],
            state="readonly",
            width=12,
        )
        self.entry_alleg_combo.pack(side=tk.LEFT, padx=4)
        self.entry_alleg_combo.bind("<<ComboboxSelected>>", self.on_entry_meta_changed)

        tk.Label(toolbar, text="CLEARANCE:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        self.entry_clear_var = tk.StringVar()
        self.entry_clear_combo = ttk.Combobox(
            toolbar,
            textvariable=self.entry_clear_var,
            values=CLEARANCES,
            state="readonly",
            width=13,
        )
        self.entry_clear_combo.pack(side=tk.LEFT, padx=4)
        self.entry_clear_combo.bind("<<ComboboxSelected>>", self.on_entry_meta_changed)

        # Action Buttons
        self.btn_purge_entry = tk.Button(
            toolbar,
            text="PURGE",
            font=("Consolas", 9, "bold"),
            command=self.delete_active_entry,
            padx=6,
        )
        self.btn_purge_entry.pack(side=tk.RIGHT, padx=2)

        self.btn_pin_entry = tk.Button(
            toolbar,
            text="📌 PIN TO SLATE",
            font=("Consolas", 9, "bold"),
            command=self.pin_active_entry,
            padx=8,
        )
        self.btn_pin_entry.pack(side=tk.RIGHT, padx=3)

        self.btn_star_entry = tk.Button(
            toolbar,
            text="★ BOOKMARK",
            font=("Consolas", 9, "bold"),
            command=self.toggle_star_active_entry,
            padx=8,
        )
        self.btn_star_entry.pack(side=tk.RIGHT, padx=3)

        # Title, Subtitle, Epigraph
        header_grid = tk.Frame(right_col)
        header_grid.pack(fill=tk.X, pady=4)
        header_grid.columnconfigure(0, weight=3)
        header_grid.columnconfigure(1, weight=2)

        tk.Label(
            header_grid, text="DOSSIER DESIGNATION / TITLE:", font=("Consolas", 8, "bold")
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header_grid, text="HIGH GOTHIC SUBTITLE / CALLSIGN:", font=("Consolas", 8, "bold")
        ).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_title_var = tk.StringVar()
        self.entry_title_var.trace_add("write", lambda *_: self.on_entry_text_changed())
        self.entry_title_inp = tk.Entry(
            header_grid, textvariable=self.entry_title_var, font=("Georgia", 12, "bold")
        )
        self.entry_title_inp.grid(row=1, column=0, sticky="ew", pady=2)

        self.entry_sub_var = tk.StringVar()
        self.entry_sub_var.trace_add("write", lambda *_: self.on_entry_text_changed())
        self.entry_sub_inp = tk.Entry(
            header_grid, textvariable=self.entry_sub_var, font=("Consolas", 10)
        )
        self.entry_sub_inp.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)

        epi_row = tk.Frame(right_col)
        epi_row.pack(fill=tk.X, pady=2)
        tk.Label(
            epi_row, text="++ IN-UNIVERSE EPIGRAPH ++", font=("Consolas", 8, "bold")
        ).pack(side=tk.LEFT)
        tk.Button(
            epi_row,
            text="⚡ ROLL 40K EPIGRAPH",
            font=("Consolas", 8, "bold"),
            command=self.roll_epigraph_for_active_entry,
            padx=6,
        ).pack(side=tk.RIGHT)

        self.entry_epi_var = tk.StringVar()
        self.entry_epi_var.trace_add("write", lambda *_: self.on_entry_text_changed())
        self.entry_epi_inp = tk.Entry(
            right_col, textvariable=self.entry_epi_var, font=("Georgia", 9, "italic")
        )
        self.entry_epi_inp.pack(fill=tk.X, pady=(0, 6))

        # Dynamic 6 Telemetry Specification Fields (2x3 Grid)
        self.specs_frame = tk.LabelFrame(
            right_col,
            text=" ADMINISTRATUM TELEMETRY & SPECIFICATIONS ",
            font=("Consolas", 9, "bold"),
            padx=6,
            pady=4,
        )
        self.specs_frame.pack(fill=tk.X, pady=4)
        for c in range(3):
            self.specs_frame.columnconfigure(c, weight=1)

        # 4-Pillar Worldbuilding Compartments (2x2 Grid)
        self.comp_frame = tk.LabelFrame(
            right_col,
            text=" STRUCTURED WORLDBUILDING COMPARTMENTS ",
            font=("Consolas", 9, "bold"),
            padx=6,
            pady=4,
        )
        self.comp_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.comp_frame.columnconfigure(0, weight=1)
        self.comp_frame.columnconfigure(1, weight=1)
        self.comp_frame.rowconfigure(0, weight=1)
        self.comp_frame.rowconfigure(1, weight=1)

        # Extended Chronicle & [[Wiki-Links]]
        ext_frame = tk.LabelFrame(
            right_col,
            text=" EXTENDED LEXICANUM CHRONICLE & NOTES (SUPPORTS [[WIKI-LINKS]]) ",
            font=("Consolas", 9, "bold"),
            padx=6,
            pady=4,
        )
        ext_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        self.codex_body_text = tk.Text(
            ext_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 10), undo=True
        )
        body_sb = ttk.Scrollbar(
            ext_frame, orient=tk.VERTICAL, command=self.codex_body_text.yview
        )
        self.codex_body_text.config(yscrollcommand=body_sb.set)
        self.codex_body_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        body_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.codex_body_text.bind("<KeyRelease>", lambda e: self.on_entry_text_changed())

        # Footer: Tags + Detected Links
        footer_row = tk.Frame(right_col)
        footer_row.pack(fill=tk.X, pady=2)
        tk.Label(footer_row, text="TAGS (COMMA-SEP):", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT
        )
        self.entry_tags_var = tk.StringVar()
        self.entry_tags_var.trace_add("write", lambda *_: self.on_entry_text_changed())
        self.entry_tags_inp = tk.Entry(
            footer_row, textvariable=self.entry_tags_var, font=("Consolas", 9), width=36
        )
        self.entry_tags_inp.pack(side=tk.LEFT, padx=6)

        self.entry_word_count_lbl = tk.Label(
            footer_row, text="0 words", font=("Consolas", 9, "bold")
        )
        self.entry_word_count_lbl.pack(side=tk.RIGHT)

    # -------------------------------------------------------------------------
    # TAB II: SCRIPTORIUM (MANUSCRIPT CHAPTERS & SCENES)
    # -------------------------------------------------------------------------
    def _build_scriptorium_tab(self):
        pane = tk.PanedWindow(self.tab_scriptorium, orient=tk.HORIZONTAL, sashwidth=5)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left_binder = tk.Frame(pane, padx=6, pady=6)
        right_editor = tk.Frame(pane, padx=8, pady=6)
        pane.add(left_binder, width=280, minsize=240)
        pane.add(right_editor, stretch="always")

        top_b = tk.Frame(left_binder)
        top_b.pack(fill=tk.X, pady=(0, 6))
        tk.Label(top_b, text="MANUSCRIPT BINDER", font=("Georgia", 11, "bold")).pack(
            side=tk.LEFT
        )
        tk.Button(
            top_b,
            text="+ NEW SCENE",
            font=("Consolas", 9, "bold"),
            command=self.create_new_scene,
            padx=8,
        ).pack(side=tk.RIGHT)

        self.ms_progress_lbl = tk.Label(
            left_binder, text="TOTAL WORDS: 0 / 15,000", font=("Consolas", 9, "bold")
        )
        self.ms_progress_lbl.pack(anchor="w", pady=(0, 4))

        list_wrap = tk.Frame(left_binder)
        list_wrap.pack(fill=tk.BOTH, expand=True)
        self.scene_listbox = tk.Listbox(
            list_wrap, font=("Consolas", 10), activestyle="none", exportselection=False
        )
        ssb = ttk.Scrollbar(
            list_wrap, orient=tk.VERTICAL, command=self.scene_listbox.yview
        )
        self.scene_listbox.config(yscrollcommand=ssb.set)
        self.scene_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ssb.pack(side=tk.RIGHT, fill=tk.Y)
        self.scene_listbox.bind("<<ListboxSelect>>", self.on_scene_listbox_select)

        # Scene Editor Header
        scn_bar = tk.Frame(right_editor)
        scn_bar.pack(fill=tk.X, pady=(0, 4))

        tk.Label(scn_bar, text="STATUS:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT
        )
        self.scene_status_var = tk.StringVar()
        self.scene_status_combo = ttk.Combobox(
            scn_bar,
            textvariable=self.scene_status_var,
            values=["OUTLINE", "FIRST DRAFT", "REVISED", "FINAL LEXICANUM"],
            state="readonly",
            width=16,
        )
        self.scene_status_combo.pack(side=tk.LEFT, padx=4)
        self.scene_status_combo.bind("<<ComboboxSelected>>", self.on_scene_changed)

        tk.Label(scn_bar, text="IMPERIAL DATE:", font=("Consolas", 8, "bold")).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        self.scene_date_var = tk.StringVar()
        self.scene_date_var.trace_add("write", lambda *_: self.on_scene_changed())
        self.scene_date_inp = tk.Entry(
            scn_bar, textvariable=self.scene_date_var, font=("Consolas", 10), width=16
        )
        self.scene_date_inp.pack(side=tk.LEFT, padx=4)

        tk.Button(
            scn_bar,
            text="DELETE SCENE",
            font=("Consolas", 9),
            command=self.delete_active_scene,
            padx=6,
        ).pack(side=tk.RIGHT, padx=2)

        tk.Button(
            scn_bar,
            text="📌 PIN POV & WORLD TO SLATE",
            font=("Consolas", 9, "bold"),
            command=self.pin_scene_pov_and_world,
            padx=8,
        ).pack(side=tk.RIGHT, padx=4)

        # Title, POV, World Row
        meta_row = tk.Frame(right_editor)
        meta_row.pack(fill=tk.X, pady=4)
        meta_row.columnconfigure(0, weight=2)
        meta_row.columnconfigure(1, weight=1)
        meta_row.columnconfigure(2, weight=1)

        tk.Label(
            meta_row, text="CHAPTER / SCENE TITLE:", font=("Consolas", 8, "bold")
        ).grid(row=0, column=0, sticky="w")
        tk.Label(meta_row, text="POV PERSONA:", font=("Consolas", 8, "bold")).grid(
            row=0, column=1, sticky="w", padx=4
        )
        tk.Label(meta_row, text="THEATRE / WORLD:", font=("Consolas", 8, "bold")).grid(
            row=0, column=2, sticky="w", padx=4
        )

        self.scene_title_var = tk.StringVar()
        self.scene_title_var.trace_add("write", lambda *_: self.on_scene_changed())
        self.scene_title_inp = tk.Entry(
            meta_row, textvariable=self.scene_title_var, font=("Georgia", 12, "bold")
        )
        self.scene_title_inp.grid(row=1, column=0, sticky="ew", pady=2)

        self.scene_pov_var = tk.StringVar()
        self.scene_pov_combo = ttk.Combobox(
            meta_row, textvariable=self.scene_pov_var, state="readonly"
        )
        self.scene_pov_combo.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
        self.scene_pov_combo.bind("<<ComboboxSelected>>", self.on_scene_changed)

        self.scene_loc_var = tk.StringVar()
        self.scene_loc_combo = ttk.Combobox(
            meta_row, textvariable=self.scene_loc_var, state="readonly"
        )
        self.scene_loc_combo.grid(row=1, column=2, sticky="ew", padx=4, pady=2)
        self.scene_loc_combo.bind("<<ComboboxSelected>>", self.on_scene_changed)

        # Epigraph & Beats
        tk.Label(
            right_editor, text="CHAPTER EPIGRAPH:", font=("Consolas", 8, "bold")
        ).pack(anchor="w")
        self.scene_epi_var = tk.StringVar()
        self.scene_epi_var.trace_add("write", lambda *_: self.on_scene_changed())
        self.scene_epi_inp = tk.Entry(
            right_editor, textvariable=self.scene_epi_var, font=("Georgia", 9, "italic")
        )
        self.scene_epi_inp.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            right_editor,
            text="TACTICAL SCENE BEATS / SYNOPSIS:",
            font=("Consolas", 8, "bold"),
        ).pack(anchor="w")
        self.scene_syn_text = tk.Text(
            right_editor, height=3, wrap=tk.WORD, font=("Segoe UI", 9)
        )
        self.scene_syn_text.pack(fill=tk.X, pady=(0, 6))
        self.scene_syn_text.bind("<KeyRelease>", lambda e: self.on_scene_changed())

        # Main Manuscript Prose Slate
        prose_hdr = tk.Frame(right_editor)
        prose_hdr.pack(fill=tk.X)
        tk.Label(
            prose_hdr,
            text="MANUSCRIPT PROSE SLATE",
            font=("Consolas", 9, "bold"),
        ).pack(side=tk.LEFT)
        self.scene_wc_lbl = tk.Label(
            prose_hdr, text="0 words", font=("Consolas", 9, "bold")
        )
        self.scene_wc_lbl.pack(side=tk.RIGHT)

        prose_wrap = tk.Frame(right_editor)
        prose_wrap.pack(fill=tk.BOTH, expand=True, pady=4)
        self.scene_prose_text = tk.Text(
            prose_wrap,
            wrap=tk.WORD,
            font=("Georgia", 11),
            padx=12,
            pady=10,
            spacing1=4,
            spacing3=4,
            undo=True,
        )
        psb = ttk.Scrollbar(
            prose_wrap, orient=tk.VERTICAL, command=self.scene_prose_text.yview
        )
        self.scene_prose_text.config(yscrollcommand=psb.set)
        self.scene_prose_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        psb.pack(side=tk.RIGHT, fill=tk.Y)
        self.scene_prose_text.bind("<KeyRelease>", lambda e: self.on_scene_changed())

    # -------------------------------------------------------------------------
    # TAB III: HOLOLITHIC SUB-SECTOR MAP & DIPLOMACY MATRIX
    # -------------------------------------------------------------------------
    def _build_astrography_tab(self):
        pane = tk.PanedWindow(self.tab_astrography, orient=tk.HORIZONTAL, sashwidth=5)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        map_frame = tk.Frame(pane, padx=6, pady=6)
        matrix_frame = tk.Frame(pane, padx=6, pady=6)
        pane.add(map_frame, stretch="always", minsize=520)
        pane.add(matrix_frame, width=360, minsize=300)

        hdr = tk.Frame(map_frame)
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(
            hdr,
            text="HOLOLITHIC SUB-SECTOR ASTROGRAPHY (CLICK OR DRAG PLANETS)",
            font=("Georgia", 11, "bold"),
        ).pack(side=tk.LEFT)
        tk.Button(
            hdr,
            text="+ CHART NEW WORLD",
            font=("Consolas", 9, "bold"),
            command=self.chart_new_world_from_map,
            padx=8,
        ).pack(side=tk.RIGHT)

        self.map_canvas = tk.Canvas(map_frame, bg="#050807", highlightthickness=1)
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        self.map_canvas.bind("<Configure>", lambda e: self.draw_sector_map())
        self.map_canvas.bind("<ButtonPress-1>", self.on_map_click)
        self.map_canvas.bind("<B1-Motion>", self.on_map_drag)
        self.map_canvas.bind("<ButtonRelease-1>", self.on_map_release)

        map_footer = tk.Frame(map_frame, pady=6)
        map_footer.pack(fill=tk.X)
        self.map_world_info_lbl = tk.Label(
            map_footer,
            text="SELECT A PLANETARY SYSTEM NODE ON THE AUSPEX GRID",
            font=("Consolas", 9, "bold"),
        )
        self.map_world_info_lbl.pack(side=tk.LEFT)
        tk.Button(
            map_footer,
            text="OPEN WORLD DOSSIER →",
            font=("Consolas", 9, "bold"),
            command=self.open_map_selected_world,
            padx=8,
        ).pack(side=tk.RIGHT)

        # Right side: Faction Diplomacy & Warband Relations
        tk.Label(
            matrix_frame,
            text="FACTION DIPLOMACY & WAR STANCES",
            font=("Georgia", 11, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        rel_form = tk.LabelFrame(
            matrix_frame,
            text=" LOG NEW DIPLOMATIC / WAR STANCE ",
            font=("Consolas", 8, "bold"),
            padx=6,
            pady=6,
        )
        rel_form.pack(fill=tk.X, pady=4)

        self.rel_src_var = tk.StringVar()
        self.rel_tgt_var = tk.StringVar()
        self.rel_stance_var = tk.StringVar(value="INQUISITORIAL SCRUTINY")
        self.rel_note_var = tk.StringVar()

        tk.Label(rel_form, text="SOURCE ENTITY:", font=("Consolas", 8)).pack(anchor="w")
        self.rel_src_combo = ttk.Combobox(
            rel_form, textvariable=self.rel_src_var, state="readonly"
        )
        self.rel_src_combo.pack(fill=tk.X, pady=2)

        tk.Label(rel_form, text="TARGET ENTITY:", font=("Consolas", 8)).pack(anchor="w")
        self.rel_tgt_combo = ttk.Combobox(
            rel_form, textvariable=self.rel_tgt_var, state="readonly"
        )
        self.rel_tgt_combo.pack(fill=tk.X, pady=2)

        tk.Label(rel_form, text="STANCE:", font=("Consolas", 8)).pack(anchor="w")
        ttk.Combobox(
            rel_form,
            textvariable=self.rel_stance_var,
            values=[
                "SWORN BLOOD-OATH",
                "UNEASY COALITION",
                "INQUISITORIAL SCRUTINY",
                "SHADOW WAR / RIVALRY",
                "EXCOMMUNICATE / PURGE",
            ],
            state="readonly",
        ).pack(fill=tk.X, pady=2)

        tk.Label(rel_form, text="CONTEXT NOTE:", font=("Consolas", 8)).pack(anchor="w")
        tk.Entry(rel_form, textvariable=self.rel_note_var, font=("Segoe UI", 9)).pack(
            fill=tk.X, pady=2
        )

        tk.Button(
            rel_form,
            text="+ RECORD STANCE",
            font=("Consolas", 9, "bold"),
            command=self.add_faction_relation,
             pady=3,
        ).pack(fill=tk.X, pady=(6, 2))

        self.relations_listbox = tk.Listbox(
            matrix_frame, font=("Consolas", 9), height=14
        )
        self.relations_listbox.pack(fill=tk.BOTH, expand=True, pady=4)
        tk.Button(
            matrix_frame,
            text="REMOVE SELECTED RELATION",
            font=("Consolas", 8),
            command=self.delete_selected_relation,
        ).pack(fill=tk.X)

    # -------------------------------------------------------------------------
    # TAB IV: IMPERIAL CHRONOLOGY & DATE COGITATOR
    # -------------------------------------------------------------------------
    def _build_chronology_tab(self):
        pane = tk.PanedWindow(self.tab_chronology, orient=tk.HORIZONTAL, sashwidth=5)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left_calc = tk.Frame(pane, padx=6, pady=6)
        right_annals = tk.Frame(pane, padx=8, pady=6)
        pane.add(left_calc, width=360, minsize=310)
        pane.add(right_annals, stretch="always")

        calc_box = tk.LabelFrame(
            left_calc,
            text=" IMPERIAL DATING COGITATOR (CHECK.FRAC.YEAR.Mxx) ",
            font=("Consolas", 9, "bold"),
            padx=8,
            pady=8,
        )
        calc_box.pack(fill=tk.X, pady=(0, 8))

        self.imp_check_var = tk.StringVar(value="0")
        self.imp_year_var = tk.StringVar(value="40999")
        self.imp_month_var = tk.StringVar(value="10")
        self.imp_day_var = tk.StringVar(value="21")

        for v in (
            self.imp_check_var,
            self.imp_year_var,
            self.imp_month_var,
            self.imp_day_var,
        ):
            v.trace_add("write", lambda *_: self.update_imperial_date_preview())

        tk.Label(calc_box, text="CHECK NUMBER (0-9):", font=("Consolas", 8)).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Combobox(
            calc_box,
            textvariable=self.imp_check_var,
            values=["0", "1", "3", "5", "7", "9"],
            width=10,
        ).grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(calc_box, text="CALENDAR YEAR (e.g. 40999):", font=("Consolas", 8)).grid(
            row=1, column=0, sticky="w"
        )
        tk.Entry(calc_box, textvariable=self.imp_year_var, width=12).grid(
            row=1, column=1, sticky="ew", pady=2
        )

        tk.Label(calc_box, text="MONTH (1-12):", font=("Consolas", 8)).grid(
            row=2, column=0, sticky="w"
        )
        tk.Entry(calc_box, textvariable=self.imp_month_var, width=12).grid(
            row=2, column=1, sticky="ew", pady=2
        )

        tk.Label(calc_box, text="DAY (1-31):", font=("Consolas", 8)).grid(
            row=3, column=0, sticky="w"
        )
        tk.Entry(calc_box, textvariable=self.imp_day_var, width=12).grid(
            row=3, column=1, sticky="ew", pady=2
        )

        self.computed_date_lbl = tk.Label(
            calc_box, text="0.805.999.M41", font=("Consolas", 14, "bold")
        )
        self.computed_date_lbl.grid(row=4, column=0, columnspan=2, pady=6)

        tk.Button(
            calc_box,
            text="USE TIMESTAMP IN EVENT FORM ↓",
            font=("Consolas", 8, "bold"),
            command=lambda: self.evt_date_var.set(self.computed_date_lbl.cget("text")),
        ).grid(row=5, column=0, columnspan=2, sticky="ew")

        # Add Timeline Event Box
        evt_box = tk.LabelFrame(
            left_calc,
            text=" LOG NEW SECTOR ANNALS EVENT ",
            font=("Consolas", 9, "bold"),
            padx=8,
            pady=8,
        )
        evt_box.pack(fill=tk.BOTH, expand=True)

        self.evt_date_var = tk.StringVar(value="0.812.999.M41")
        self.evt_title_var = tk.StringVar()
        self.evt_era_var = tk.StringVar(value="M42 // ERA INDOMITUS")

        tk.Label(evt_box, text="IMPERIAL DATE:", font=("Consolas", 8)).pack(anchor="w")
        tk.Entry(evt_box, textvariable=self.evt_date_var, font=("Consolas", 10)).pack(
            fill=tk.X, pady=2
        )

        tk.Label(evt_box, text="EVENT TITLE:", font=("Consolas", 8)).pack(anchor="w")
        tk.Entry(evt_box, textvariable=self.evt_title_var, font=("Segoe UI", 10)).pack(
            fill=tk.X, pady=2
        )

        tk.Label(evt_box, text="ERA:", font=("Consolas", 8)).pack(anchor="w")
        ttk.Combobox(
            evt_box,
            textvariable=self.evt_era_var,
            values=[
                "M30-M31 // GREAT CRUSADE & HERESY",
                "M32-M40 // AGE OF IMPERIUM",
                "M41 // TIME OF ENDING",
                "M42 // ERA INDOMITUS",
            ],
            state="readonly",
        ).pack(fill=tk.X, pady=2)

        tk.Label(evt_box, text="CHRONICLE DETAILS:", font=("Consolas", 8)).pack(
            anchor="w"
        )
        self.evt_desc_text = tk.Text(evt_box, height=4, wrap=tk.WORD, font=("Segoe UI", 9))
        self.evt_desc_text.pack(fill=tk.BOTH, expand=True, pady=2)

        tk.Button(
            evt_box,
            text="+ INSCRIBE INTO SECTOR ANNALS",
            font=("Consolas", 9, "bold"),
            command=self.add_timeline_event,
            pady=4,
        ).pack(fill=tk.X, pady=4)

        # Right side: Chronology List
        tk.Label(
            right_annals,
            text="SECTOR ANNALS & NARRATIVE CHRONOLOGY",
            font=("Georgia", 12, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        self.timeline_text = tk.Text(
            right_annals, wrap=tk.WORD, font=("Consolas", 10), padx=10, pady=10
        )
        self.timeline_text.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------------------
    # TAB V: LEXMECHANIC LORE & NAME FORGE
    # -------------------------------------------------------------------------
    def _build_forge_tab(self):
        top = tk.Frame(self.tab_forge, padx=10, pady=8)
        top.pack(fill=tk.X)
        tk.Label(
            top,
            text="LEXMECHANIC NOMENCLATURE & LORE FORGE",
            font=("Georgia", 12, "bold"),
        ).pack(side=tk.LEFT)
        tk.Button(
            top,
            text="⚡ CYCLE ALL COGITATOR TABLES",
            font=("Consolas", 9, "bold"),
            command=self.roll_all_forge_tables,
            padx=10,
            pady=3,
        ).pack(side=tk.RIGHT)

        self.forge_grid = tk.Frame(self.tab_forge, padx=10, pady=4)
        self.forge_grid.pack(fill=tk.BOTH, expand=True)
        for c in range(3):
            self.forge_grid.columnconfigure(c, weight=1)
        for r in range(2):
            self.forge_grid.rowconfigure(r, weight=1)

        self.forge_listboxes = {}
        keys = list(FORGE_TABLES.keys())
        for idx, k in enumerate(keys):
            tbl = FORGE_TABLES[k]
            card = tk.LabelFrame(
                self.forge_grid,
                text=f" {tbl['title'].upper()} ",
                font=("Consolas", 9, "bold"),
                padx=6,
                pady=6,
            )
            card.grid(row=idx // 3, column=idx % 3, sticky="nsew", padx=5, pady=5)

            lb = tk.Listbox(card, font=("Consolas", 10), height=6, exportselection=False)
            lb.pack(fill=tk.BOTH, expand=True, pady=4)
            self.forge_listboxes[k] = lb

            btn_row = tk.Frame(card)
            btn_row.pack(fill=tk.X)
            tk.Button(
                btn_row,
                text="↻ ROLL",
                font=("Consolas", 8, "bold"),
                command=lambda key=k: self.roll_single_forge_table(key),
            ).pack(side=tk.LEFT, padx=2)
            tk.Button(
                btn_row,
                text="COPY",
                font=("Consolas", 8),
                command=lambda key=k: self.copy_selected_forge_item(key),
            ).pack(side=tk.LEFT, padx=2)
            tk.Button(
                btn_row,
                text="+ CREATE DOSSIER",
                font=("Consolas", 8, "bold"),
                command=lambda key=k: self.create_dossier_from_forge(key),
            ).pack(side=tk.RIGHT, padx=2)

        self.roll_all_forge_tables()

    # -------------------------------------------------------------------------
    # PERSISTENT RIGHT-HAND SIDEBAR: PINNED REFERENCE SLATE & SCRATCHPAD
    # -------------------------------------------------------------------------
    def _build_reference_drawer(self):
        hdr = tk.Frame(self.right_ref_drawer, padx=8, pady=6)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr,
            text="📌 PINNED REFERENCE SLATE",
            font=("Georgia", 11, "bold"),
        ).pack(side=tk.LEFT)
        tk.Button(
            hdr,
            text="UNPIN",
            font=("Consolas", 8),
            command=self.unpin_current_ref,
            padx=6,
        ).pack(side=tk.RIGHT)

        self.pinned_combo_var = tk.StringVar()
        self.pinned_combo = ttk.Combobox(
            self.right_ref_drawer,
            textvariable=self.pinned_combo_var,
            state="readonly",
        )
        self.pinned_combo.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.pinned_combo.bind("<<ComboboxSelected>>", self.on_pinned_combo_selected)

        self.pinned_readout = tk.Text(
            self.right_ref_drawer,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            padx=8,
            pady=8,
            height=18,
        )
        self.pinned_readout.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Persistent Vox-Scratchpad
        scratch_lbl = tk.Label(
            self.right_ref_drawer,
            text="++ PERSISTENT VOX-SCRATCHPAD (AUTO-SAVED) ++",
            font=("Consolas", 8, "bold"),
        )
        scratch_lbl.pack(anchor="w", padx=8, pady=(6, 2))

        self.scratchpad_text = tk.Text(
            self.right_ref_drawer,
            height=7,
            wrap=tk.WORD,
            font=("Consolas", 9),
            padx=6,
            pady=6,
        )
        self.scratchpad_text.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.scratchpad_text.bind("<KeyRelease>", self.on_scratchpad_changed)

    # -------------------------------------------------------------------------
    # THEME ENGINE
    # -------------------------------------------------------------------------
    def apply_theme(self):
        theme_name = self.state.get("theme", "AUSPEX GREEN")
        t = THEMES.get(theme_name, THEMES["AUSPEX GREEN"])
        self.colors = t

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TNotebook", background=t["bg_void"], borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=t["bg_card"],
            foreground=t["text_muted"],
            padding=(12, 6),
            font=("Consolas", 9, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", t["bg_panel"])],
            foreground=[("selected", t["accent_bright"])],
        )
        style.configure(
            "TCombobox",
            fieldbackground=t["bg_input"],
            background=t["bg_card"],
            foreground=t["text_main"],
        )

        self._style_widget_tree(self.root, t)
        self.draw_sector_map()

    def _style_widget_tree(self, widget, t):
        wtype = widget.winfo_class()
        try:
            if wtype in ("Frame", "Labelframe", "Toplevel", "Tk"):
                widget.configure(bg=t["bg_panel"])
                if wtype == "Labelframe":
                    widget.configure(fg=t["accent_bright"])
            elif wtype == "PanedWindow":
                widget.configure(bg=t["border_dim"])
            elif wtype == "Label":
                widget.configure(bg=widget.master.cget("bg"), fg=t["text_main"])
            elif wtype == "Button":
                txt = widget.cget("text")
                if "+" in txt or "CREATE DESKTOP" in txt or "EXPORT" in txt:
                    widget.configure(
                        bg=t["accent_main"],
                        fg="#050807",
                        activebackground=t["accent_bright"],
                        relief=tk.FLAT,
                    )
                elif "PURGE" in txt or "DELETE" in txt:
                    widget.configure(
                        bg=t["bg_card"],
                        fg=t["danger"],
                        activebackground=t["danger"],
                        relief=tk.GROOVE,
                    )
                else:
                    widget.configure(
                        bg=t["bg_card"],
                        fg=t["accent_bright"],
                        activebackground=t["border_dim"],
                        relief=tk.GROOVE,
                    )
            elif wtype in ("Entry", "Text", "Listbox"):
                widget.configure(
                    bg=t["bg_input"],
                    fg=t["text_main"],
                    insertbackground=t["accent_bright"],
                    selectbackground=t["accent_main"],
                    selectforeground="#050807",
                    highlightbackground=t["border_dim"],
                    highlightcolor=t["accent_main"],
                )
        except Exception:
            pass

        for child in widget.winfo_children():
            self._style_widget_tree(child, t)

    def on_theme_changed(self, _event=None):
        self.state["theme"] = self.theme_var.get()
        self.apply_theme()
        self.save_state()

    # -------------------------------------------------------------------------
    # VIEW REFRESH & SYNCHRONIZATION
    # -------------------------------------------------------------------------
    def refresh_all_views(self):
        self._is_loading_ui = True
        try:
            proj = self.get_active_project()
            # Project selector
            proj_names = [p["name"] for p in self.state["projects"]]
            self.project_combo["values"] = proj_names
            self.project_var.set(proj["name"])

            # Scratchpad
            self.scratchpad_text.delete("1.0", tk.END)
            self.scratchpad_text.insert("1.0", proj.get("scratchpad", ""))

            self.refresh_codex_list()
            self.load_active_entry_into_editor()
            self.refresh_scriptorium_view()
            self.refresh_pinned_drawer()
            self.draw_sector_map()
            self.refresh_relations_view()
            self.refresh_chronology_view()
            self.update_telemetry_counts()
        finally:
            self._is_loading_ui = False

    def update_telemetry_counts(self):
        proj = self.get_active_project()
        total_words = 0
        for e in proj["entries"]:
            total_words += count_words(e.get("body", ""))
            for v in e.get("compartments", {}).values():
                total_words += count_words(v)
        for s in proj["scenes"]:
            total_words += count_words(s.get("content", ""))

        self.telemetry_stats_lbl.config(
            text=f"{len(proj['entries'])} Dossiers • {len(proj['scenes'])} Scenes • {total_words:,} Words"
        )

    # -------------------------------------------------------------------------
    # CODEX LOGIC
    # -------------------------------------------------------------------------
    def set_category_filter(self, cat_id: str):
        self.state["activeCategoryFilter"] = cat_id
        self.refresh_codex_list()
        self.save_state()

    def set_allegiance_filter(self, alleg: str):
        self.state["activeAllegianceFilter"] = alleg
        self.refresh_codex_list()
        self.save_state()

    def get_filtered_entries(self):
        proj = self.get_active_project()
        cat = self.state.get("activeCategoryFilter", "all")
        alleg = self.state.get("activeAllegianceFilter", "ALL")
        q = self.codex_search_var.get().strip().lower()

        results = []
        for e in proj["entries"]:
            if cat != "all" and e.get("category") != cat:
                continue
            if alleg != "ALL" and e.get("allegiance") != alleg:
                continue
            if q:
                blob = " ".join(
                    [
                        e.get("title", ""),
                        e.get("subtitle", ""),
                        e.get("body", ""),
                        " ".join(e.get("tags", [])),
                        " ".join(e.get("fields", {}).values()),
                        " ".join(e.get("compartments", {}).values()),
                    ]
                ).lower()
                if q not in blob:
                    continue
            results.append(e)
        return results

    def refresh_codex_list(self):
        self.filtered_entries = self.get_filtered_entries()
        self.codex_listbox.delete(0, tk.END)
        sel_idx = 0
        for idx, e in enumerate(self.filtered_entries):
            star = "★ " if e.get("starred") else "  "
            pin = "📌" if e["id"] in self.state.get("pinnedReferenceIds", []) else ""
            cat_short = CATEGORY_SCHEMA.get(e.get("category", "factions"), {}).get(
                "short", "DOC"
            )
            self.codex_listbox.insert(
                tk.END, f"{star}[{cat_short}] {e.get('title', 'Untitled')} {pin}"
            )
            if e["id"] == self.state.get("selectedEntryId"):
                sel_idx = idx

        if self.filtered_entries:
            self.codex_listbox.selection_set(sel_idx)
        self.codex_list_heading.config(
            text=f"DATABANK DOSSIERS ({len(self.filtered_entries)})"
        )

    def on_codex_listbox_select(self, _event=None):
        if self._is_loading_ui:
            return
        sel = self.codex_listbox.curselection()
        if not sel or sel[0] >= len(self.filtered_entries):
            return
        chosen = self.filtered_entries[sel[0]]
        self.state["selectedEntryId"] = chosen["id"]
        self.state["lastEditedPointer"] = {
            "type": "codex",
            "id": chosen["id"],
            "title": chosen.get("title", ""),
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self.load_active_entry_into_editor()
        self.save_state()

    def load_active_entry_into_editor(self):
        entry = self.get_active_entry()
        if not entry:
            return
        self._is_loading_ui = True
        try:
            cat = entry.get("category", "factions")
            schema = CATEGORY_SCHEMA.get(cat, CATEGORY_SCHEMA["factions"])

            self.entry_cat_var.set(cat)
            self.entry_alleg_var.set(entry.get("allegiance", "IMPERIUM"))
            self.entry_clear_var.set(entry.get("clearance", "VERMILION"))
            self.entry_title_var.set(entry.get("title", ""))
            self.entry_sub_var.set(entry.get("subtitle", ""))
            self.entry_epi_var.set(entry.get("epigraph", ""))
            self.entry_tags_var.set(", ".join(entry.get("tags", [])))

            # Rebuild dynamic 6 telemetry fields
            for child in self.specs_frame.winfo_children():
                child.destroy()
            self.spec_entries.clear()

            fields_data = entry.setdefault("fields", {})
            for idx, (fkey, flabel) in enumerate(schema["fields"]):
                cell = tk.Frame(self.specs_frame, bg=self.colors["bg_panel"])
                cell.grid(row=idx // 3, column=idx % 3, sticky="ew", padx=4, pady=2)
                tk.Label(
                    cell,
                    text=flabel.upper(),
                    font=("Consolas", 8),
                    bg=self.colors["bg_panel"],
                    fg=self.colors["text_muted"],
                ).pack(anchor="w")
                sv = tk.StringVar(value=fields_data.get(fkey, ""))
                sv.trace_add("write", lambda *_: self.on_entry_text_changed())
                ent_w = tk.Entry(
                    cell,
                    textvariable=sv,
                    font=("Consolas", 9),
                    bg=self.colors["bg_input"],
                    fg=self.colors["text_main"],
                    insertbackground=self.colors["accent_bright"],
                )
                ent_w.pack(fill=tk.X)
                self.spec_entries[fkey] = sv

            # Rebuild 4 Structured Worldbuilding Compartments
            for child in self.comp_frame.winfo_children():
                child.destroy()
            self.compartment_texts.clear()

            comp_data = entry.setdefault("compartments", {})
            for idx, (ckey, ctitle) in enumerate(schema["compartments"]):
                box = tk.Frame(self.comp_frame, bg=self.colors["bg_panel"])
                box.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=4, pady=3)
                tk.Label(
                    box,
                    text=ctitle,
                    font=("Consolas", 8, "bold"),
                    bg=self.colors["bg_panel"],
                    fg=self.colors["accent_bright"],
                ).pack(anchor="w")
                tw = tk.Text(
                    box,
                    height=4,
                    wrap=tk.WORD,
                    font=("Segoe UI", 9),
                    bg=self.colors["bg_input"],
                    fg=self.colors["text_main"],
                    insertbackground=self.colors["accent_bright"],
                )
                tw.pack(fill=tk.BOTH, expand=True)
                tw.insert("1.0", comp_data.get(ckey, ""))
                tw.bind("<KeyRelease>", lambda e: self.on_entry_text_changed())
                self.compartment_texts[ckey] = tw

            # Body
            self.codex_body_text.delete("1.0", tk.END)
            self.codex_body_text.insert("1.0", entry.get("body", ""))

            self._update_entry_word_badge(entry)
        finally:
            self._is_loading_ui = False

    def _update_entry_word_badge(self, entry):
        w = count_words(entry.get("body", ""))
        for v in entry.get("compartments", {}).values():
            w += count_words(v)
        self.entry_word_count_lbl.config(text=f"{w:,} words in dossier")

    def on_entry_meta_changed(self, _event=None):
        if self._is_loading_ui:
            return
        entry = self.get_active_entry()
        if not entry:
            return
        old_cat = entry.get("category")
        entry["category"] = self.entry_cat_var.get()
        entry["allegiance"] = self.entry_alleg_var.get()
        entry["clearance"] = self.entry_clear_var.get()
        if entry["category"] != old_cat:
            self.load_active_entry_into_editor()
        self.refresh_codex_list()
        self.refresh_pinned_drawer()
        self.save_state()

    def on_entry_text_changed(self):
        if self._is_loading_ui:
            return
        entry = self.get_active_entry()
        if not entry:
            return
        entry["title"] = self.entry_title_var.get()
        entry["subtitle"] = self.entry_sub_var.get()
        entry["epigraph"] = self.entry_epi_var.get()
        entry["tags"] = [
            t.strip() for t in self.entry_tags_var.get().split(",") if t.strip()
        ]
        for fkey, sv in self.spec_entries.items():
            entry["fields"][fkey] = sv.get()
        for ckey, tw in self.compartment_texts.items():
            entry["compartments"][ckey] = tw.get("1.0", "end-1c")
        entry["body"] = self.codex_body_text.get("1.0", "end-1c")
        entry["updatedAt"] = int(time.time())

        self.state["lastEditedPointer"] = {
            "type": "codex",
            "id": entry["id"],
            "title": entry["title"],
            "timestamp": time.strftime("%H:%M:%S"),
        }

        self._update_entry_word_badge(entry)
        self.refresh_codex_list()
        self.refresh_pinned_drawer()
        self.update_telemetry_counts()
        self.save_state()

    def create_new_codex_entry(self, preset_cat=None):
        proj = self.get_active_project()
        cat = preset_cat or (
            self.state.get("activeCategoryFilter")
            if self.state.get("activeCategoryFilter") != "all"
            else "factions"
        )
        schema = CATEGORY_SCHEMA.get(cat, CATEGORY_SCHEMA["factions"])
        new_id = f"ent_{int(time.time() * 1000)}"
        new_entry = {
            "id": new_id,
            "category": cat,
            "allegiance": "IMPERIUM",
            "clearance": "VERMILION",
            "starred": False,
            "title": f"New {schema['short']} Dossier",
            "subtitle": proj.get("sector", "Segmentum Obscurus"),
            "epigraph": '"++ Data-Inquisition Record Initialized ++"',
            "tags": [schema["short"].lower()],
            "updatedAt": int(time.time()),
            "coords": {
                "x": random.randint(20, 80),
                "y": random.randint(20, 80),
            },
            "fields": {},
            "compartments": {"sec1": "", "sec2": "", "sec3": "", "sec4": ""},
            "body": "",
        }
        proj["entries"].insert(0, new_entry)
        self.state["selectedEntryId"] = new_id
        self.refresh_codex_list()
        self.load_active_entry_into_editor()
        self.save_state()

    def toggle_star_active_entry(self):
        entry = self.get_active_entry()
        if not entry:
            return
        entry["starred"] = not entry.get("starred", False)
        self.refresh_codex_list()
        self.save_state()

    def delete_active_entry(self):
        proj = self.get_active_project()
        entry = self.get_active_entry()
        if not entry or len(proj["entries"]) <= 1:
            return
        if messagebox.askyesno(
            "++ CONFIRM DATA PURGE ++",
            f"Purge dossier '{entry.get('title')}' from the cogitator databanks?",
        ):
            proj["entries"] = [e for e in proj["entries"] if e["id"] != entry["id"]]
            self.state["selectedEntryId"] = proj["entries"][0]["id"]
            self.refresh_all_views()
            self.save_state()

    def roll_epigraph_for_active_entry(self):
        q = random.choice(FORGE_TABLES["epigraphs"]["quotes"])
        self.entry_epi_var.set(q)
        self.on_entry_text_changed()

    # -------------------------------------------------------------------------
    # PINNED REFERENCE SLATE & SCRATCHPAD
    # -------------------------------------------------------------------------
    def pin_active_entry(self):
        entry = self.get_active_entry()
        if not entry:
            return
        self.pin_entry_by_id(entry["id"])

    def pin_entry_by_id(self, entry_id: str):
        pins = self.state.setdefault("pinnedReferenceIds", [])
        if entry_id not in pins:
            pins.insert(0, entry_id)
        self.state["activeRefId"] = entry_id
        self.refresh_pinned_drawer()
        self.refresh_codex_list()
        self.save_state()

    def unpin_current_ref(self):
        ref_id = self.state.get("activeRefId")
        pins = self.state.get("pinnedReferenceIds", [])
        if ref_id in pins:
            pins.remove(ref_id)
        self.state["activeRefId"] = pins[0] if pins else None
        self.refresh_pinned_drawer()
        self.refresh_codex_list()
        self.save_state()

    def on_pinned_combo_selected(self, _event=None):
        idx = self.pinned_combo.current()
        pins = self.state.get("pinnedReferenceIds", [])
        if 0 <= idx < len(pins):
            self.state["activeRefId"] = pins[idx]
            self.refresh_pinned_drawer()
            self.save_state()

    def refresh_pinned_drawer(self):
        proj = self.get_active_project()
        valid_ids = {e["id"]: e for e in proj["entries"]}
        pins = [
            pid for pid in self.state.get("pinnedReferenceIds", []) if pid in valid_ids
        ]
        self.state["pinnedReferenceIds"] = pins

        self.pinned_readout.config(state=tk.NORMAL)
        self.pinned_readout.delete("1.0", tk.END)

        if not pins:
            self.pinned_combo["values"] = []
            self.pinned_combo_var.set("-- No Pinned Dossiers --")
            self.pinned_readout.insert(
                "1.0",
                "No dossiers currently pinned.\n\nClick '📌 PIN TO SLATE' on any "
                "Faction, World, Character, or Wargear dossier to keep it open "
                "side-by-side while writing in the Scriptorium!",
            )
            self.pinned_readout.config(state=tk.DISABLED)
            return

        if self.state.get("activeRefId") not in pins:
            self.state["activeRefId"] = pins[0]

        titles = [valid_ids[pid]["title"] for pid in pins]
        self.pinned_combo["values"] = titles
        active_ent = valid_ids[self.state["activeRefId"]]
        self.pinned_combo_var.set(active_ent["title"])

        schema = CATEGORY_SCHEMA.get(
            active_ent.get("category", "factions"), CATEGORY_SCHEMA["factions"]
        )
        lines = [
            f"=== {active_ent.get('title', '').upper()} ===",
            f"{active_ent.get('subtitle', '')}",
            f"[{schema['short']} • {active_ent.get('allegiance', 'IMPERIUM')} • CLEARANCE: {active_ent.get('clearance', 'VERMILION')}]",
            "",
        ]
        if active_ent.get("epigraph"):
            lines.append(f"{active_ent['epigraph']}\n")

        for fkey, flabel in schema["fields"]:
            val = active_ent.get("fields", {}).get(fkey, "")
            if val:
                lines.append(f"• {flabel}: {val}")
        lines.append("")

        for ckey, ctitle in schema["compartments"]:
            val = active_ent.get("compartments", {}).get(ckey, "")
            if val:
                lines.append(f"--- {ctitle} ---")
                lines.append(val)
                lines.append("")

        if active_ent.get("body"):
            lines.append("--- EXTENDED CHRONICLE ---")
            lines.append(active_ent["body"])

        self.pinned_readout.insert("1.0", "\n".join(lines))
        self.pinned_readout.config(state=tk.DISABLED)

    def on_scratchpad_changed(self, _event=None):
        if self._is_loading_ui:
            return
        proj = self.get_active_project()
        proj["scratchpad"] = self.scratchpad_text.get("1.0", "end-1c")
        self.save_state()

    # -------------------------------------------------------------------------
    # SCRIPTORIUM LOGIC
    # -------------------------------------------------------------------------
    def refresh_scriptorium_view(self):
        proj = self.get_active_project()
        self.scene_listbox.delete(0, tk.END)

        ms_words = 0
        sel_idx = 0
        for idx, s in enumerate(proj["scenes"]):
            wc = count_words(s.get("content", ""))
            ms_words += wc
            self.scene_listbox.insert(
                tk.END, f"0{idx + 1}. {s.get('title', 'Untitled')} ({wc}w)"
            )
            if s["id"] == self.state.get("activeSceneId"):
                sel_idx = idx

        if proj["scenes"]:
            self.scene_listbox.selection_set(sel_idx)

        goal = proj.get("wordGoal", 15000)
        self.ms_progress_lbl.config(
            text=f"TOTAL MANUSCRIPT WORDS: {ms_words:,} / {goal:,}"
        )
        self.load_active_scene_into_editor()

    def on_scene_listbox_select(self, _event=None):
        if self._is_loading_ui:
            return
        proj = self.get_active_project()
        sel = self.scene_listbox.curselection()
        if not sel or sel[0] >= len(proj["scenes"]):
            return
        scn = proj["scenes"][sel[0]]
        self.state["activeSceneId"] = scn["id"]
        self.state["lastEditedPointer"] = {
            "type": "scene",
            "id": scn["id"],
            "title": scn.get("title", ""),
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self.load_active_scene_into_editor()
        self.save_state()

    def load_active_scene_into_editor(self):
        proj = self.get_active_project()
        scn = self.get_active_scene()
        if not scn:
            return
        self._is_loading_ui = True
        try:
            self.scene_status_var.set(scn.get("status", "FIRST DRAFT"))
            self.scene_date_var.set(scn.get("imperialDate", ""))
            self.scene_title_var.set(scn.get("title", ""))
            self.scene_epi_var.set(scn.get("epigraph", ""))

            chars = [e for e in proj["entries"] if e.get("category") == "characters"]
            worlds = [e for e in proj["entries"] if e.get("category") == "worlds"]

            self.scene_pov_combo["values"] = ["-- Unassigned --"] + [
                c["title"] for c in chars
            ]
            self.scene_loc_combo["values"] = ["-- Unassigned --"] + [
                w["title"] for w in worlds
            ]

            pov_ent = next(
                (c for c in chars if c["id"] == scn.get("povEntryId")), None
            )
            loc_ent = next(
                (w for w in worlds if w["id"] == scn.get("locationEntryId")), None
            )
            self.scene_pov_var.set(pov_ent["title"] if pov_ent else "-- Unassigned --")
            self.scene_loc_var.set(loc_ent["title"] if loc_ent else "-- Unassigned --")

            self.scene_syn_text.delete("1.0", tk.END)
            self.scene_syn_text.insert("1.0", scn.get("synopsis", ""))

            self.scene_prose_text.delete("1.0", tk.END)
            self.scene_prose_text.insert("1.0", scn.get("content", ""))

            wc = count_words(scn.get("content", ""))
            self.scene_wc_lbl.config(text=f"{wc:,} words (~{max(1, math.ceil(wc / 220))} min read)")
        finally:
            self._is_loading_ui = False

    def on_scene_changed(self, _event=None):
        if self._is_loading_ui:
            return
        proj = self.get_active_project()
        scn = self.get_active_scene()
        if not scn:
            return

        scn["status"] = self.scene_status_var.get()
        scn["imperialDate"] = self.scene_date_var.get()
        scn["title"] = self.scene_title_var.get()
        scn["epigraph"] = self.scene_epi_var.get()
        scn["synopsis"] = self.scene_syn_text.get("1.0", "end-1c")
        scn["content"] = self.scene_prose_text.get("1.0", "end-1c")

        for e in proj["entries"]:
            if e.get("category") == "characters" and e["title"] == self.scene_pov_var.get():
                scn["povEntryId"] = e["id"]
            if e.get("category") == "worlds" and e["title"] == self.scene_loc_var.get():
                scn["locationEntryId"] = e["id"]

        wc = count_words(scn["content"])
        self.scene_wc_lbl.config(
            text=f"{wc:,} words (~{max(1, math.ceil(wc / 220))} min read)"
        )

        self.state["lastEditedPointer"] = {
            "type": "scene",
            "id": scn["id"],
            "title": scn["title"],
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self.update_telemetry_counts()
        self.save_state()

    def pin_scene_pov_and_world(self):
        scn = self.get_active_scene()
        if not scn:
            return
        if scn.get("locationEntryId"):
            self.pin_entry_by_id(scn["locationEntryId"])
        if scn.get("povEntryId"):
            self.pin_entry_by_id(scn["povEntryId"])

    def create_new_scene(self):
        proj = self.get_active_project()
        num = len(proj["scenes"]) + 1
        new_scn = {
            "id": f"scn_{int(time.time() * 1000)}",
            "title": f"Chapter {num}: New Tactical Scene",
            "status": "OUTLINE",
            "imperialDate": "0.815.999.M41",
            "povEntryId": "",
            "locationEntryId": "",
            "epigraph": '"++ Thought for the Day: Victory needs no explanation. ++"',
            "synopsis": "",
            "content": "",
            "updatedAt": int(time.time()),
        }
        proj["scenes"].append(new_scn)
        self.state["activeSceneId"] = new_scn["id"]
        self.refresh_scriptorium_view()
        self.save_state()

    def delete_active_scene(self):
        proj = self.get_active_project()
        scn = self.get_active_scene()
        if not scn or len(proj["scenes"]) <= 1:
            return
        if messagebox.askyesno("Delete Scene", f"Delete scene '{scn.get('title')}'?"):
            proj["scenes"] = [s for s in proj["scenes"] if s["id"] != scn["id"]]
            self.state["activeSceneId"] = proj["scenes"][0]["id"]
            self.refresh_scriptorium_view()
            self.save_state()

    # -------------------------------------------------------------------------
    # ASTROGRAPHY SECTOR MAP & FACTION MATRIX
    # -------------------------------------------------------------------------
    def draw_sector_map(self):
        if not hasattr(self, "map_canvas"):
            return
        c = self.map_canvas
        c.delete("all")
        w = max(400, c.winfo_width())
        h = max(300, c.winfo_height())

        # Auspex Grid
        for gx in range(0, w, 60):
            c.create_line(gx, 0, gx, h, fill="#11261e")
        for gy in range(0, h, 60):
            c.create_line(0, gy, w, gy, fill="#11261e")

        proj = self.get_active_project()
        worlds = [e for e in proj["entries"] if e.get("category") == "worlds"]

        # Warp Routes between worlds
        for i in range(len(worlds) - 1):
            w1, w2 = worlds[i], worlds[i + 1]
            x1 = (w1.get("coords", {}).get("x", 50) / 100.0) * w
            y1 = (w1.get("coords", {}).get("y", 50) / 100.0) * h
            x2 = (w2.get("coords", {}).get("x", 50) / 100.0) * w
            y2 = (w2.get("coords", {}).get("y", 50) / 100.0) * h
            c.create_line(x1, y1, x2, y2, fill="#b45309", dash=(6, 4), width=2)

        # Draw Planetary Nodes
        sel_id = self.state.get("mapSelectedWorldId")
        for world in worlds:
            coords = world.setdefault("coords", {"x": 50, "y": 50})
            px = (coords["x"] / 100.0) * w
            py = (coords["y"] / 100.0) * h
            col = (
                "#f43f5e"
                if world.get("allegiance") == "CHAOS"
                else self.colors["accent_main"]
            )

            if world["id"] == sel_id:
                c.create_oval(
                    px - 22,
                    py - 22,
                    px + 22,
                    py + 22,
                    outline="#fbbf24",
                    dash=(3, 2),
                    width=2,
                )
            c.create_oval(
                px - 13,
                py - 13,
                px + 13,
                py + 13,
                fill="#070b09",
                outline=col,
                width=2,
            )
            c.create_oval(px - 5, py - 5, px + 5, py + 5, fill=col, outline="")
            c.create_text(
                px,
                py + 24,
                text=world.get("title", "World"),
                fill="#f8fafc",
                font=("Consolas", 9, "bold"),
            )

        sel_w = next((x for x in worlds if x["id"] == sel_id), None)
        if sel_w:
            pclass = sel_w.get("fields", {}).get("planetClass", "Unspecified Class")
            tithe = sel_w.get("fields", {}).get("titheGrade", "N/A")
            self.map_world_info_lbl.config(
                text=f"SELECTED: {sel_w['title']} [{sel_w.get('allegiance')}] • {pclass} • Tithe: {tithe}"
            )

    def on_map_click(self, event):
        proj = self.get_active_project()
        worlds = [e for e in proj["entries"] if e.get("category") == "worlds"]
        w = max(400, self.map_canvas.winfo_width())
        h = max(300, self.map_canvas.winfo_height())

        for world in worlds:
            px = (world.get("coords", {}).get("x", 50) / 100.0) * w
            py = (world.get("coords", {}).get("y", 50) / 100.0) * h
            if math.hypot(event.x - px, event.y - py) <= 22:
                self.state["mapSelectedWorldId"] = world["id"]
                self._dragging_world_id = world["id"]
                self.draw_sector_map()
                return

    def on_map_drag(self, event):
        if not self._dragging_world_id:
            return
        proj = self.get_active_project()
        world = next(
            (e for e in proj["entries"] if e["id"] == self._dragging_world_id), None
        )
        if not world:
            return
        w = max(400, self.map_canvas.winfo_width())
        h = max(300, self.map_canvas.winfo_height())
        nx = max(8, min(92, int((event.x / w) * 100)))
        ny = max(10, min(88, int((event.y / h) * 100)))
        world["coords"] = {"x": nx, "y": ny}
        self.draw_sector_map()

    def on_map_release(self, _event):
        if self._dragging_world_id:
            self._dragging_world_id = None
            self.save_state()

    def open_map_selected_world(self):
        wid = self.state.get("mapSelectedWorldId")
        if wid:
            self.state["selectedEntryId"] = wid
            self.notebook.select(0)
            self.refresh_codex_list()
            self.load_active_entry_into_editor()

    def chart_new_world_from_map(self):
        self.create_new_codex_entry(preset_cat="worlds")
        self.notebook.select(0)

    def refresh_relations_view(self):
        proj = self.get_active_project()
        titles = [e["title"] for e in proj["entries"]]
        self.rel_src_combo["values"] = titles
        self.rel_tgt_combo["values"] = titles
        if titles and not self.rel_src_var.get():
            self.rel_src_var.set(titles[0])
        if len(titles) > 1 and not self.rel_tgt_var.get():
            self.rel_tgt_var.set(titles[1])

        self.relations_listbox.delete(0, tk.END)
        id_map = {e["id"]: e["title"] for e in proj["entries"]}
        for rel in proj.get("relations", []):
            s = id_map.get(rel.get("sourceId"), rel.get("sourceId", "Entity"))
            t = id_map.get(rel.get("targetId"), rel.get("targetId", "Entity"))
            self.relations_listbox.insert(
                tk.END, f"[{rel.get('stance')}] {s} ⇄ {t} — {rel.get('note', '')}"
            )

    def add_faction_relation(self):
        proj = self.get_active_project()
        title_map = {e["title"]: e["id"] for e in proj["entries"]}
        s_id = title_map.get(self.rel_src_var.get())
        t_id = title_map.get(self.rel_tgt_var.get())
        if not s_id or not t_id:
            return
        proj.setdefault("relations", []).insert(
            0,
            {
                "id": f"rel_{int(time.time() * 1000)}",
                "sourceId": s_id,
                "targetId": t_id,
                "stance": self.rel_stance_var.get(),
                "note": self.rel_note_var.get().strip(),
            },
        )
        self.rel_note_var.set("")
        self.refresh_relations_view()
        self.save_state()

    def delete_selected_relation(self):
        proj = self.get_active_project()
        sel = self.relations_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(proj.get("relations", [])):
            proj["relations"].pop(idx)
            self.refresh_relations_view()
            self.save_state()

    # -------------------------------------------------------------------------
    # CHRONOLOGY & IMPERIAL DATE CALCULATOR
    # -------------------------------------------------------------------------
    def update_imperial_date_preview(self):
        try:
            stamp = compute_imperial_date(
                int(self.imp_check_var.get() or 0),
                int(self.imp_year_var.get() or 40999),
                int(self.imp_month_var.get() or 10),
                int(self.imp_day_var.get() or 21),
            )
            self.computed_date_lbl.config(text=stamp)
        except Exception:
            pass

    def refresh_chronology_view(self):
        proj = self.get_active_project()
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete("1.0", tk.END)
        for ev in proj.get("timeline", []):
            self.timeline_text.insert(
                tk.END,
                f"++ [{ev.get('imperialDate', '')}]  {ev.get('era', '')} ++\n"
                f"   {ev.get('title', '')}\n"
                f"   {ev.get('desc', '')}\n\n",
            )
        self.timeline_text.config(state=tk.DISABLED)

    def add_timeline_event(self):
        title = self.evt_title_var.get().strip()
        if not title:
            return
        proj = self.get_active_project()
        proj.setdefault("timeline", []).append(
            {
                "id": f"evt_{int(time.time() * 1000)}",
                "imperialDate": self.evt_date_var.get().strip() or "0.815.999.M41",
                "era": self.evt_era_var.get(),
                "title": title,
                "desc": self.evt_desc_text.get("1.0", "end-1c").strip(),
            }
        )
        self.evt_title_var.set("")
        self.evt_desc_text.delete("1.0", tk.END)
        self.refresh_chronology_view()
        self.save_state()

    # -------------------------------------------------------------------------
    # LEXMECHANIC LORE & NAME FORGE
    # -------------------------------------------------------------------------
    def roll_single_forge_table(self, key: str):
        tbl = FORGE_TABLES[key]
        items = []
        for _ in range(6):
            if key == "epigraphs":
                items.append((random.choice(tbl["quotes"]), "Epigraph"))
            else:
                name = f"{random.choice(tbl['first'])} {random.choice(tbl['second'])}"
                sub = random.choice(tbl["epithet"])
                items.append((name, sub))
        self.forge_results[key] = items
        lb = self.forge_listboxes.get(key)
        if lb:
            lb.delete(0, tk.END)
            for name, sub in items:
                lb.insert(tk.END, f"{name}  [{sub}]")
            lb.selection_set(0)

    def roll_all_forge_tables(self):
        for k in FORGE_TABLES:
            self.roll_single_forge_table(k)

    def copy_selected_forge_item(self, key: str):
        lb = self.forge_listboxes.get(key)
        if not lb:
            return
        sel = lb.curselection()
        idx = sel[0] if sel else 0
        items = self.forge_results.get(key, [])
        if 0 <= idx < len(items):
            self.root.clipboard_clear()
            self.root.clipboard_append(items[idx][0])

    def create_dossier_from_forge(self, key: str):
        lb = self.forge_listboxes.get(key)
        if not lb:
            return
        sel = lb.curselection()
        idx = sel[0] if sel else 0
        items = self.forge_results.get(key, [])
        if not (0 <= idx < len(items)):
            return
        name, sub = items[idx]
        cat = FORGE_TABLES[key]["category"]
        proj = self.get_active_project()
        new_id = f"ent_{int(time.time() * 1000)}"
        proj["entries"].insert(
            0,
            {
                "id": new_id,
                "category": cat,
                "allegiance": "IMPERIUM",
                "clearance": "VERMILION",
                "starred": False,
                "title": "Inquisitorial Vox-Excerpt" if key == "epigraphs" else name,
                "subtitle": sub,
                "epigraph": (
                    name
                    if key == "epigraphs"
                    else random.choice(FORGE_TABLES["epigraphs"]["quotes"])
                ),
                "tags": ["Forge Generated", cat],
                "updatedAt": int(time.time()),
                "coords": {
                    "x": random.randint(20, 80),
                    "y": random.randint(20, 80),
                },
                "fields": {},
                "compartments": {"sec1": "", "sec2": "", "sec3": "", "sec4": ""},
                "body": "",
            },
        )
        self.state["selectedEntryId"] = new_id
        self.notebook.select(0)
        self.refresh_codex_list()
        self.load_active_entry_into_editor()
        self.save_state()

    # -------------------------------------------------------------------------
    # PROJECT & EXPORT DIALOGS
    # -------------------------------------------------------------------------
    def on_main_tab_changed(self, _event=None):
        if self._is_loading_ui:
            return
        try:
            self.state["activeMainTab"] = self.notebook.index(self.notebook.select())
            if self.state["activeMainTab"] == 2:
                self.draw_sector_map()
            self.save_state(quiet=True)
        except Exception:
            pass

    def jump_to_last_edited(self):
        ptr = self.state.get("lastEditedPointer", {})
        if ptr.get("type") == "scene":
            self.state["activeSceneId"] = ptr.get("id")
            self.notebook.select(1)
            self.refresh_scriptorium_view()
        else:
            self.state["selectedEntryId"] = ptr.get("id")
            self.notebook.select(0)
            self.refresh_codex_list()
            self.load_active_entry_into_editor()

    def on_project_switched(self, _event=None):
        chosen_name = self.project_var.get()
        for p in self.state["projects"]:
            if p["name"] == chosen_name:
                self.state["activeProjectId"] = p["id"]
                self.state["selectedEntryId"] = (
                    p["entries"][0]["id"] if p["entries"] else None
                )
                self.state["activeSceneId"] = (
                    p["scenes"][0]["id"] if p["scenes"] else None
                )
                break
        self.refresh_all_views()
        self.save_state()

    def open_new_project_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Initialize New 40K Crusade / Worldbuilding Project")
        dlg.geometry("460x320")
        dlg.transient(self.root)
        dlg.grab_set()
        self._style_widget_tree(dlg, self.colors)

        f = tk.Frame(dlg, padx=14, pady=14, bg=self.colors["bg_panel"])
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            f,
            text="PROJECT / CRUSADE / NOVEL TITLE:",
            font=("Consolas", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["accent_bright"],
        ).pack(anchor="w")
        name_v = tk.StringVar(value="Chronicles of Sector Kaligari")
        tk.Entry(f, textvariable=name_v, font=("Segoe UI", 10)).pack(
            fill=tk.X, pady=(2, 8)
        )

        tk.Label(
            f,
            text="SECTOR / THEATRE:",
            font=("Consolas", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["accent_bright"],
        ).pack(anchor="w")
        sec_v = tk.StringVar(value="Segmentum Obscurus")
        tk.Entry(f, textvariable=sec_v, font=("Consolas", 10)).pack(
            fill=tk.X, pady=(2, 8)
        )

        tk.Label(
            f,
            text="ERA / MILLENNIUM:",
            font=("Consolas", 9, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["accent_bright"],
        ).pack(anchor="w")
        era_v = tk.StringVar(value="Era Indomitus • M42")
        tk.Entry(f, textvariable=era_v, font=("Consolas", 10)).pack(
            fill=tk.X, pady=(2, 12)
        )

        def _create():
            pid = f"proj_{int(time.time() * 1000)}"
            eid = f"ent_{int(time.time() * 1000)}"
            sid = f"scn_{int(time.time() * 1000)}"
            new_p = {
                "id": pid,
                "name": name_v.get().strip() or "New 40K Project",
                "sector": sec_v.get().strip(),
                "era": era_v.get().strip(),
                "wordGoal": 15000,
                "description": "Custom 40K worldbuilding and writing project.",
                "scratchpad": "++ VOX-SCRATCHPAD ++\n",
                "entries": [
                    {
                        "id": eid,
                        "category": "factions",
                        "allegiance": "IMPERIUM",
                        "clearance": "VERMILION",
                        "starred": True,
                        "title": "Order / Chapter Prime",
                        "subtitle": sec_v.get().strip(),
                        "epigraph": '"Only in death does duty end."',
                        "tags": ["Primary Faction"],
                        "updatedAt": int(time.time()),
                        "coords": {"x": 50, "y": 50},
                        "fields": {},
                        "compartments": {"sec1": "", "sec2": "", "sec3": "", "sec4": ""},
                        "body": "",
                    }
                ],
                "scenes": [
                    {
                        "id": sid,
                        "title": "Chapter I: Planetfall",
                        "status": "OUTLINE",
                        "imperialDate": "0.100.001.M42",
                        "povEntryId": "",
                        "locationEntryId": "",
                        "epigraph": '"In the grim darkness of the far future, there is only war."',
                        "synopsis": "",
                        "content": "",
                        "updatedAt": int(time.time()),
                    }
                ],
                "relations": [],
                "timeline": [],
            }
            self.state["projects"].append(new_p)
            self.state["activeProjectId"] = pid
            self.state["selectedEntryId"] = eid
            self.state["activeSceneId"] = sid
            self.refresh_all_views()
            self.save_state()
            dlg.destroy()

        tk.Button(
            f,
            text="CONSECRATE NEW PROJECT",
            font=("Consolas", 10, "bold"),
            bg=self.colors["accent_main"],
            fg="#050807",
            command=_create,
            pady=6,
        ).pack(fill=tk.X)

    def open_project_settings_dialog(self):
        proj = self.get_active_project()
        dlg = tk.Toplevel(self.root)
        dlg.title("Project Telemetry Configuration")
        dlg.geometry("460x320")
        dlg.transient(self.root)
        dlg.grab_set()

        f = tk.Frame(dlg, padx=14, pady=14, bg=self.colors["bg_panel"])
        f.pack(fill=tk.BOTH, expand=True)

        name_v = tk.StringVar(value=proj.get("name", ""))
        sec_v = tk.StringVar(value=proj.get("sector", ""))
        goal_v = tk.StringVar(value=str(proj.get("wordGoal", 15000)))

        for lbl, var in [
            ("PROJECT TITLE:", name_v),
            ("SECTOR / SUB-SECTOR:", sec_v),
            ("MANUSCRIPT WORD GOAL:", goal_v),
        ]:
            tk.Label(
                f,
                text=lbl,
                font=("Consolas", 9, "bold"),
                bg=self.colors["bg_panel"],
                fg=self.colors["accent_bright"],
            ).pack(anchor="w")
            tk.Entry(f, textvariable=var, font=("Consolas", 10)).pack(
                fill=tk.X, pady=(2, 8)
            )

        def _save():
            proj["name"] = name_v.get().strip() or proj["name"]
            proj["sector"] = sec_v.get().strip()
            try:
                proj["wordGoal"] = max(500, int(goal_v.get()))
            except Exception:
                pass
            self.refresh_all_views()
            self.save_state()
            dlg.destroy()

        tk.Button(
            f,
            text="SAVE PROJECT TELEMETRY",
            font=("Consolas", 10, "bold"),
            bg=self.colors["accent_main"],
            fg="#050807",
            command=_save,
            pady=6,
        ).pack(fill=tk.X, pady=8)

    def export_markdown_compilation(self):
        proj = self.get_active_project()
        default_name = f"{proj['name'].replace(' ', '_').replace(':', '')}_Bible.md"
        out_path = filedialog.asksaveasfilename(
            title="Export Markdown Worldbuilding Bible & Manuscript",
            defaultextension=".md",
            initialfile=default_name,
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
        )
        if not out_path:
            return

        md = [
            f"# {proj['name']}",
            f"**Sector:** {proj.get('sector', '')} | **Era:** {proj.get('era', '')}\n",
            f"{proj.get('description', '')}\n",
            "## PART I: CODEX DATABANKS\n",
        ]
        for e in proj["entries"]:
            schema = CATEGORY_SCHEMA.get(
                e.get("category", "factions"), CATEGORY_SCHEMA["factions"]
            )
            md.append(
                f"### [{schema['short']}] {e.get('title', '')} ({e.get('allegiance', '')})"
            )
            if e.get("subtitle"):
                md.append(f"*{e['subtitle']}*\n")
            if e.get("epigraph"):
                md.append(f"> {e['epigraph']}\n")
            for fkey, flabel in schema["fields"]:
                val = e.get("fields", {}).get(fkey)
                if val:
                    md.append(f"- **{flabel}:** {val}")
            md.append("")
            for ckey, ctitle in schema["compartments"]:
                val = e.get("compartments", {}).get(ckey)
                if val:
                    md.append(f"#### {ctitle}\n{val}\n")
            if e.get("body"):
                md.append(f"#### Extended Chronicle\n{e['body']}\n")

        md.append("## PART II: SCRIPTORIUM MANUSCRIPT\n")
        for s in proj["scenes"]:
            md.append(f"### {s.get('title', '')} ({s.get('imperialDate', '')})")
            if s.get("epigraph"):
                md.append(f"> {s['epigraph']}\n")
            md.append(f"{s.get('content', '')}\n")

        Path(out_path).write_text("\n".join(md), encoding="utf-8")
        messagebox.showinfo(
            "++ EXPORT COMPLETE ++",
            f"Exported complete Codex & Manuscript Markdown to:\n{out_path}",
        )

    def open_backup_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Noosphere Data-Slate JSON Archive & Restore")
        dlg.geometry("480x240")
        dlg.transient(self.root)
        dlg.grab_set()

        f = tk.Frame(dlg, padx=16, pady=16, bg=self.colors["bg_panel"])
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            f,
            text=f"Automatic Local Database:\n{self.save_file}",
            font=("Consolas", 9),
            bg=self.colors["bg_panel"],
            fg=self.colors["text_main"],
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 12))

        def _export_json():
            p = filedialog.asksaveasfilename(
                title="Save Portable .JSON Data-Slate Backup",
                defaultextension=".json",
                initialfile="dataslate_40k_backup.json",
                filetypes=[("JSON Archive", "*.json")],
            )
            if p:
                Path(p).write_text(
                    json.dumps(self.state, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                messagebox.showinfo("Saved", f"Saved JSON backup to:\n{p}")

        def _import_json():
            p = filedialog.askopenfilename(
                title="Restore .JSON Data-Slate Backup",
                filetypes=[("JSON Archive", "*.json")],
            )
            if p:
                try:
                    data = json.loads(Path(p).read_text(encoding="utf-8"))
                    if isinstance(data, dict) and data.get("projects"):
                        self.state = data
                        self.save_state()
                        self.refresh_all_views()
                        dlg.destroy()
                        messagebox.showinfo("Restored", "Data-Slate archive restored!")
                except Exception as ex:
                    messagebox.showerror("Error", f"Invalid JSON file:\n{ex}")

        tk.Button(
            f,
            text="⬇ EXPORT PORTABLE .JSON BACKUP",
            font=("Consolas", 9, "bold"),
            bg=self.colors["accent_main"],
            fg="#050807",
            command=_export_json,
            pady=6,
        ).pack(fill=tk.X, pady=4)

        tk.Button(
            f,
            text="⬆ LOAD / RESTORE .JSON BACKUP FILE",
            font=("Consolas", 9, "bold"),
            bg=self.colors["bg_card"],
            fg=self.colors["accent_bright"],
            command=_import_json,
            pady=6,
        ).pack(fill=tk.X, pady=4)


# =============================================================================
# 6. ENTRY POINT
# =============================================================================
def main():
    root = tk.Tk()
    app = LexicanumCogitatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()