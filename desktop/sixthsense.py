import requests
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import matplotlib.style as mpl_style

mpl_style.use("default")


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="SixthSense")
        self.set_default_size(800, 600)

        # Create a layout container
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(layout)

        # Create a figure and canvas for plotting
        self.figure = Figure()
        # Set the background color of the plot
        self.figure.patch.set_facecolor("#242424")
        self.canvas = FigureCanvas(self.figure)
        layout.pack_start(self.canvas, True, True, 0)

        # Create an empty plot
        self.x_data = []
        self.y_data = []
        (self.line,) = self.figure.add_subplot(1, 1, 1).plot([], [])
        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)

        # Start the continuous data fetching
        self.sample_counter = 0
        self.fetch_data()

        # Create buttons to select the plot type
        self.button_temperature = Gtk.Button(label="Temperature")
        self.button_pressure = Gtk.Button(label="Pressure")
        self.button_humidity = Gtk.Button(label="Humidity")
        self.button_config = Gtk.Button()
        self.button_config_image = Gtk.Image.new_from_icon_name(
            "preferences-system-symbolic", Gtk.IconSize.BUTTON
        )
        self.button_config.add(self.button_config_image)
        self.button_temperature.connect("clicked", self.on_button_temperature_clicked)
        self.button_pressure.connect("clicked", self.on_button_pressure_clicked)
        self.button_humidity.connect("clicked", self.on_button_humidity_clicked)
        self.button_config.connect("clicked", self.on_button_config_clicked)
        button_box = Gtk.Box(spacing=10)
        button_box.set_margin_bottom(10)
        # button_box.set_margin_top(10)
        button_box.set_margin_left(10)
        button_box.set_margin_right(10)
        button_box.pack_start(self.button_temperature, True, True, 0)
        button_box.pack_start(self.button_pressure, True, True, 0)
        button_box.pack_start(self.button_humidity, True, True, 0)
        button_box.pack_end(self.button_config, False, False, 0)

        layout.pack_start(button_box, False, False, 0)

    def on_button_temperature_clicked(self, button):
        self.sensor_type = "temperature"

    def on_button_pressure_clicked(self, button):
        self.sensor_type = "pressure"

    def on_button_humidity_clicked(self, button):
        self.sensor_type = "humidity"

    def on_button_config_clicked(self, button):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Configuration",
        )
        dialog.format_secondary_text("This is where you can configure settings.")
        dialog.run()
        dialog.destroy()

    def fetch_data(self):
        # Fetch data from the REST API
        response = requests.get("http://127.0.0.1:8000/sensors/all?t=c&p=hpa&h=perc")

        # Parse the data and add it to the plot
        temperature = response.json()["temperature"]["value"]
        pressure = response.json()["pressure"]["value"]
        humidity = response.json()["humidity"]["value"]

        self.sample_counter += 1
        self.x_data.append(self.sample_counter)
        self.y_data.append(temperature)

        # Update the plot
        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)
        self.line.set_color((0.5, 0.5, 0.5))
        self.line.axes.relim()
        self.line.axes.autoscale_view(True, True, True)
        self.canvas.draw()

        # Schedule the next data fetch
        GLib.timeout_add_seconds(1, self.fetch_data)


win = MyWindow()
win.connect("destroy", Gtk.main_quit)

# Add the figure to the window
box = win.get_children()[0]
box.pack_start(win.canvas, True, True, 0)

win.show_all()
Gtk.main()
