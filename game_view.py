import arcade
import arcade.gui as gui

from board import Game
from board_sprites import BoardSprites
from constants import *
from menu_view import MenuView
from ui_theme import FONT, TEXT as TEXT_COLOR, TITLE_FONT
from widgets import BevelButton, Tooltip, audio_toggle, panel
import audio

ELIMINATED = (71, 85, 105)  # slate 600


class GameView(gui.UIView):
    def __init__(self, players):
        super().__init__()
        self.players = players
        self.game = Game(players, ROWS, COLS)
        self.hover = None
        self.resolving = False
        self.wave = 0
        self.board = BoardSprites(self.game.board, MARGIN, MARGIN)
        # Built up front: the winner can appear mid-chain, frames before the game-over panel.
        self.dim = arcade.SpriteList()
        self.dim.append(arcade.SpriteSolidColor(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                                (*BACKGROUND, 200)))
        self.build_hud()

    def build_hud(self):
        root = self.hud = self.add_widget(gui.UIAnchorLayout())
        info = gui.UIBoxLayout(space_between=8, align="left")
        self.turn_label = info.add(gui.UILabel("", font_name=FONT, font_size=20, bold=True))
        roster = info.add(gui.UIBoxLayout(vertical=False, space_between=12))
        self.roster = [roster.add(gui.UILabel(PLAYER_NAMES[p], font_name=FONT, font_size=12))
                       for p in range(self.players)]
        root.add(info, anchor_x="left", anchor_y="top", align_x=MARGIN, align_y=-MARGIN)

        actions = gui.UIBoxLayout(vertical=False, space_between=8)
        buttons = []
        for icon, tooltip, action in (("restart", "Restart  R", self.restart), ("pause", "Pause  Esc", self.pause)):
            button = actions.add(BevelButton(icon=icon, width=42, height=42, tooltip=tooltip))
            button.on_click = lambda event, action=action: action()
            buttons.append(button)
        root.add(actions, anchor_x="right", anchor_y="top", align_x=-MARGIN, align_y=-MARGIN + 4)
        # Floats under the buttons, over the roster, only while a button is hovered.
        self.tooltip = root.add(Tooltip(buttons), anchor_x="right", anchor_y="top", align_x=-MARGIN, align_y=-72)
        self.pause_menu = self.add_widget(self.build_pause_menu())
        self.pause_menu.visible = False
        self.update_hud()

    def build_pause_menu(self):
        card = gui.UIBoxLayout(space_between=10)
        card.add(gui.UILabel("PAUSED", font_name=TITLE_FONT, font_size=26, text_color=TEXT_COLOR))
        card.add(gui.UISpace(height=8))
        for text, icon, variant, action in (("Resume", "play", "accent", self.resume),
                                            ("Main menu", "menu", "raised", self.to_menu),
                                            ("Exit to desktop", "exit", "raised", arcade.exit)):
            button = card.add(BevelButton(text, icon=icon, width=230, height=50, variant=variant, radius=14))
            button.on_click = lambda event, action=action: action()
        toggles = card.add(gui.UIBoxLayout(vertical=False, space_between=10))
        for kind in ("sound", "music"):
            toggles.add(audio_toggle(kind, labelled=True, width=110, height=46, variant="raised"))
        overlay = gui.UIAnchorLayout()
        overlay.add(panel(card, padding=28))
        return overlay

    @property
    def paused(self):
        return self.pause_menu.visible

    def pause(self):
        if self.game.winner is None:
            self.hud.visible = False
            self.pause_menu.visible = True

    def resume(self):
        self.pause_menu.visible = False
        self.hud.visible = True

    def update_hud(self):
        game = self.game
        player = game.turn if game.winner is None else game.winner
        self.turn_label.text = f"{PLAYER_NAMES[player]}'s turn" if game.winner is None else f"{PLAYER_NAMES[player]} wins"
        self.turn_label.update_font(font_color=PLAYER_COLORS[player])
        self.turn_label.fit_content()
        for p, label in enumerate(self.roster):
            label.update_font(font_color=PLAYER_COLORS[p] if p in game.alive else ELIMINATED)

    def show_game_over(self):
        winner = self.game.winner
        self.hud.visible = False
        overlay = gui.UIAnchorLayout()
        card = gui.UIBoxLayout(space_between=14)
        card.add(gui.UILabel(f"{PLAYER_NAMES[winner].upper()} WINS", font_name=TITLE_FONT, font_size=26,
                             text_color=PLAYER_COLORS[winner]))
        card.add(gui.UILabel("Every other atom has been captured.", font_name=FONT, font_size=12,
                             text_color=MUTED_TEXT))
        card.add(gui.UISpace(height=6))
        buttons = card.add(gui.UIBoxLayout(vertical=False, space_between=10))
        again = buttons.add(BevelButton("Play again", icon="restart", width=150, height=50, variant="accent"))
        again.on_click = lambda event: self.restart()
        menu = buttons.add(BevelButton("Main menu", icon="menu", width=150, height=50, variant="raised"))
        menu.on_click = lambda event: self.to_menu()
        overlay.add(panel(card, padding=32))
        self.add_widget(overlay)

    def restart(self):
        self.window.show_view(GameView(self.players))

    def to_menu(self):
        self.window.show_view(MenuView(self.players))

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.ESCAPE, arcade.key.P):
            self.resume() if self.paused else self.pause()
        elif symbol == arcade.key.R and not self.paused:
            self.restart()

    @property
    def busy(self):
        return self.resolving or self.paused or self.game.winner is not None

    def update_highlight(self):
        legal = not self.busy and self.hover and self.game.board.can_place(*self.hover, self.game.turn)
        self.board.set_highlight(self.hover if legal else None, self.game.turn)

    def on_mouse_motion(self, x, y, dx, dy):
        self.hover = self.board.cell_at(x, y)
        self.update_highlight()

    def on_mouse_press(self, x, y, button, modifiers):
        cell = self.board.cell_at(x, y)
        if not cell or self.busy:
            return
        if self.game.play(*cell):
            audio.play("place")
            self.resolving = True
            self.wave = 0
            self.board.sync()
            self.update_highlight()
        else:
            audio.play("error")

    def on_update(self, delta_time):
        self.tooltip.refresh()
        if self.paused:
            return  # freeze explosions and spinning
        if self.board.update(delta_time):
            self.game.update_alive()
        if self.resolving and not self.board.animating:
            if self.game.winner is None and self.game.board.unstable():
                self.board.start_wave()
                self.wave += 1
                audio.play("explode", speed=min(1 + 0.07 * (self.wave - 1), 1.8))  # pitch climbs with the chain
            else:
                self.resolving = False
                self.game.end_turn()
                self.on_turn_end()
                self.update_highlight()

    def on_turn_end(self):
        self.update_hud()
        if self.game.winner is not None:
            audio.play("win")
            self.show_game_over()

    def on_draw_before_ui(self):
        self.board.draw()
        if self.paused or self.game.winner is not None:
            self.dim.draw()
