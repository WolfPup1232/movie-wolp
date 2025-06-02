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
from shutil import disk_usage

# Import Textual Library Classes
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.screen import Screen
from textual.suggester import Suggester, SuggestFromList
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Input
from textual.widgets._input import Selection
from rich.console import Console
from rich.text import Text

# Import Rich Pixels Library Classes
from rich_pixels import Pixels

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
        self.config = {"movie_directories": [], "tv_directories": []}

        # Initialize Movie Wolp's media library objects
        self.movies = {}
        self.tv_shows = {}

        # Initialize list of mounted drives
        self.drives = []

    """
    Textual DOM mounted event handler.
    Handles events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self) -> None:

        # If the config file, movie cache file, and TV cache file all exist...
        if (self.config_path.exists() and self.movie_cache_path.exists() and self.tv_cache_path.exists()):

            # Load config file...
            with open(self.config_path) as file:
                self.config = json.load(file)

            # Load movie cache file...
            with open(self.movie_cache_path) as file:
                self.movies = json.load(file)

            # Load TV cache file...
            with open(self.tv_cache_path) as file:
                self.tv_shows = json.load(file)

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
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent=2)

    """
    Scan movie directories, then save the movie file paths to a cache file.
    """
    def scan_movie_directories(self):

        # Scan movies library folders for list of movies
        movies = self.scan_directories(self.config["movie_directories"])

        # Save list of movies to movies cache file...
        with open(self.movie_cache_path, 'w') as file:
            json.dump(movies, file, indent=2)

    """
    Scan TV directories, then save the episode file paths to a cache file.
    """
    def scan_tv_directories(self):

        # Initialize empty list of TV episodes
        episode_files = []

        # Scan each TV show library folder...
        for tv_root in self.config["tv_directories"]:
            for tv_show in os.scandir(tv_root):

                # Skip loose files at this level...
                if not tv_show.is_dir():
                    continue

                # Add each TV show episode to the list of TV episodes...
                for item in os.scandir(tv_show.path):
                    if item.is_file():
                        episode_files.append(item.path)

                # Scan for "season" subfolders...
                for item in os.scandir(tv_show.path):
                    if item.is_dir() and item.name.lower().startswith("season"):

                        # Add each season's episodes to the list of TV episodes...
                        for season_item in os.scandir(item.path):
                            if season_item.is_file():
                                episode_files.append(season_item.path)

        # Save list of TV episodes
        with open(self.tv_cache_path, 'w') as file:
            json.dump(episode_files, file, indent=2)

    """
    Recursively scan a list of directories for files.
    """
    def scan_directories(self, directory_list):

        # Initialize empty list of files
        all_files = []

        # Recursively scan each subdirectory in the specified directory...
        for path in directory_list:
            for root, _, files in os.walk(path):

                # Add each file found to the list of all files...
                for file in files:
                    full_path = os.path.join(root, file)
                    all_files.append(full_path)

        # Return list of all files found
        return all_files

    """
    Get Textual DOM title element.
    """
    def get_title(self):
        return Static("Movie Wolp", id="title")

    """
    Get Textual DOM logo element.
    """
    def get_logo(self):
        return Static(Pixels.from_image_path(self.base_path / "wolp-24.png"), id="logo")

"""
Main Menu Screen
"""
class MainMenuScreen(Screen):

    """
    Textual DOM initialization event handler.
    Initializes the main menu screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize Textual DOM elements
        self.subtitle = Static("Main Menu", id="subtitle")

        # Header
        yield Container(self.app.get_logo(), Vertical(self.app.get_title(), self.subtitle, id="container-title"), id="header")

        # Menu buttons
        yield Button("Search Movies...", id="button-search-movies")
        yield Button("Search TV Shows...", id="button-search-tv")
        yield Button("Configure Movie Wolp...", id="button-config")

        # Exit button
        yield Button("Exit Movie Wolp", id="button-exit")

    """
    Textual button click event handler.
    Handles button click events for all buttons in the Textual DOM.
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

        # Initialize Textual DOM elements
        self.subtitle = Static("Configuration Menu", id="subtitle")

        # Header
        yield Container(self.app.get_logo(), Vertical(self.app.get_title(), self.subtitle, id="container-title"), id="header")

        # Menu buttons
        yield Button("Movie Library folders...", id="button-add-movies")
        yield Button("TV Show Library folders...", id="button-add-tv")
        yield Button("Save & Rescan Libraries", id="button-config-save")

        # Exit button
        yield Button("Exit Movie Wolp", id="button-exit")

    """
    Textual DOM mounted event handler.
    Handles events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self) -> None:

        # Get list of mounted drives...
        self.app.drives = list(reversed([os.path.join("/mnt", drive)
                                         for drive in os.listdir("/mnt")
                                         if os.path.isdir(os.path.join("/mnt", drive))]))

    """
    Textual button click event handler.
    Handles button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Movie Library button click...
        if event.button.id == "button-add-movies":
            self.app.push_screen(FolderListScreen("movie_directories"))

        # TV Show Library button click...
        elif event.button.id == "button-add-tv":
            self.app.push_screen(FolderListScreen("tv_directories"))

        # Save & Return button click...
        elif event.button.id == "button-config-save":

            # Apply any movie/tv folder screen changes before saving...
            if hasattr(self.app, "temp_folder_lists"):
                for key, value in self.app.temp_folder_lists.items():
                    self.app.config[key] = value

            # Save configuration file
            self.app.save_config()

            # Save library cache files
            self.app.scan_movie_directories()
            self.app.scan_tv_directories()

            # Show main menu
            self.app.pop_screen()
            self.app.push_screen(MainMenuScreen())

             # Notify user
            self.app.notify("Rescan successfully completed!")

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

        # Initialize value indicating the last-clicked mouse button
        self.mouse_button_clicked = 1

    """
    Textual DOM initialization event handler.
    Initializes the generic folder list screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize Textual DOM elements
        self.subtitle = Static({"movie_directories": "Movie Library Folders", "tv_directories": "TV Show Library Folders"}.get(self.key, ""), id="subtitle")
        self.input = FolderBar(placeholder="Enter a folder path", suggester=SuggestFromList(self.app.drives, case_sensitive=False))
        self.list_view = ListView(id="search-results")

        # Header
        yield Container(self.app.get_logo(), Vertical(self.app.get_title(), self.subtitle, id="container-title"), id="header")

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
    Handles events which occur immediately after the Textual DOM has been initialized.
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
    Mouse down event handler.
    Handles mouse button down events for the entire Textual DOM.
    """
    def on_mouse_down(self, event: events.MouseDown) -> None:

        # Detect left-click...
        if event.button == 1:
            self.mouse_button_clicked = 1

        # Detect middle-click...
        elif event.button == 2:
            self.mouse_button_clicked = 2

        # Detect right-click...
        elif event.button == 3:
            self.mouse_button_clicked = 3

    """
    Mouse click event handler.
    Handles mouse click events for all controls in the Textual DOM.
    """
    def on_click(self, event: events.Click) -> None:

        # If the mouse was single-clicked...
        if event.chain == 1:

            # If the click was a left-click...
            if self.mouse_button_clicked == 1:

                # Handle logo's left-click event
                self.handle_logo_left_click(event.control)

            # Otherwise, the click was a right-click...
            elif self.mouse_button_clicked == 3:

                # Handle list item's right-click event
                self.handle_list_item_right_click(event.control)

        # Otherwise, if the mouse was double-clicked...
        elif event.chain == 2:

            # If the second click was a left-click...
            if self.mouse_button_clicked == 1:

                # Handle input bar's double-click event
                self.handle_input_double_click()

                # Handle list item's double-click event
                self.handle_list_item_double_click(event.control)

    """
    Logo mouse left-click event handler.
    Handles mouse left-click events for the header logo in the Textual DOM.
    """
    def handle_logo_left_click(self, logo: Static) -> None:

        # If the main logo was clicked...
        if logo and logo.id == 'logo':

            # Show main menu
            self.app.pop_screen()

    """
    Input bar mouse double-click event handler.
    Handles mouse double-click events for the input bar.
    """
    def handle_input_double_click(self) -> None:

        # Select all text in the input bar
        self.input.action_select_all()

    """
    List item mouse right-click event handler.
    Handles mouse right-click events for all list items in the Textual DOM.
    """
    def handle_list_item_right_click(self, item: ListItem) -> None:

        # If the right-clicked list item is a folder...
        if item and item.name == 'folder' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # If the file path exists...
            if path.exists():

                # Open the file path location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                return

    """
    List item mouse double-click event handler.
    Handles mouse double-click events for all list items in the Textual DOM.
    """
    def handle_list_item_double_click(self, item: ListItem) -> None:

        # If the double-clicked list item is a folder...
        if item and item.name == 'folder' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # If the file path exists...
            if path.exists():

                # Open the file path location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                return

    """
    Textual button click event handler.
    Handles button click events for all buttons in the Textual DOM.
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
            self.list_view.append(ListItem(Static(folder, name='folder')))

"""
Movie Search Screen
"""
class MovieSearchScreen(Screen):

    """
    Class constructor.
    """
    def __init__(self):
        super().__init__()

        # Initialize value indicating the last-clicked mouse button
        self.mouse_button_clicked = 1

    """
    Textual DOM initialization event handler.
    Initializes the movie search screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize Textual DOM elements
        self.subtitle = Static("Search Movies", id="subtitle")
        self.diskinfo = Static("", id="container-disk-info")
        self.search = SearchBar(placeholder="Start typing a movie title...")
        self.results = ListView(id="search-results")

        # Title
        yield Container(self.app.get_logo(), Vertical(self.app.get_title(), self.subtitle, id="container-title"), self.diskinfo, id="header")

        # Search bar
        yield self.search

        # Search results
        yield self.results

        # Back / Rescan Library buttons
        yield Horizontal(Button("Back to Main Menu", id="button-back"), Button("Rescan Movie Library", id="button-rescan-library"), id="container-horizontal")

    """
    Textual DOM mounted event handler.
    Handles events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self):

        # Place cursor in search bar
        self.search.focus()

        # Load movie cache file...
        with open(self.app.movie_cache_path) as file:
            self.movies = json.load(file)

        # Initialize filtered movie list
        self.filtered = self.movies

        # Display search results
        self.refresh_results()

    """
    Input field changed event handler.
    Handles input field text changed events for all input fields in the Textual DOM.
    """
    def on_input_changed(self, event: Input.Changed) -> None:

        # Get input field text
        text = event.value.strip().lower()

        # Search movies for input field text
        self.filtered = [movie for movie in self.movies if text in os.path.basename(movie).lower()]

        # Refresh search results
        self.refresh_results()

    """
    Mouse down event handler.
    Handles mouse button down events for the entire Textual DOM.
    """
    def on_mouse_down(self, event: events.MouseDown) -> None:

        # Detect left-click...
        if event.button == 1:
            self.mouse_button_clicked = 1

        # Detect middle-click...
        elif event.button == 2:
            self.mouse_button_clicked = 2

        # Detect right-click...
        elif event.button == 3:
            self.mouse_button_clicked = 3

    """
    Mouse click event handler.
    Handles mouse click events for all controls in the Textual DOM.
    """
    def on_click(self, event: events.Click) -> None:

        # If the mouse was single-clicked...
        if event.chain == 1:

            # If the click was a left-click...
            if self.mouse_button_clicked == 1:

                # Reset disk usage DOM element
                self.query_one("#container-disk-info", Static).update("")

                # Handle logo's left-click event
                self.handle_logo_left_click(event.control)

                # Handle list item's left-click event
                self.handle_list_item_left_click(event.control)

            # Otherwise, if the click was a right-click...
            elif self.mouse_button_clicked == 3:

                # Handle list item's right-click event
                self.handle_list_item_right_click(event.control)

        # Otherwise, if the mouse was double-clicked...
        elif event.chain == 2:

            # If the second click was a left-click...
            if self.mouse_button_clicked == 1:

                # Handle search bar's double-click event
                self.handle_search_double_click()

                # Handle list item's double-click event
                self.handle_list_item_double_click(event.control)

    """
    Logo mouse left-click event handler.
    Handles mouse left-click events for the header logo in the Textual DOM.
    """
    def handle_logo_left_click(self, logo: Static) -> None:

        # If the main logo was clicked...
        if logo and logo.id == 'logo':

            # Show main menu
            self.app.pop_screen()

    """
    Search bar mouse double-click event handler.
    Handles mouse double-click events for the search bar.
    """
    def handle_search_double_click(self) -> None:

        # Select all text in the search bar
        self.search.action_select_all()

    """
    List item mouse left-click event handler.
    Handles mouse left-click events for all list items in the Textual DOM.
    """
    def handle_list_item_left_click(self, item: ListItem) -> None:

        # If the left-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # Get disk path from file path...
            while path.parent != Path("/mnt") and path != path.parent:
                path = path.parent

            # Attempt to read and output disk usage...
            try:

                # Get disk usage from file path
                usage = disk_usage(path)

                # Calculate disk usage
                total_space = usage.total / (1024 ** 3)
                free_space = usage.free / (1024 ** 3)

                # Format disk usage output
                text = Text()
                text.append(f"\n{path}\n\n", style="bold")
                text.append(f"{free_space:.1f} GB ", style="bold")
                text.append(f"free\n")
                text.append(f"{total_space:.1f} GB total")

                # Update disk usage DOM element
                self.query_one("#container-disk-info", Static).update(text)

            # Catch errors...
            except Exception as exception:

                # Format error output
                text = Text()
                text.append(f"\nError checking disk:\n\n", style="bold")
                text.append(f"{exception}")

                # Update disk usage DOM element
                self.query_one("#container-disk-info", Static).update(text)

    """
    List item mouse right-click event handler.
    Handles mouse right-click events for all list items in the Textual DOM.
    """
    def handle_list_item_right_click(self, item: ListItem) -> None:

        # If the right-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # If the file path exists...
            if path.exists():

                # Open the file path location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                return

    """
    List item mouse double-click event handler.
    Handles mouse double-click events for all list items in the Textual DOM.
    """
    def handle_list_item_double_click(self, item: ListItem) -> None:

        # If the double-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # If the file path exists...
            if path.exists():

                # Open the file path location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                return

    """
    Textual button click event handler.
    Handles button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Rescan button clicked...
        if event.button.id == "button-rescan-library":

            # Rescan movie library
            self.app.scan_movie_directories()

            # Reload movie cache file...
            with open(self.app.movie_cache_path) as file:
                self.movies = json.load(file)

            # Update filtered list of movies
            self.filtered = self.movies
            self.search.value = ""
            self.refresh_results()

            # Notify user
            self.app.notify("Rescan successfully completed!")

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
        for path in self.filtered[:99]:

            # Initialize rich text
            text = Text()

            # Format directories...
            if os.path.isdir(path):

                # Get directory path elements
                parent_directory = os.path.dirname(path)
                folder_name = os.path.basename(path)

                # Format search result
                if parent_directory:
                    text.append(f"{parent_directory}/")
                text.append(folder_name, style="bold #40C057")

            # Format files...
            else:

                # Get file path elements
                directory_path = os.path.dirname(path)
                basename = os.path.basename(path)
                filename, extension = os.path.splitext(basename)

                # Format search result
                if directory_path:
                    text.append(f"{directory_path}/")
                text.append(filename, style="bold #40C057")
                text.append(extension)

            # Output search result
            self.results.append(ListItem(Static(text, name='result')))


"""
TV Search Screen
"""
class TVSearchScreen(Screen):

    """
    Class constructor.
    """
    def __init__(self):
        super().__init__()

        # Initialize value indicating the last-clicked mouse button
        self.mouse_button_clicked = 1

    """
    Textual DOM initialization.
    Initializes the TV search screen's UI controls.
    """
    def compose(self) -> ComposeResult:

        # Initialize Textual DOM elements
        self.subtitle = Static("Search TV Shows", id="subtitle")
        self.diskinfo = Static("", id="container-disk-info")
        self.search = SearchBar(placeholder="Start typing a TV show title...")
        self.results = ListView(id="search-results")

        # Title
        yield Container(self.app.get_logo(), Vertical(self.app.get_title(), self.subtitle, id="container-title"), self.diskinfo, id="header")

        # Search bar
        yield self.search

        # Search results
        yield self.results

        # Back / Rescan Library buttons
        yield Horizontal(Button("Back to Main Menu", id="button-back"), Button("Rescan TV Show Library", id="button-rescan-library"), id="container-horizontal")

    """
    Textual DOM mounted event handler.
    Handles events which occur immediately after the Textual DOM has been initialized.
    """
    def on_mount(self):

        # Focus the search bar
        self.search.focus()

        # Load TV episodes cache file...
        with open(self.app.tv_cache_path) as file:
            self.episodes = json.load(file)

        # Initialize list of TV show directories (two levels up from each episode)
        self.shows = sorted({Path(episode).parent.parent for episode in self.episodes})

        # Initialize navigation
        self.level = "root"                 # "root" | "show" | "season"
        self.current_show = None            # Current selected episode file path
        self.current_season = None          # Current selected season directory path
        self.filtered = list(self.shows)    # Filtered list of TV shows

        # Refresh search results
        self.refresh_results()

    """
    Input field changed event handler.
    Handles input field text changed events for all input fields in the Textual DOM.
    """
    def on_input_changed(self, event: Input.Changed) -> None:

        # Get input field text
        text = event.value.strip().lower()

        # Search movies for input field text
        self.filtered = [show for show in self.shows if text in show.name.lower()]

        # Reset navigation to root level
        self.level = "root"
        self.current_show = None
        self.current_season = None

        # Refresh search results
        self.refresh_results()

    """
    Mouse down event handler.
    Handles mouse button down events for the entire Textual DOM.
    """
    def on_mouse_down(self, event: events.MouseDown) -> None:

        # Detect left-click...
        if event.button == 1:
            self.mouse_button_clicked = 1

        # Detect middle-click...
        elif event.button == 2:
            self.mouse_button_clicked = 2

        # Detect right-click...
        elif event.button == 3:
            self.mouse_button_clicked = 3

    """
    Mouse click event handler.
    Handles mouse click events for all controls in the Textual DOM.
    """
    def on_click(self, event: events.Click) -> None:

        # If the mouse was single-clicked...
        if event.chain == 1:

            # If the click was a left-click...
            if self.mouse_button_clicked == 1:

                # Reset disk usage DOM element
                self.query_one("#container-disk-info", Static).update("")

                # Handle logo's left-click event
                self.handle_logo_left_click(event.control)

                # Handle list item's left-click event
                self.handle_list_item_left_click(event.control)

            # Otherwise, if the click was a right-click...
            elif self.mouse_button_clicked == 3:

                # Handle list item's right-click event
                self.handle_list_item_right_click(event.control)

        # Otherwise, if the mouse was double-clicked...
        elif event.chain == 2:

            # If the second click was a left-click...
            if self.mouse_button_clicked == 1:

                # Handle search bar's double-click event
                self.handle_search_double_click()

                # Handle list item's double-click event
                self.handle_list_item_double_click(event.control)

    """
    Logo mouse left-click event handler.
    Handles mouse left-click events for the header logo in the Textual DOM.
    """
    def handle_logo_left_click(self, logo: Static) -> None:

        # If the main logo was clicked...
        if logo and logo.id == 'logo':

            # Show main menu
            self.app.pop_screen()

    """
    Search bar mouse double-click event handler.
    Handles mouse double-click events for the search bar.
    """
    def handle_search_double_click(self) -> None:

        # Select all text in the search bar
        self.search.action_select_all()

    """
    List item mouse left-click event handler.
    Handles mouse left-click events for all list items in the Textual DOM.
    """
    def handle_list_item_left_click(self, item: ListItem) -> None:

        # If the left-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # Get disk path from file path...
            while path.parent != Path("/mnt") and path != path.parent:
                path = path.parent

            # Attempt to read and output disk usage...
            try:

                # Get disk usage from file path
                usage = disk_usage(path)

                # Calculate disk usage
                total_space = usage.total / (1024 ** 3)
                free_space = usage.free / (1024 ** 3)

                # Format disk usage output
                text = Text()
                text.append(f"\n{path}\n\n", style="bold")
                text.append(f"{free_space:.1f} GB ", style="bold")
                text.append(f"free\n")
                text.append(f"{total_space:.1f} GB total")

                # Update disk usage DOM element
                self.query_one("#container-disk-info", Static).update(text)

            # Catch errors...
            except Exception as exception:

                # Format error output
                text = Text()
                text.append(f"\nError checking disk:\n\n", style="bold")
                text.append(f"{exception}")

                # Update disk usage DOM element
                self.query_one("#container-disk-info", Static).update(text)

    """
    List item mouse right-click event handler.
    Handles mouse right-click events for all list items in the Textual DOM.
    """
    def handle_list_item_right_click(self, item: ListItem) -> None:

        # If the right-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # If the file path exists...
            if path.exists():

                # Open the file path location in Dolphin
                subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                return

    """
    List item mouse double-click event handler.
    Handles mouse double-click events for all list items in the Textual DOM.
    """
    def handle_list_item_double_click(self, item: ListItem) -> None:

        # If the double-clicked list item is a search result...
        if item and item.name == 'result' and hasattr(item, "renderable"):

            # Get the file path from the list item
            file_path = str(item.renderable)

            # If the file path is not set...
            if not file_path:

                # Skip file path
                return

            # Convert file path to Path object
            path = Path(file_path)

            # "root"
            # Show root TV show directories...
            if self.level == "root" and path.is_dir():
                self.level = "show"
                self.current_show = path
                self.refresh_results()
                return

            # "show"
            # Show seasons in the selected TV show...
            if self.level == "show" and path.is_dir():

                # Attempt to navigate up one level...
                if path == self.current_show.parent:
                    self.level = "root"
                    self.current_show = None
                    self.refresh_results()
                    return

                # Show TV show seasons
                self.level = "season"
                self.current_season = path
                self.refresh_results()
                return

            # "season"
            # Show episodes in the selected season...
            if self.level == "season":

                # Attempt to navigate up one level...
                if path == self.current_season.parent:
                    self.level = "show"
                    self.current_season = None
                    self.refresh_results()
                    return

                # If the file path exists...
                if path.is_file() and path.exists():

                    # Open the file path location in Dolphin
                    subprocess.Popen(["dolphin", "--select", str(path.resolve())])
                    return

    """
    Textual button click event handler.
    Handles button click events for all buttons in the Textual DOM.
    """
    def on_button_pressed(self, event: Button.Pressed) -> None:

        # Rescan button clicked...
        if event.button.id == "button-rescan-library":

            # Rescan TV library
            self.app.scan_tv_directories()

            # Reload TV cache file...
            with open(self.app.tv_cache_path) as file:
                self.episodes = json.load(file)

            # Update filtered list of movies
            self.shows = sorted({Path(episode).parent.parent for episodes in self.episodes})
            self.filtered = list(self.shows)
            self.search.value = ""

            # Reset navigation to root level
            self.level = "root"
            self.current_show = None
            self.current_season = None

            # Refresh results
            self.refresh_results()

            # Notify user
            self.app.notify("Rescan successfully completed!")

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

            # Get root level folders to exclude
            excluded_roots = set()
            for path in self.app.config["tv_directories"]:
                resolved_path = Path(path).resolve()
                excluded_roots.add(str(resolved_path))
                excluded_roots.add(str(resolved_path.parent))

            # Show all TV show directories...
            for path in self.filtered[:99]:
                if str(path.resolve()) not in excluded_roots:

                    # Get directory path elements
                    parent_directory = os.path.dirname(path)
                    folder_name = os.path.basename(path)

                    # Format search result
                    text = Text()
                    if parent_directory:
                        text.append(f"{parent_directory}/")
                    text.append(folder_name, style="bold #40C057")

                    # Output search result
                    self.results.append(ListItem(Static(text, name='result')))

        # "show"
        # Show seasons in the selected TV show...
        elif self.level == "show":

            # Add 'up one level' path to navigate back to the root level
            up_path = self.current_show.parent
            up_text = Text()
            up_text.append(str(up_path), style="bold #FBA454")
            self.results.append(ListItem(Static(up_text, name='result')))

            # Show all seasons...
            seasons = sorted(path for path in self.current_show.iterdir() if path.is_dir())
            for season in seasons:

                # Get directory path elements
                full_path = season.resolve()
                root_path = full_path.parent.parent
                show_folder = full_path.parent.name
                season_folder = full_path.name

                # Format search result
                text = Text()
                if root_path:
                    text.append(f"{root_path}/")
                    text.append(f"{show_folder}/", style="bold #40C057")
                    text.append(season_folder, style="bold #358E9A")

                # Output search result
                self.results.append(ListItem(Static(text, name='result')))

        # "season"
        # Show episodes in the selected season...
        elif self.level == "season":

            # Add 'up one level' path to navigate back to the TV show
            up_path = self.current_season.parent
            up_text = Text()
            up_text.append(str(up_path), style="bold #FBA454")
            self.results.append(ListItem(Static(up_text, name='result')))

            # Show all season episodes...
            episodes = sorted(path for path in self.current_season.iterdir() if path.is_file())
            for episode in episodes:

                # Resolve full path
                full_path = episode.resolve()
                root_path = full_path.parent.parent.parent
                show_folder = full_path.parent.parent.name
                season_folder = full_path.parent.name
                filename, extension = os.path.splitext(full_path.name)

                # Format search result
                text = Text()
                if root_path:
                    text.append(f"{root_path}/")
                text.append(f"{show_folder}/", style="bold #40C057")
                text.append(f"{season_folder}/", style="bold #358E9A")
                text.append(filename, style="bold #CE458B")
                text.append(extension, style="#CE458B")

                # Output search result
                self.results.append(ListItem(Static(text, name='result')))


"""
Folder Bar Widget
"""
class FolderBar(Input):

    # Initialize keyboard action bindings
    BINDINGS = [Binding("ctrl+a", "select_all", "Select All", show=False),
                Binding("tab", "autocomplete", "Autocomplete", show=False),]

    """
    Class constructor.
    """
    def __init__(self, placeholder: str = "", suggester: Suggester | None = None):
        super().__init__(placeholder=placeholder, suggester=suggester)

        # Get Movie Wolp's base file path
        self.base_path = Path(__file__).parent

    """
    Search bar Ctrl+A event handler.
    Handles the Select All keyboard binding.
    """
    def action_select_all(self) -> None:

        # Select all text in the search bar
        self.selection = Selection(0, len(self.value))

    """
    Search bar Tab event handler.
    Handles the Autocomplete keyboard binding.
    """
    def action_autocomplete(self) -> None:

        # If suggestion isn't blank...
        if self._suggestion != "":

            # Autocomplete text with suggestion
            self.value = self._suggestion

            # Move cursor to end
            self.cursor_position = len(self.value)

"""
Search Bar Widget
"""
class SearchBar(Input):

    # Initialize keyboard action bindings
    BINDINGS = [Binding("ctrl+a", "select_all", "Select All", show=False),]

    """
    Search bar Ctrl+A event handler.
    Handles the Select All keyboard binding.
    """
    def action_select_all(self) -> None:

        # Select all text in search bar
        self.selection = Selection(0, len(self.value))


# Run Movie Wolp!
if __name__ == "__main__":
    app = MovieWolp()
    app.run()

