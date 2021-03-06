"""Find URLs in code and make them clickable."""

from functools import partial
import tkinter
from typing import Iterable, Tuple
import webbrowser

from porcupine import get_tab_manager, tabs, utils
from porcupine.plugins import underlines


def find_urls(text: tkinter.Text) -> Iterable[Tuple[str, str]]:
    searching_begins_here = '1.0'
    while True:
        match_start = text.search(
            r'\mhttps?://[a-z]', searching_begins_here, 'end',
            nocase=True, regexp=True)
        if not match_start:     # empty string means not found
            break

        # urls end on space, quote or end of line
        end_of_line = f'{match_start} lineend'
        match_end = text.search(r'''["' ]''', match_start, end_of_line, regexp=True) or end_of_line

        # support parenthesized urls and commas/dots after urls
        if text.get(f'{match_end} - 1 char') in {',', '.'}:
            match_end += ' - 1 char'

        url = text.get(match_start, match_end)
        closing2opening = {')': '(', '}': '{', '>': '<'}    # {url} is useful for tcl code
        if url[-1] in closing2opening and closing2opening[url[-1]] not in url:
            # url isn't like "Bla(bla)" but ends with ")" or similar, assume that's not part of url
            match_end = f'{match_end} - 1 char'

        yield (match_start, match_end)
        searching_begins_here = match_end


def update_url_underlines(tab: tabs.FileTab, junk: object = None) -> None:
    tab.event_generate('<<SetUnderlines>>', data=underlines.Underlines(
        id='urls',
        underline_list=[
            underlines.Underline(start, end, "ctrl+click or ctrl+enter to open")
            for start, end in find_urls(tab.textwidget)
        ],
    ))


def open_the_url(tab: tabs.FileTab, index: str, junk: object) -> utils.BreakOrNone:
    # tag_ranges is a painful method to use
    ranges = tab.textwidget.tag_ranges('underline:urls')
    for start, end in zip(ranges[0::2], ranges[1::2]):
        if tab.textwidget.compare(start, '<=', index) and tab.textwidget.compare(index, '<=', end):
            webbrowser.open(tab.textwidget.get(start, end))
            return 'break'
    return None


def on_new_tab(event: utils.EventWithData) -> None:
    tab = event.data_widget()
    if isinstance(tab, tabs.FileTab):
        tab.textwidget.bind('<<ContentChanged>>', partial(update_url_underlines, tab), add=True)
        update_url_underlines(tab)

        tab.textwidget.tag_bind('underline:urls', '<Control-Button-1>', partial(open_the_url, tab, 'current'), add=True)
        tab.textwidget.bind('<Control-Return>', partial(open_the_url, tab, 'insert'), add=True)


def setup() -> None:
    utils.bind_with_data(get_tab_manager(), '<<NewTab>>', on_new_tab, add=True)
