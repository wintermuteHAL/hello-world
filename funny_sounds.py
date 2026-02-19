#!/usr/bin/env python3
"""
Funny Sounds Player
-------------------
Featuring Arnold Schwarzenegger, The Crypt Keeper, and Randy 'Macho Man' Savage.

Windows : uses pyttsx3 (Windows built-in SAPI engine) — pip install pyttsx3
Linux   : uses espeak — apt-get install espeak
Mac     : uses espeak — brew install espeak

Run normally for live playback, or pass --save to export WAV files.
"""

import subprocess
import sys
import os
import random
import tempfile
import shutil

IS_WINDOWS = sys.platform == "win32"

# ─────────────────────────────────────────────
#  CHARACTER DEFINITIONS
# ─────────────────────────────────────────────

CHARACTERS = {
    "1": {
        "name": "Arnold Schwarzenegger",
        "ascii_art": r"""
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   ░  ┌──────────────────────────┐    ░
   ░  │   ██████████████████    │    ░
   ░  │  ██ ▓▓ ARNOLD ▓▓ ██    │    ░
   ░  │  ██                ██   │    ░
   ░  │  ██  ◉          ◉  ██   │    ░
   ░  │  ██                ██   │    ░
   ░  │  ██    ━━━━━━━━    ██   │    ░
   ░  │  ██████████████████     │    ░
   ░  └──────────────────────────┘    ░
   ░     "I'LL  BE  BACK"             ░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
""",
        "intro": "I am Arnold Schwarzenegger. Hasta la vista, baby.",
        "phrases": [
            "I'll be back.",
            "Hasta la vista, baby.",
            "GET TO DA CHOPPA!",
            "It's not a tumor!",
            "You are terminated.",
            "Come with me if you want to live.",
            "I need your clothes, your boots, and your motorcycle.",
            "Talk to da hand!",
            "Put that cookie down! Now!",
            "You have been erased.",
            "Consider that a divorce.",
            "Do it! Do it now!",
            "You are one ugly mother.",
            "I lied.",
        ],
        # Slower rate, very low pitch → gravelly Austrian-ish robot voice
        "espeak_args": ["-v", "en-us", "-s", "105", "-p", "10", "-a", "200"],
        # pyttsx3 (Windows): slow and deliberate
        "pyttsx3_settings": {"rate": 120, "volume": 1.0},
    },

    "2": {
        "name": "The Crypt Keeper",
        "ascii_art": r"""
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   ░   ░░░░░░░░░░░░░░░░░░░░░░░░░        ░
   ░  ░  ┌────────────────────┐  ░      ░
   ░ ░   │  ░░░░░░░░░░░░░░░░  │   ░     ░
   ░ ░   │ ░  ◉          ◉  ░ │   ░     ░
   ░ ░   │  ░░ ▲        ▲ ░░  │   ░     ░
   ░ ░   │    ░░░░░░░░░░░░    │   ░     ░
   ░ ░   │       ▓▓▓▓▓▓       │   ░     ░
   ░  ░  └────────────────────┘  ░      ░
   ░   ░░░░░░░░░░░░░░░░░░░░░░░░░        ░
   ░        HEHEHEHEHEHEHE!              ░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
""",
        "intro": "Hello boils and ghouls! Hehehehehe! Welcome to my little program of terror!",
        "phrases": [
            "Hello boils and ghouls! Hehehehehe!",
            "It's DYING time! Hehehehehe!",
            "You could say he had a GRAVE situation! Heh heh heh!",
            "That was a real SCREAM! Hehehehehe!",
            "Time to face the MUMMY music! Heh heh heh!",
            "That tale gave me the CREEPS! Hehehehehe!",
            "You might say he had a DYING wish! Heh heh!",
            "Don't lose your HEAD over it! Hehehe!",
            "I'm DYING to tell you this one! Hehehehehe!",
            "Things are getting a little HAIRY! Heh heh!",
            "That's to DIE for! Hehehehehe!",
            "Welcome to my FRIGHT club! Hehehe!",
            "I've been DYING to meet you! Hehehehehe!",
            "Looks like this is a dead end! Heh heh heh!",
        ],
        # Higher pitch, faster rate → wheezy creepy cackle
        "espeak_args": ["-v", "en-us", "-s", "155", "-p", "75", "-a", "180"],
        # pyttsx3 (Windows): fast and high energy
        "pyttsx3_settings": {"rate": 200, "volume": 0.9},
    },

    "3": {
        "name": "Randy 'Macho Man' Savage",
        "ascii_art": r"""
   ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
   ★                                  ★
   ★   ╔══════════════════════════╗   ★
   ★   ║  O H H H H   Y E A H H  ║   ★
   ★   ╠══════════════════════════╣   ★
   ★   ║  ██  MACHO MAN  ██  ██  ║   ★
   ★   ║  ██  R A N D Y  ████    ║   ★
   ★   ║  ██  S A V A G E  ██    ║   ★
   ★   ╚══════════════════════════╝   ★
   ★     SNAP INTO A SLIM JIM!        ★
   ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
""",
        "intro": "OHHHH YEAHHH! The Macho Man Randy Savage is HERE! Dig it!",
        "phrases": [
            "OHHHH YEAHHH!",
            "Snap into a Slim Jim! OHHHH YEAHHH!",
            "The Macho Man Randy Savage is the cream of the crop!",
            "OHHHH YEAHHH! Dig it!",
            "I am the tower of power, too sweet to be sour!",
            "The Madness is running WILD! OHHHH YEAHHH!",
            "Oooh yeah, the Macho Madness! Dig it!",
            "Be a man! Come on! Dig it!",
            "Oh yeah, the cream rises to the top! YEAHHH!",
            "Pomp and Circumstance! OHHHH YEAHHH!",
            "I'm the best there is, the best there was! Dig it!",
            "SNAP INTO IT! OHHHH YEAHHH!",
            "The Macho Madness is on a whole nother level, yeah!",
            "Nothing means nothing! OHHHH YEAHHH!",
        ],
        # Fast rate, mid-low pitch, high amplitude → loud intense delivery
        "espeak_args": ["-v", "en-us", "-s", "148", "-p", "35", "-a", "250"],
        # pyttsx3 (Windows): fast and loud
        "pyttsx3_settings": {"rate": 185, "volume": 1.0},
    },
}

# ─────────────────────────────────────────────
#  AUDIO
# ─────────────────────────────────────────────

def _find_player():
    """Return the first available audio player command on Linux/Mac, or None."""
    for player in ("aplay", "paplay", "ffplay", "sox"):
        if shutil.which(player):
            return player
    return None


def _speak_windows(text, pyttsx3_settings, output_dir=None):
    """Speak using the Windows built-in SAPI engine via pyttsx3."""
    try:
        import pyttsx3
    except ImportError:
        print("  [pyttsx3 not found — run: pip install pyttsx3]")
        return None

    engine = pyttsx3.init()
    engine.setProperty("rate", pyttsx3_settings["rate"])
    engine.setProperty("volume", pyttsx3_settings["volume"])

    if output_dir:
        safe = "".join(c if c.isalnum() or c in " _-" else "" for c in text[:40])
        wav_path = os.path.join(output_dir, f"{safe.strip()}.wav")
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        return wav_path

    engine.say(text)
    engine.runAndWait()
    return None


def _speak_espeak(text, espeak_args, output_dir=None):
    """Speak using espeak (Linux / Mac)."""
    if output_dir:
        safe = "".join(c if c.isalnum() or c in " _-" else "" for c in text[:40])
        wav_path = os.path.join(output_dir, f"{safe.strip()}.wav")
        cmd = ["espeak"] + espeak_args + [text, "-w", wav_path]
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        return wav_path

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    try:
        subprocess.run(
            ["espeak"] + espeak_args + [text, "-w", tmp],
            check=True, stderr=subprocess.DEVNULL,
        )
        player = _find_player()
        if player == "ffplay":
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", tmp],
                check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            )
        elif player:
            subprocess.run([player, tmp], check=False, stderr=subprocess.DEVNULL)
        else:
            print("  [no audio player found — use --save to export WAV files]")
    except FileNotFoundError:
        print("  [espeak not found — install with: apt-get install espeak]")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return None


def speak(text, char, output_dir=None):
    """Speak text using the appropriate engine for the current platform."""
    if IS_WINDOWS:
        return _speak_windows(text, char["pyttsx3_settings"], output_dir)
    return _speak_espeak(text, char["espeak_args"], output_dir)


# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║           F U N N Y   S O U N D S   P L A Y E R             ║
║    Arnold Schwarzenegger  •  Crypt Keeper  •  Macho Man      ║
╚══════════════════════════════════════════════════════════════╝
"""

def print_banner():
    print(BANNER)


def show_main_menu():
    print("Choose your character:\n")
    for key, char in CHARACTERS.items():
        print(f"  [{key}] {char['name']}")
    print("  [4] Random character & random phrase")
    print("  [q] Quit\n")


def show_character_menu(char):
    print(char["ascii_art"])
    print(f"=== {char['name'].upper()} ===\n")
    print("Choose a phrase  (Enter = random, b = back):\n")
    for i, phrase in enumerate(char["phrases"], 1):
        print(f"  [{i:2}] {phrase}")
    print()


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

def character_loop(key, output_dir):
    char = CHARACTERS[key]
    while True:
        show_character_menu(char)
        choice = input(">>> ").strip().lower()

        if choice == "b":
            break

        if choice == "":
            phrase = random.choice(char["phrases"])
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(char["phrases"]):
                    phrase = char["phrases"][idx]
                else:
                    print("  Invalid choice.\n")
                    continue
            except ValueError:
                print("  Invalid choice.\n")
                continue

        print(f'\n  >> "{phrase}"\n')
        wav = speak(phrase, char, output_dir)
        if wav:
            print(f"  Saved: {wav}\n")

        again = input("  Play another phrase? [y/n] ").strip().lower()
        if again != "y":
            break


def play_random(output_dir):
    key = random.choice(list(CHARACTERS.keys()))
    char = CHARACTERS[key]
    phrase = random.choice(char["phrases"])
    print(f"\n  [{char['name']}]\n  >> \"{phrase}\"\n")
    wav = speak(phrase, char, output_dir)
    if wav:
        print(f"  Saved: {wav}\n")


def main():
    # --save flag: export WAV files to a directory instead of live playback
    output_dir = None
    if "--save" in sys.argv:
        output_dir = os.path.join(os.getcwd(), "funny_sounds_output")
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n  [Save mode] WAV files will be written to: {output_dir}")

    print_banner()

    while True:
        show_main_menu()
        choice = input(">>> ").strip().lower()

        if choice == "q":
            print('\n  "Hasta la vista, baby."\n')
            speak("Hasta la vista, baby.", CHARACTERS["1"], output_dir)
            print("  Goodbye!\n")
            break

        if choice in CHARACTERS:
            char = CHARACTERS[choice]
            print(f'\n  >> Introducing... {char["name"]}!\n')
            speak(char["intro"], char, output_dir)
            character_loop(choice, output_dir)

        elif choice == "4":
            play_random(output_dir)

        else:
            print("  Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()
