from components.carousel import Carousel, ScrollDirection, VerticalScroller
from components.playerbox import PlayerBox
from components.sidebar import Sidebar
from ttml import Lyrics


from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, ListItem, Static


class SyncScreen(Screen):
    lyrics_saved_state: Lyrics = None
    active_line_index: int = 0

    def compose(self) -> ComposeResult:
        yield Static("No Lyrics Loaded", id="lyrics_label")
        yield Sidebar(id="sidebar")
        yield Carousel(id="word-carousel")
        yield (Horizontal(
            Button("←", id="prev_word_button"),
            Button("→", id="next_word_button"),
            Button("F", id="set_start_time",
                   tooltip="Set timestamp as the startime of the word"),
            Button("G", id="set_end_move",
                   tooltip="Set timestamp as the end of current word and start time of the next word"),
            Button("H", id="set_end_time",
                   tooltip="Set Timestamp as the endtime of the current word and stay there"),
            id="carousel_control"
        ))
        yield PlayerBox(id="player_box", player=self.app.PLAYER)

    def update_scroller(self) -> None:
        carousel: Carousel = self.query_one(Carousel)
        vertical_scroller: VerticalScroller = self.query_one(VerticalScroller)
        active_word_index = self.app.CURR_LYRICS.element_map[self.app.CURR_LYRICS.get_element_map_index(
            carousel.active_item.element)][1]

        if vertical_scroller.active_line_index > active_word_index:
            vertical_scroller.scroll(ScrollDirection.backward)
        elif vertical_scroller.active_line_index < active_word_index:
            vertical_scroller.scroll(ScrollDirection.forward)

    def on_button_pressed(self, event: Button.Pressed):
        carousel: Carousel = self.query_one(Carousel)

        if event.button.id == "next_word_button":
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
        if event.button.id == "prev_word_button":
            carousel.move(ScrollDirection.backward)
            self.update_scroller()
        elif event.button.id == "set_start_time":
            active_word_index: int = self.app.CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            self.app.CURR_LYRICS.element_map[active_word_index][0].start_time = round(
                self.app.PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_time":
            active_word_index: int = self.app.CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            self.app.CURR_LYRICS.element_map[active_word_index][0].end_time = round(
                self.app.PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
        elif event.button.id == "set_end_move":
            active_word_index: int = self.app.CURR_LYRICS.get_element_map_index(
                carousel.active_item.element)
            self.app.CURR_LYRICS.element_map[active_word_index][0].end_time = round(
                self.app.PLAYER.get_timestamp(), 3)
            active_item_index = carousel.query_one(
                "#root")._nodes.index(carousel.active_item)
            carousel.query_one("#root")._nodes[active_item_index].update()
            carousel.move(ScrollDirection.forward)
            self.update_scroller()
            self.app.CURR_LYRICS.element_map[active_word_index +
                                    1][0].start_time = round(self.app.PLAYER.get_timestamp(), 3)+0.02
            carousel.query_one("#root")._nodes[active_item_index+1].update()

    def on_screen_resume(self, event: events.ScreenResume):
        label: Static = self.query_one("#lyrics_label", Static)

        if self.app.CURR_LYRICS == self.lyrics_saved_state:
            return

        if self.app.CURR_LYRICS.element_map == []:
            self.lyrics_saved_state = self.app.CURR_LYRICS
            self.query_one("#word-carousel").visible = False
            label.display = True
            return

        self.lyrics_saved_state = self.app.CURR_LYRICS
        self.query_one("#word-carousel").visible = True
        self.remove_children(ListItem)
        label.display = False

        self.mount(VerticalScroller(lyrics=self.app.CURR_LYRICS))