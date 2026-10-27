import arcade
import arcade.gui as gui

from constants import MUTED_TEXT, PLAYER_COLORS
from ui_theme import FONT, PRIMARY, SECONDARY, TITLE_FONT, TEXT


class MenuView(gui.UIView):
    def __init__(self, players=2):
        super().__init__()
        self.players = players

        column = gui.UIBoxLayout(space_between=14)
        column.add(gui.UILabel("CHAIN", font_name=TITLE_FONT, font_size=40, text_color=TEXT))
        column.add(gui.UILabel("REACTION", font_name=TITLE_FONT, font_size=40, text_color=PLAYER_COLORS[0]))
        column.add(gui.UISpace(height=28))
        column.add(gui.UILabel("Players", font_name=FONT, font_size=13, text_color=MUTED_TEXT))

        self.count_buttons = {}
        row = gui.UIBoxLayout(vertical=False, space_between=6)
        for n in range(2, len(PLAYER_COLORS) + 1):
            button = gui.UIFlatButton(text=str(n), width=44, height=44)
            button.on_click = lambda event, n=n: self.select(n)
            self.count_buttons[n] = row.add(button)
        column.add(row)

        column.add(gui.UISpace(height=20))
        play = column.add(gui.UIFlatButton(text="Play", width=200, height=48, style=PRIMARY))
        play.on_click = lambda event: self.start()
        column.add(gui.UISpace(height=28))
        column.add(gui.UILabel(
            "Add atoms to empty cells or your own.\n"
            "Full cells explode and capture their neighbours.\n"
            "Last player with atoms wins.",
            font_name=FONT, font_size=12, text_color=MUTED_TEXT, multiline=True, width=400, align="center"))

        self.add_widget(gui.UIAnchorLayout()).add(column)
        self.select(players)

    def select(self, n):
        self.players = n
        for count, button in self.count_buttons.items():
            button.style = PRIMARY if count == n else SECONDARY

    def start(self):
        from game_view import GameView  # avoid circular import: GameView links back here
        self.window.show_view(GameView(self.players))

    def on_key_press(self, symbol, modifiers):
        if symbol in (arcade.key.ENTER, arcade.key.SPACE):
            self.start()
        elif symbol in (arcade.key.LEFT, arcade.key.RIGHT):
            n = self.players + (1 if symbol == arcade.key.RIGHT else -1)
            self.select(min(max(n, 2), len(PLAYER_COLORS)))
        elif arcade.key.KEY_2 <= symbol <= arcade.key.KEY_8:
            self.select(symbol - arcade.key.KEY_0)
