import pyglet
from karaoke_game import KaraokeGame
from voice_translator import VoiceTranslator

SCROLL_SPEED = 100


class KaraokeWindow(pyglet.window.Window):
    def __init__(self, game: KaraokeGame, translator: VoiceTranslator):
        super().__init__(width=800, height=600, caption="Karaoke Game")
        self.game = game
        self.translator = translator

        self.countdown = 3.0

        # 60 frames per second
        pyglet.clock.schedule_interval(self.update, 1/60)
        self.translator.start()

    def update(self, dt):
        # countdown
        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                # game has to start
                self.game_started = True
                self.game.start()
        # game started
        elif self.game_started:
            self.game.update(dt, self.translator.to_midi())

    def on_draw(self):
        self.clear()

        # countdown before game starts
        if self.countdown > 0:
            pyglet.text.Label(
                f"Starting in: {int(self.countdown) + 1}",
                x=self.width // 2, y=self.height // 2,
                font_size=48,
                anchor_x='center', anchor_y='center'
            ).draw()
            return

        # vertical line showing where notes should be hit (current time)
        line_x = self.width // 2
        pyglet.shapes.Line(line_x, 0, line_x, self.height -
                           10, color=(255, 255, 255)).draw()

        # notes to hit
        for start, note, duration in self.game.song.notes:
            time_until = start - self.game.time
            x = self.width // 2 + time_until * SCROLL_SPEED
            if -100 < x < self.width + 100:
                y = self.note_to_y(note)
                pyglet.shapes.Rectangle(
                    x, y, duration * SCROLL_SPEED, 10, color=(255, 0, 0)).draw()

        # player current note
        p_note = self.translator.to_midi()
        if p_note:
            y = self.note_to_y(p_note)
            pyglet.shapes.Rectangle(
                self.width // 2 - 5, y, 10, 10, color=(0, 255, 0)).draw()

        # score and percentage
        pyglet.text.Label(
            f"Score: {self.game.score} ({self.game.percentage}%)", x=10, y=self.height - 20).draw()

        # end screen
        if not self.game.running:
            pyglet.text.Label(
                f"Final Score: {self.game.percentage}%",
                x=self.width // 2, y=self.height // 2,
                font_size=20,
                anchor_x='center', anchor_y='center'
            ).draw()

    def on_close(self):
        self.translator.stop()
        super().on_close()

    def note_to_y(self, note):
        # Range of midi notes that can be displayed
        note_min, note_max = 40, 90
        return (note - note_min) / (note_max - note_min) * self.height
