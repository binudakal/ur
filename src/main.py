import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .start_window import StartWindow
from .game_window import GameWindow
# from .game import *


class UrApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.binudakal.ur',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about)
        self.create_action('preferences', self.on_preferences)
        self.win = None

    def do_activate(self):
        """Called when the application is activated.
        We raise the application's main window, creating it if
        necessary.
        """

        win = self.props.active_window

        if not win:
            win = StartWindow(application=self)
            self.menuWin = win # store the menu window
            self.win = self.menuWin # set the current app window

        win.present()

    def on_about(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                    application_name='Ur',
                    application_icon='com.github.binudakal.ur',
                    developer_name='Binuda Kalugalage',
                    license_type=Gtk.License.GPL_3_0,
                    website='https://github.com/binudakal/ur',
                    issue_url='https://github.com/binudakal/ur/issues/new',
                    version='0.1.0',
                    developers=[
                            'Binuda Kalugalage https://github.com/binudakal'
                    ],
                    designers=[
                        'Binuda Kalugalage https://github.com/binudakal'
                    ],
                    copyright='© Binuda Kalugalage'
                )
        about.present()

    def on_win(self, winner):
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
            self.win = GameWindow(application=self)

            self.win.present()

        elif response == "main_menu":
            self.win.destroy()
            self.win = self.menuWin

            self.win.present()

    def on_impossible(self, player):
        toast = Adw.Toast(
            title = f"{player.name} has no possible moves!"
        )

        self.win.toast_overlay. add_toast(toast)


    def on_preferences(self, widget, _):
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

