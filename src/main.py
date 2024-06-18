import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import GnomeUrWindow
from .game import *


class ButtonManager:
    def __init__(self, window):
        self.window = window

    def set_sensitivity(self, button_id, sensitivity):
        """Set the sensitivity of a button."""
        self.window.set_sensitivity(button_id, sensitivity)

    def disable_all_buttons(self):
        """Disable all buttons."""
        button_ids = [
            "LTile1", "LTile2", "LTile3", "LTile4", "LTile13", "LTile14",
            "CTile5", "CTile6", "CTile7", "CTile8", "CTile9", "CTile10", "CTile11", "CTile12",
            "RTile1", "RTile2", "RTile3", "RTile4", "RTile13", "RTile14"
        ]
        for button_id in button_ids:
            self.set_sensitivity(button_id, False)

class GnomeUrApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.binudakal.gnomeur',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.button_manager = None
        self.win = None

    def do_activate(self):
        """Called when the application is activated.
        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = GnomeUrWindow(application=self)
            self.win = win
            self.button_manager = ButtonManager(win)
            self.game = Game(self, win)

        self.game.play_game()
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Ur',
                                application_icon='com.github.binudakal.gnomeur',
                                developer_name='Binuda Kalugalage',
                                version='0.1.0',
                                developers=['Binuda Kalugalage'],
                                copyright='© 2024 Binuda Kalugalage')
        about.present()

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
    app = GnomeUrApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main(None)

