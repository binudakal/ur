import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import UrWindow
from .game import *


class UrApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.binudakal.ur',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.win = None

    def do_activate(self):
        """Called when the application is activated.
        We raise the application's main window, creating it if
        necessary.
        """

        win = self.props.active_window

        if not win:
            win = UrWindow(application=self)
            self.win = win

        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Ur',
                                application_icon='com.github.binudakal.ur',
                                developer_name='Binuda Kalugalage',
                                version='0.1.0',
                                developers=['Binuda Kalugalage'],
                                copyright='© 2024 Binuda Kalugalage')
        about.present()

    def on_win_action(self, winner):
        """Display an alert dialog when a player wins the game."""
        dialog = Adw.AlertDialog(
            heading=f"{winner.name} has won!",
            close_response="new_game",
        )

        # Set the buttons for the dialog
        dialog.add_response("new_game", "New Game")
        dialog.set_response_appearance("new_game", Adw.ResponseAppearance.SUGGESTED)

        dialog.add_response("main_menu", "Main Menu")

        # Connect to the response signal
        dialog.choose(self.win, None, self.on_win_response)

    def on_win_response(self, _dialog, task):
        response = _dialog.choose_finish(task)
        print(f'Selected "{response}" response.')

        if response == "new_game":
            self.win.destroy()
            self.win = UrWindow(application=self)
            self.win.present()

        elif response == "main_menu":
            pass

    def on_impossible(self, player):
        toast = Adw.Toast(
            title = f"{player.name} has no possible moves!"
        )

        self.win.toast_overlay. add_toast(toast)


    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.
        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)



def main(version):
    """The application's entry point."""
    app = UrApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main(None)

