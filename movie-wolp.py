#!/usr/bin/env python3

"""
------------------------------------------------
                   Movie Wolp
    A terminal-based media library explorer.
         Copyright (c) 2025 WolfPup1232
                 Icons by Icons8
------------------------------------------------
"""

# Import Python Standard Library Modules
import os, json, subprocess

# Import Python Standard Library Classes
from pathlib import Path

# Import Textual Library Classes
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Input
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.reactive import reactive

# Import Rich Pixels Library Classes
from rich_pixels import Pixels
from rich.console import Console

# Application title
APP_TITLE = "Movie Wolp"

# Config and cache file names
CONFIG_FILE = "config.json"
MOVIE_CACHE = "movies.json"
TV_CACHE = "tv-shows.json"

"""
Movie Wolp application's main class.
"""
class MovieWolp(App):

    # Path to the CSS stylesheet for styling Textual elements
    CSS_PATH = "movie-wolp.tcss"

    """
    Class constructor.
    """
    def __init__(self):
        super().__init__()

        # Get Movie Wolp's base file path
        self.base_path = Path(__file__).parent

        # Get Movie Wolp's config and cache paths
        self.config_path = self.base_path / CONFIG_FILE
        self.movie_cache_path = self.base_path / MOVIE_CACHE
        self.tv_cache_path = self.base_path / TV_CACHE

        # Initialize Movie Wolp's config object
        self.config = {"movie_dirs": [], "tv_dirs": []}

        # Initialize Movie Wolp's media library objects
        self.movies = {}
        self.tv_shows = {}

    """
    Textual DOM mounted event handler.
    Handles the events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self) -> None:

        # If the config file, movie cache file, and TV cache file all exist...
        if (self.config_path.exists() and self.movie_cache_path.exists() and self.tv_cache_path.exists()):

            # Load config file...
            with open(self.config_path) as f:
                self.config = json.load(f)

            # Load movie cache file...
            with open(self.movie_cache_path) as f:
                self.movies = json.load(f)

            # Load TV cache file...
            with open(self.tv_cache_path) as f:
                self.tv_shows = json.load(f)

            # Show main menu
            self.push_screen(MainMenuScreen())

        # Otherwise, if the config file, or either of the cache files, do not exist...
        else:

            # Show configuration screen
            self.push_screen(ConfigurationScreen())

    """
    Save the current movie and TV folder configuration to a JSON file.
    """
    def save_config(self):

        # Save config file...
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    """
    Scan movie directories, then save the movie file paths to a cache file.
    """
    def scan_movie_directories(self):

        # Scan movies library folders for list of movies
        movies = self.scan_directories(self.config["movie_dirs"])

        # Save list of movies to movies cache file...
        with open(self.movie_cache_path, 'w') as f:
            json.dump(movies, f, indent=2)

    """
    Scan TV directories, then save the episode file paths to a cache file.
    """
    def scan_tv_directories(self):

        # Scan TV library folders for list of TV shows
        tv_shows = self.scan_directories(self.config["tv_dirs"])

        # Save list of TV shows to TV cache file...
        with open(self.tv_cache_path, 'w') as f:
            json.dump(tv_shows, f, indent=2)

    """
    Recursively scan a list of directories for files.
    """
    def scan_directories(self, dir_list):

        # Initialize empty list of files
        all_files = []

        # Recursively scan each subdirectory in the specified directory...
        for path in dir_list:
            for root, _, files in os.walk(path):

                # Add each file found to the list of all files...
                for file in files:
                    full_path = os.path.join(root, file)
                    all_files.append(full_path)

        # Return list of all files found
        return all_files


"""
Main Menu Screen
"""
class MainMenuScreen(Screen):

    """
    Textual DOM initialization event handler.
    Initializes the main menu screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Title
        yield Container(Static(Pixels.from_image_path(self.app.base_path / "wolp-24.png"), id="logo"), Vertical(Static("Movie Wolp", id="title"), Static("Main Menu", id="subtitle"), id="container-title"), id="header")

        # Menu buttons
        yield Button("Search Movies...", id="button-search-movies")
        yield Button("Search TV Shows...", id="button-search-tv")
        yield Button("Configure Movie Wolp...", id="button-config")

        # Exit button
        yield Button("Exit Movie Wolp", id="button-exit")

    """
    Textual button click event handler.
    Handles the button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Search Movies button click...
        if event.button.id == "button-search-movies":
            self.app.push_screen(MovieSearchScreen())

        # Search TV Shows button click...
        elif event.button.id == "button-search-tv":
            self.app.push_screen(TVSearchScreen())

        # Configure Movie Wolp button click...
        elif event.button.id == "button-config":
            self.app.push_screen(ConfigurationScreen())

        # Exit Movie Wolp button click...
        elif event.button.id == "button-exit":

            # Exit
            self.app.exit()


"""
Configuration Screen
"""
class ConfigurationScreen(Screen):

    """
    Textual DOM initialization event handler.
    Initializes the configuration screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Title
        yield Container(Static(Pixels.from_image_path(self.app.base_path / "wolp-24.png"), id="logo"), Vertical(Static("Movie Wolp", id="title"), Static("Configuration Menu", id="subtitle"), id="container-title"), id="header")

        # Menu buttons
        yield Button("Movie Library folders...", id="button-add-movies")
        yield Button("TV Show Library folders...", id="button-add-tv")
        yield Button("Save & Return to Main Menu", id="button-config-save")

        # Exit button
        yield Button("Exit Movie Wolp", id="button-exit")

    """
    Textual button click event handler.
    Handles the button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Movie Library button click...
        if event.button.id == "button-add-movies":
            self.app.push_screen(FolderListScreen("movie_dirs"))

        # TV Show Library button click...
        elif event.button.id == "button-add-tv":
            self.app.push_screen(FolderListScreen("tv_dirs"))

        # Save & Return button click...
        elif event.button.id == "button-config-save":

            # Apply any movie/tv folder screen changes before saving...
            if hasattr(self.app, "temp_folder_lists"):
                for key, val in self.app.temp_folder_lists.items():
                    self.app.config[key] = val

            # Save configuration file
            self.app.save_config()

            # Save library cache files
            self.app.scan_movie_directories()
            self.app.scan_tv_directories()

            # Show main menu
            self.app.pop_screen()
            self.app.push_screen(MainMenuScreen())

        # Exit Movie Wolp button click...
        elif event.button.id == "button-exit":

            # Exit
            self.app.exit()


"""
Generic Folder List Screen
"""
class FolderListScreen(Screen):

    """
    Class constructor.
    """
    def __init__(self, key):
        super().__init__()

        # Get folder list key so we know which folder list to edit
        self.key = key

    """
    Textual DOM initialization event handler.
    Initializes the generic folder list screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize input bar and folder list
        self.input = Input(placeholder="Enter a folder path")
        self.list_view = ListView()

        # Initialize subtitle text according to folder list key
        subtitle_text = ""
        if self.key == "movie_dirs":
            subtitle_text = "Movie Library Folders"
        elif self.key == "tv_dirs":
            subtitle_text = "TV Show Library Folders"

        # Title
        yield Container(Static(Pixels.from_image_path(self.app.base_path / "wolp-24.png"), id="logo"), Vertical(Static("Movie Wolp", id="title"), Static(subtitle_text, id="subtitle"), id="container-title"), id="header")

        # Input bar
        yield self.input

        # Menu buttons
        yield Horizontal(Button("Add Folder", id="button-add-folder"), Button("Remove Selected", id="button-remove-folder"), id="container-horizontal")

        # Folder list
        yield self.list_view

        # Back button
        yield Button("Back", id="button-back")

    """
    Textual DOM mounted event handler.
    Handles the events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self) -> None:

        # Create temp folder list storage if it doesn't exist...
        if not hasattr(self.app, "temp_folder_lists"):
            self.app.temp_folder_lists = {}

        # Load existing temp list if available...
        if self.key in self.app.temp_folder_lists:
            self.folder_list = self.app.temp_folder_lists[self.key]

        # Otherwise, copy folder list from config...
        else:
            self.folder_list = list(self.app.config[self.key])
            self.app.temp_folder_lists[self.key] = self.folder_list

        # Refresh folder list display
        self.refresh_list()

    """
    Textual button click event handler.
    Handles the button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Add Folder button clicked...
        if event.button.id == "button-add-folder":

            # Get input folder path
            path = self.input.value.strip()

            # If path is not empty and not already in list...
            if path and path not in self.folder_list:

                # Add folder path to list
                self.folder_list.append(path)
                self.input.value = ""
                self.refresh_list()

        # Remove Selected button clicked...
        elif event.button.id == "button-remove-folder":
            index = self.list_view.index

            # If a valid item is selected...
            if index is not None and 0 <= index < len(self.folder_list):

                # Remove selected item from list
                del self.folder_list[index]
                self.refresh_list()

        # Back button clicked...
        elif event.button.id == "button-back":

            # Show main menu
            self.app.pop_screen()

    """
    Refresh the folder list view with current folder paths.
    """
    def refresh_list(self):

        # Clear folder list
        self.list_view.clear()

        # Refresh folder list...
        for folder in self.folder_list:
            self.list_view.append(ListItem(Static(folder)))


"""
Movie Search Screen
"""
class MovieSearchScreen(Screen):

    """
    Textual DOM initialization event handler.
    Initializes the movie search screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize search bar and search results
        self.input = Input(placeholder="Start typing a movie title...")
        self.results = ListView(id="search-results")

        # Title
        yield Container(Static(Pixels.from_image_path(self.app.base_path / "wolp-24.png"), id="logo"), Vertical(Static("Movie Wolp", id="title"), Static("Search Movies", id="subtitle"), id="container-title"), id="header")

        # Search bar
        yield self.input

        # Search results
        yield self.results

        # Back / Rescan Library buttons
        yield Horizontal(Button("Back to Main Menu", id="button-back"), Button("Rescan Movie Library", id="button-rescan-library"), id="container-horizontal")

    """
    Textual DOM mounted event handler.
    Handles the events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self):

        # Place cursor in search bar
        self.input.focus()

        # Load movie cache file...
        with open(self.app.movie_cache_path) as f:
            self.movies = json.load(f)

        # Initialize filtered movie list
        self.filtered = self.movies

        # Display search results
        self.refresh_results()

    """
    Input field changed event handler.
    Handles the input field text changed events for all text input fields in the Textual DOM.
    """
    def on_input_changed(self, event: Input.Changed) -> None:

        # Get input field text
        text = event.value.strip().lower()

        # Search movies for input field text
        self.filtered = [m for m in self.movies if text in os.path.basename(m).lower()]

        # Refresh search results
        self.refresh_results()

    """
    Mouse click event handler.
    Handles the mouse click events for all controls in the Textual DOM.
    """
    def on_click(self, event: events.Click) -> None:

        # If mouse was double-clicked...
        if event.chain == 2:

            # Attempt to handle list item double-click event
            self.handle_list_item_double_click(event.control)

    """
    List item mouse double-click event handler.
    Handles the mouse double-click events for all list items in the Textual DOM.
    """
    def handle_list_item_double_click(self, item: ListItem) -> None:

        # If the double-clicked list item has text...
        if item and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file exists...
            if file_path and Path(file_path).exists():

                # Attempt to open the file location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(Path(file_path).resolve())])

    """
    Textual button click event handler.
    Handles the button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Rescan button clicked...
        if event.button.id == "button-rescan-library":

            # Rescan movie library
            self.app.scan_movie_directories()

            # Reload movie cache file...
            with open(self.app.movie_cache_path) as f:
                self.movies = json.load(f)

            # Update filtered list of movies
            self.filtered = self.movies
            self.input.value = ""
            self.refresh_results()

        # Back button clicked...
        elif event.button.id == "button-back":

            # Show main menu
            self.app.pop_screen()

    """
    Refresh the search results list view with filtered movies.
    """
    def refresh_results(self):

        # Clear search results
        self.results.clear()

        # List movies according to search terms...
        for path in self.filtered[:50]:
            self.results.append(ListItem(Static(path)))


"""
TV Search Screen
"""
class TVSearchScreen(Screen):

    """
    Textual DOM initialization.
    Initializes the TV search screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize search bar and search results
        self.input = Input(placeholder="Start typing a TV show title...")
        self.results = ListView(id="search-results")

        # Title
        yield Container(Static(Pixels.from_image_path(self.app.base_path / "wolp-24.png"), id="logo"), Vertical(Static("Movie Wolp", id="title"), Static("Search TV Shows", id="subtitle"), id="container-title"), id="header")

        # Search bar
        yield self.input

        # Search results
        yield self.results

        # Back / Rescan Library buttons
        yield Horizontal(Button("Back to Main Menu", id="button-back"), Button("Rescan TV Show Library", id="button-rescan-library"), id="container-horizontal")

    """
    Textual DOM mounted event handler.
    Handles the events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self):

        # Focus the search input box
        self.input.focus()

        # Load TV episodes cache file...
        with open(self.app.tv_cache_path) as f:
            self.episodes = json.load(f)

        # Initialize list of TV show directories (two levels up from each episode)
        self.shows = sorted({Path(p).parent.parent for p in self.episodes})

        # Initialize navigation
        self.level = "root"              # "root" | "show" | "season"
        self.cur_show = None             # Current selected episode file path
        self.cur_season = None           # Current selected season directory path
        self.filtered = list(self.shows) # Filtered list of TV shows

        # Refresh search results
        self.refresh_results()

    """
    Input field changed event handler.
    Handles the input field text changed events for all text input fields in the Textual DOM.
    """
    def on_input_changed(self, event: Input.Changed) -> None:

        # Get input field text
        text = event.value.strip().lower()

        # Search movies for input field text
        self.filtered = [s for s in self.shows if text in s.name.lower()]

        # Reset navigation to root level
        self.level = "root"
        self.cur_show = None
        self.cur_season = None

        # Refresh search results
        self.refresh_results()

    """
    Mouse click event handler.
    Handles the mouse click events for all controls in the Textual DOM.
    """
    def on_click(self, event: events.Click) -> None:

        # If mouse was double-clicked...
        if event.chain == 2:

            # Attempt to handle list item double-click event
            self.handle_list_item_double_click(event.control)

    """
    List item mouse double-click event handler.
    Handles the mouse double-click events for all list items in the Textual DOM.
    """
    def handle_list_item_double_click(self, item: ListItem) -> None:

        # If the double-clicked list item has text...
        if item and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path_txt = str(item.renderable)

            # If the file does not exist...
            if not file_path_txt:

                # Skip file
                return

            # Convert file path to Path object
            path = Path(file_path_txt)

            # "root"
            # Show root TV show directories...
            if self.level == "root" and path.is_dir():
                self.level = "show"
                self.cur_show = path
                self.refresh_results()
                return

            # "show"
            # Show seasons in the selected TV show...
            if self.level == "show" and path.is_dir():
                self.level = "season"
                self.cur_season = path
                self.refresh_results()
                return

            # "season"
            # Show episodes in the selected season...
            if self.level == "season":

                # Navigate up one level...
                if path == self.cur_season.parent:
                    self.level = "show"
                    self.cur_season = None
                    self.refresh_results()
                    return

                # Attempt to open the file location in Dolphin
                if path.is_file() and path.exists():
                    subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                    return

    """
    Textual button click event handler.
    Handles the button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Rescan button clicked...
        if event.button.id == "button-rescan-library":

            # Rescan TV library
            self.app.scan_tv_directories()

            # Reload TV cache file...
            with open(self.app.tv_cache_path) as f:
                self.episodes = json.load(f)

            # Update filtered list of movies
            self.shows = sorted({Path(p).parent.parent for p in self.episodes})
            self.filtered = list(self.shows)
            self.input.value = ""

            # Reset navigation to root level
            self.level = "root"
            self.cur_show = None
            self.cur_season = None

            # Refresh results
            self.refresh_results()

        # Back button clicked...
        elif event.button.id == "button-back":

            # Show main menu
            self.app.pop_screen()

    """
    Refresh the search results list view with filtered TV shows/season/episodes based on the current navigation level.
    """
    def refresh_results(self) -> None:

        # Clear search results
        self.results.clear()

        # "root"
        # Show root TV show directories...
        if self.level == "root":
            for path in self.filtered[:50]:
                self.results.append(ListItem(Static(str(path))))

        # "show"
        # Show seasons in the selected TV show...
        elif self.level == "show":
            seasons = sorted(p for p in self.cur_show.iterdir() if p.is_dir())
            for season in seasons:
                self.results.append(ListItem(Static(str(season))))

        # "season"
        # Show episodes in the selected season...
        elif self.level == "season":

            # Add 'Up' path to navigate back to the TV show
            up_path = self.cur_season.parent
            self.results.append(ListItem(Static(str(up_path))))

            # Show all season episodes...
            episodes = sorted(p for p in self.cur_season.iterdir() if p.is_file())
            for ep in episodes:
                self.results.append(ListItem(Static(str(ep))))


# Run Movie Wolp!
if __name__ == "__main__":
    app = MovieWolp()
    app.run()

