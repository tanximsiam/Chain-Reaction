"""Sound effects and music (Kenney CC0 sounds bundled with Arcade). Silent if no audio device works."""
import arcade

EFFECTS = {  # name: (resource, volume)
    "click": (":resources:sounds/hit5.wav", 0.25),
    "place": (":resources:sounds/coin5.wav", 0.3),
    "error": (":resources:sounds/error3.wav", 0.35),
    "explode": (":resources:sounds/rockHit2.wav", 0.4),
    "win": (":resources:sounds/upgrade4.wav", 0.45),
}
MUSIC = (":resources:music/funkyrobot.mp3", 0.18)

settings = {"sound": True, "music": False}
_sounds = {}
_music_player = None


def _load(resource):
    if resource not in _sounds:
        try:
            _sounds[resource] = arcade.load_sound(resource)
        except Exception:  # no audio backend or codec: play nothing rather than crash
            _sounds[resource] = None
    return _sounds[resource]


def play(name, speed=1.0):
    if settings["sound"]:
        resource, volume = EFFECTS[name]
        sound = _load(resource)
        if sound:
            try:
                arcade.play_sound(sound, volume=volume, speed=speed)
            except Exception:
                pass


def toggle(kind):
    """Flip "sound" or "music" on/off and return the new state."""
    global _music_player
    settings[kind] = not settings[kind]
    if kind == "music":
        if settings["music"]:
            sound = _load(MUSIC[0])
            _music_player = sound and arcade.play_sound(sound, volume=MUSIC[1], loop=True)
        elif _music_player:
            arcade.stop_sound(_music_player)
            _music_player = None
    return settings[kind]


def icon(kind):
    return f"{kind}_{'on' if settings[kind] else 'off'}"
