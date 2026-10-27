import arcade
import arcade.gui as gui
from arcade.gui.property import bind

import audio
from icons import icon_texture
from ui_theme import FONT, INK, VARIANTS, WHITE, lerp, rounded_patch

DEPTH = 4                         # resting height of the face above its lip, in px
STIFFNESS, DAMPING = 900.0, 26.0  # underdamped spring: the face overshoots a little on release
PRESS_KICK = -260.0               # px/s; makes even a very fast click visibly sink
CAP_HEIGHT = 0.69                 # Liberation Sans cap height, in em
ICON_GAP = 8


class BevelButton(gui.UIInteractiveWidget):
    """Rounded button with a bevelled lip. Lifts on hover, sinks when pressed and springs back."""

    def __init__(self, text="", icon=None, width=100, height=44, variant="secondary",
                 font_size=15, radius=12, tooltip="", **kwargs):
        super().__init__(width=width, height=height, **kwargs)
        self.icon = icon
        self.radius = radius
        self.tooltip = tooltip
        self._variant = variant
        self.lift = float(DEPTH)
        self.velocity = 0.0
        self.label = arcade.Text(text, 0, 0, font_name=FONT, font_size=font_size,
                                 bold=variant in ("primary", "accent"), anchor_x="center", anchor_y="baseline")
        bind(self, "pressed", self._on_pressed)
        bind(self, "hovered", self.trigger_render)

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self._variant = value
        self.label.bold = value in ("primary", "accent")
        self.trigger_render()

    def set_icon(self, icon):
        self.icon = icon
        self.trigger_render()

    def _on_pressed(self):
        if self.pressed:
            self.velocity = PRESS_KICK
            audio.play("click")
        self.trigger_render()

    def on_update(self, dt):
        dt = min(dt, 1 / 30)
        target = 0.0 if self.pressed else DEPTH + (1.0 if self.hovered else 0.0)
        if abs(target - self.lift) > 0.01 or abs(self.velocity) > 0.5:
            self.velocity += (STIFFNESS * (target - self.lift) - DAMPING * self.velocity) * dt
            self.lift += self.velocity * dt
            self.trigger_render()

    def do_render(self, surface):
        self.prepare_render(surface)
        face, hover, content = VARIANTS[self._variant]
        color = hover if self.hovered else face
        w, h = self.content_width, self.content_height
        body = h - DEPTH - 1
        lift = max(0.0, min(self.lift, DEPTH + 1.0))

        # NinePatchTexture.draw_rect directly: arcade 3.3.2's Surface.draw_texture drops x/y for nine-patches.
        rounded_patch(lerp(face, INK, 0.5), self.radius).draw_rect(rect=arcade.LBWH(0, 0, w, body))
        rounded_patch(color, self.radius, lerp(color, WHITE, 0.2)).draw_rect(rect=arcade.LBWH(0, lift, w, body))

        # Icon and label are centred together as one group.
        size = round(min(body * 0.55, 22)) if self.icon else 0
        text_width = self.label.content_width if self.label.text else 0
        x = (w - size - text_width - (ICON_GAP if size and text_width else 0)) / 2
        cy = lift + body / 2
        if self.icon:
            surface.draw_texture(x, cy - size / 2, size, size, icon_texture(self.icon, content, size))
            x += size + ICON_GAP
        if self.label.text:
            # Centre on cap height; anchor_y="center" centres the full ascender-descender box, which reads high.
            self.label.position = (x + text_width / 2, cy - CAP_HEIGHT * self.label.font_size * 96 / 72 / 2)
            self.label.color = content
            self.label.draw()


def panel(child, padding=28, radius=20, color=(30, 41, 59)):
    """Rounded card holding `child`."""
    return child.with_background(texture=rounded_patch(color, radius)).with_padding(all=padding)


def audio_toggle(kind, labelled=False, **kwargs):
    """Icon button that turns "sound" or "music" on and off; `labelled` adds the word next to the icon."""
    def tooltip():
        return f"{kind.capitalize()} {'on' if audio.settings[kind] else 'off'}"

    button = BevelButton(kind.capitalize() if labelled else "", icon=audio.icon(kind), tooltip=tooltip(), **kwargs)

    def click(event):
        audio.toggle(kind)
        button.set_icon(audio.icon(kind))
        button.tooltip = tooltip()
    button.on_click = click
    return button


class Tooltip(gui.UILabel):
    """Small pill that names whichever of `buttons` is hovered. Call refresh() every frame."""

    def __init__(self, buttons):
        super().__init__("", font_name=FONT, font_size=11, text_color=(226, 232, 240))
        self.buttons = buttons
        self.with_background(texture=rounded_patch((51, 65, 85), 8)).with_padding(left=8, right=8, top=4, bottom=4)
        self.visible = False

    def refresh(self):
        text = next((b.tooltip for b in self.buttons if b.hovered), "")
        if text != self.text:
            self.text = text
            self.fit_content()
            self.visible = bool(text)
