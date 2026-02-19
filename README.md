# hello-world

This is my first step.

## Funny Sounds Player

An interactive CLI program that speaks famous catchphrases from three iconic characters using text-to-speech.

### Characters

| # | Character | Sample phrase |
|---|-----------|---------------|
| 1 | Arnold Schwarzenegger | "I'll be back." |
| 2 | The Crypt Keeper | "Hello boils and ghouls! Hehehehehe!" |
| 3 | Randy 'Macho Man' Savage | "OHHHH YEAHHH!" |

### Requirements

```bash
apt-get install espeak   # TTS engine
```

### Usage

**Interactive mode** (requires audio hardware):

```bash
python3 funny_sounds.py
```

**Save mode** — exports WAV files to `./funny_sounds_output/`:

```bash
python3 funny_sounds.py --save
```

### Controls

```
[1]  Arnold Schwarzenegger
[2]  The Crypt Keeper
[3]  Randy 'Macho Man' Savage
[4]  Random character & random phrase
[q]  Quit
```

After choosing a character, select a numbered phrase or press **Enter** for a random one. Press **b** to go back to the main menu.
