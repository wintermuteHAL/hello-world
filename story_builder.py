#!/usr/bin/env python3
"""
Choose Your Adventure — Story Builder
--------------------------------------
Write mode : create and link scenes interactively
Play mode  : walk through your story to test it

Usage:
    python story_builder.py                        # new story
    python story_builder.py my_story.json          # load existing story
    python story_builder.py my_story.json --play   # jump straight to play mode
"""

import json
import os
import sys
import textwrap

# ─────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────

def new_story(title: str) -> dict:
    return {"title": title, "start": None, "scenes": {}}


def new_scene(title: str, text: str) -> dict:
    return {"title": title, "text": text, "choices": []}


def load_story(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_story(path: str, story: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {path}")


# ─────────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────────

DIVIDER = "─" * 60

def clear():
    os.system("cls" if sys.platform == "win32" else "clear")


def wrap(text: str, width: int = 70) -> str:
    return "\n".join(textwrap.fill(line, width) for line in text.splitlines())


def pause():
    input("\n  [Press Enter to continue]")


def header(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ─────────────────────────────────────────────
#  SCENE ID HELPERS
# ─────────────────────────────────────────────

def slugify(text: str) -> str:
    """Turn a title into a safe scene ID, e.g. 'The Dark Cave' → 'the_dark_cave'."""
    return "_".join(text.lower().split())[:40]


def pick_scene(story: dict, prompt: str = "Scene ID") -> str | None:
    """Ask the user to type or pick a scene ID from a numbered list."""
    scenes = list(story["scenes"].keys())
    if not scenes:
        print("  No scenes yet.")
        return None
    for i, sid in enumerate(scenes, 1):
        title = story["scenes"][sid]["title"]
        marker = " [START]" if sid == story["start"] else ""
        print(f"  [{i}] {sid}  —  {title}{marker}")
    raw = input(f"\n  {prompt} (number or ID): ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(scenes):
            return scenes[idx]
    if raw in story["scenes"]:
        return raw
    print("  Not found.")
    return None


# ─────────────────────────────────────────────
#  WRITE MODE — individual actions
# ─────────────────────────────────────────────

def action_new_scene(story: dict) -> None:
    header("NEW SCENE")
    title = input("  Scene title: ").strip()
    if not title:
        print("  Cancelled.")
        return

    sid = slugify(title)
    # Avoid collisions
    base, n = sid, 1
    while sid in story["scenes"]:
        sid = f"{base}_{n}"
        n += 1

    print(f"\n  Write the scene text. Enter a blank line when done.")
    lines = []
    while True:
        line = input()
        if line == "" and lines:
            break
        lines.append(line)
    text = "\n".join(lines)

    story["scenes"][sid] = new_scene(title, text)
    print(f'\n  Scene "{sid}" created.')

    # Offer to set as start if none exists
    if story["start"] is None:
        if input("  Set as story start? [y/n] ").strip().lower() == "y":
            story["start"] = sid
            print(f"  Start scene set to \"{sid}\".")


def action_edit_scene(story: dict) -> None:
    header("EDIT SCENE")
    if not story["scenes"]:
        print("  No scenes yet.")
        return

    sid = pick_scene(story, "Scene to edit")
    if not sid:
        return

    scene = story["scenes"][sid]
    print(f'\n  Editing: {scene["title"]}\n')
    print("  What would you like to change?")
    print("  [1] Title")
    print("  [2] Body text")
    print("  [3] Back")

    choice = input("\n  >>> ").strip()
    if choice == "1":
        new_title = input("  New title: ").strip()
        if new_title:
            scene["title"] = new_title
            print("  Title updated.")
    elif choice == "2":
        print(f'\n  Current text:\n\n{wrap(scene["text"])}\n')
        print("  Write new text. Enter a blank line when done.")
        lines = []
        while True:
            line = input()
            if line == "" and lines:
                break
            lines.append(line)
        scene["text"] = "\n".join(lines)
        print("  Text updated.")


def action_manage_choices(story: dict) -> None:
    header("MANAGE CHOICES")
    if not story["scenes"]:
        print("  No scenes yet.")
        return

    sid = pick_scene(story, "Scene to edit choices for")
    if not sid:
        return

    scene = story["scenes"][sid]

    while True:
        print(f'\n  Choices for "{scene["title"]}":')
        if scene["choices"]:
            for i, c in enumerate(scene["choices"], 1):
                target_title = story["scenes"].get(c["target"], {}).get("title", "???")
                print(f'  [{i}] "{c["text"]}"  →  {c["target"]} ({target_title})')
        else:
            print("  (no choices — this is an ending)")

        print("\n  [a] Add choice  [r] Remove choice  [b] Back")
        cmd = input("  >>> ").strip().lower()

        if cmd == "b":
            break

        elif cmd == "a":
            text = input("  Choice text (what the reader sees): ").strip()
            if not text:
                continue
            print("\n  Which scene does this lead to?")
            target = pick_scene(story, "Target scene")
            if not target:
                continue
            scene["choices"].append({"text": text, "target": target})
            print("  Choice added.")

        elif cmd == "r":
            if not scene["choices"]:
                print("  No choices to remove.")
                continue
            raw = input("  Remove choice number: ").strip()
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(scene["choices"]):
                    removed = scene["choices"].pop(idx)
                    print(f'  Removed: "{removed["text"]}"')
                else:
                    print("  Out of range.")


def action_set_start(story: dict) -> None:
    header("SET START SCENE")
    sid = pick_scene(story, "Scene to use as story start")
    if sid:
        story["start"] = sid
        print(f'  Start scene set to "{sid}".')


def action_list_scenes(story: dict) -> None:
    header("ALL SCENES")
    if not story["scenes"]:
        print("  No scenes yet.")
        return

    for sid, scene in story["scenes"].items():
        marker = " [START]" if sid == story["start"] else ""
        ending = " [ENDING]" if not scene["choices"] else ""
        print(f'\n  {sid}{marker}{ending}')
        print(f'    Title   : {scene["title"]}')
        print(f'    Preview : {scene["text"][:60].replace(chr(10), " ")}…')
        if scene["choices"]:
            for c in scene["choices"]:
                print(f'    → "{c["text"]}"  →  {c["target"]}')


def action_check_story(story: dict) -> None:
    """Report broken links, orphaned scenes, and missing start."""
    header("STORY CHECK")
    issues = []

    if not story["start"]:
        issues.append("No start scene set.")
    elif story["start"] not in story["scenes"]:
        issues.append(f'Start scene "{story["start"]}" does not exist.')

    # Find all scenes that are referenced by choices
    referenced = set()
    if story["start"]:
        referenced.add(story["start"])

    for sid, scene in story["scenes"].items():
        for c in scene["choices"]:
            t = c["target"]
            if t not in story["scenes"]:
                issues.append(f'Scene "{sid}": choice "{c["text"]}" links to missing scene "{t}".')
            referenced.add(t)

    orphans = [sid for sid in story["scenes"] if sid not in referenced]
    for o in orphans:
        issues.append(f'Scene "{o}" is unreachable (not linked from any choice).')

    endings = [sid for sid, s in story["scenes"].items() if not s["choices"]]

    if issues:
        print(f"\n  Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"  ⚠  {issue}")
    else:
        print("\n  No issues found.")

    print(f"\n  Scenes   : {len(story['scenes'])}")
    print(f"  Endings  : {len(endings)} ({', '.join(endings) or 'none'})")


# ─────────────────────────────────────────────
#  WRITE MODE — main loop
# ─────────────────────────────────────────────

def write_mode(story: dict, path: str) -> None:
    while True:
        header(f"STORY BUILDER  —  {story['title']}")
        print("  [n] New scene")
        print("  [e] Edit scene text / title")
        print("  [c] Manage choices")
        print("  [s] Set start scene")
        print("  [l] List all scenes")
        print("  [k] Check story for issues")
        print("  [p] Play story")
        print("  [w] Save")
        print("  [q] Quit")
        print()

        cmd = input("  >>> ").strip().lower()

        if cmd == "n":
            action_new_scene(story)
            save_story(path, story)
        elif cmd == "e":
            action_edit_scene(story)
            save_story(path, story)
        elif cmd == "c":
            action_manage_choices(story)
            save_story(path, story)
        elif cmd == "s":
            action_set_start(story)
            save_story(path, story)
        elif cmd == "l":
            action_list_scenes(story)
            pause()
        elif cmd == "k":
            action_check_story(story)
            pause()
        elif cmd == "p":
            play_mode(story)
        elif cmd == "w":
            save_story(path, story)
            pause()
        elif cmd == "q":
            save_story(path, story)
            print("  Goodbye!\n")
            break


# ─────────────────────────────────────────────
#  PLAY MODE
# ─────────────────────────────────────────────

def play_mode(story: dict) -> None:
    clear()
    header(f"PLAYING: {story['title']}")

    if not story["start"]:
        print("  No start scene set. Go to the editor and set one.")
        pause()
        return
    if story["start"] not in story["scenes"]:
        print(f'  Start scene "{story["start"]}" is missing.')
        pause()
        return

    history = []
    current = story["start"]

    while True:
        scene = story["scenes"].get(current)
        if not scene:
            print(f'\n  Error: scene "{current}" not found.')
            pause()
            break

        print(f'\n  ── {scene["title"]} ──\n')
        print(wrap(scene["text"]))
        print()

        choices = scene["choices"]
        if not choices:
            print("  [THE END]\n")
            if history:
                if input("  Play again from the start? [y/n] ").strip().lower() == "y":
                    history = []
                    current = story["start"]
                    clear()
                    header(f"PLAYING: {story['title']}")
                    continue
            break

        for i, c in enumerate(choices, 1):
            print(f"  [{i}] {c['text']}")
        if history:
            print("  [b] Go back")
        print("  [q] Quit to editor")
        print()

        raw = input("  >>> ").strip().lower()

        if raw == "q":
            break
        if raw == "b" and history:
            current = history.pop()
            clear()
            header(f"PLAYING: {story['title']}")
            continue
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                history.append(current)
                current = choices[idx]["target"]
                clear()
                header(f"PLAYING: {story['title']}")
                continue
        print("  Invalid choice.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    play_only = "--play" in args
    args = [a for a in args if a != "--play"]

    path = args[0] if args else None

    if path and os.path.exists(path):
        story = load_story(path)
        print(f'  Loaded "{story["title"]}" ({len(story["scenes"])} scenes)')
    else:
        if path is None:
            path = input("  Story filename (e.g. my_story.json): ").strip()
            if not path.endswith(".json"):
                path += ".json"

        if os.path.exists(path):
            story = load_story(path)
            print(f'  Loaded "{story["title"]}" ({len(story["scenes"])} scenes)')
        else:
            title = input("  Story title: ").strip() or "My Adventure"
            story = new_story(title)
            save_story(path, story)
            print(f'  Created new story: "{title}"')

    if play_only:
        play_mode(story)
    else:
        write_mode(story, path)


if __name__ == "__main__":
    main()
