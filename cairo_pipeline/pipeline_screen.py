import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject, GLib


class Pipeline_Screen(Gtk.DrawingArea):

    @staticmethod
    def MainRun(pipeline):
        """ Example use of the Screen/pipeline combo """
        window = Gtk.Window()
        window.connect("destroy", Gtk.main_quit)
        window.set_size_request(400, 400)
        widget = Pipeline_Screen(pipeline)
        widget.show()
        window.add(widget)
        window.present()
        Gtk.main()


    def __init__(self, pipeline, tick=50):
        Super(Screen, self).__init__()
        self.connect("draw", self.on_draw)
        GLib.timeout_add(tick, self.tick)
        self._pipeline = pipeline

    def tick(self):
        rect = self.get_allocation()
        self.get_window().invalidate_rect(rect, True)
        return True

    def on_draw(self, widget, event):
        self.cr = self.get_window().cairo_create()
        geom = self.get_window().get_geometry()
        self._pipeline.tick(self.cr)
