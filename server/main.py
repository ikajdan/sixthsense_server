#!/usr/bin/env python3

from typing import Annotated
import uvicorn
from enum import Enum
from pydantic import Field
from sense_emu import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware


hat = SenseHat()
app = FastAPI()

# TODO: Dev only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


joy_h_count = 0
joy_v_count = 0
joy_c_count = 0


def led_to_pos(led):
    ROW_SIZE = 8
    x = led % ROW_SIZE
    y = led // ROW_SIZE
    return [x, y]


def hex_to_rgb(hex):
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


def joy_pushed_up(event):
    if event.action != ACTION_RELEASED:
        global joy_v_count
        joy_v_count = joy_v_count + 1


def joy_pushed_down(event):
    if event.action != ACTION_RELEASED:
        global joy_v_count
        joy_v_count = joy_v_count - 1


def joy_pushed_left(event):
    if event.action != ACTION_RELEASED:
        global joy_h_count
        joy_h_count = joy_h_count - 1


def joy_pushed_right(event):
    if event.action != ACTION_RELEASED:
        global joy_h_count
        joy_h_count = joy_h_count + 1


def joy_pushed_middle(event):
    if event.action != ACTION_RELEASED:
        global joy_c_count
        joy_c_count = joy_c_count + 1


hat.stick.direction_up = joy_pushed_up
hat.stick.direction_down = joy_pushed_down
hat.stick.direction_left = joy_pushed_left
hat.stick.direction_right = joy_pushed_right
hat.stick.direction_middle = joy_pushed_middle


class Sensors(str, Enum):
    temperature = "temperature"
    pressure = "pressure"
    humidity = "humidity"
    roll = "roll"
    pitch = "pitch"
    yaw = "yaw"


class Units:
    class Temperature(str, Enum):
        celsius = "celsius"
        fahrenheit = "fahrenheit"

    class Pressure(str, Enum):
        hectopascals = "hectopascals"
        mercury = "mercury"

    class Humidity(str, Enum):
        percent = "percent"
        normalized = "normalized"

    class Orientation(str, Enum):
        degrees = "degrees"
        radians = "radians"


@app.get("/")
async def root():
    data = {}
    data["message"] = "API server is up"
    return data


@app.get("/sensors/all")
async def get_all_sensors(
    t: str | None = None,
    p: str | None = None,
    h: str | None = None,
    ro: str | None = None,
    pi: str | None = None,
    ya: str | None = None,
):
    data = {}
    match t:
        case "c":
            data_child = {}
            data_child["name"] = "Temperature"
            data_child["value"] = hat.temperature
            data_child["unit"] = " °C"
            data["temperature"] = data_child
        case "f":
            data_child = {}
            data_child["name"] = "Temperature"
            data_child["value"] = hat.temperature * 9 / 5 + 32
            data_child["unit"] = " F"
            data["temperature"] = data_child

    data_child = {}
    data_child["name"] = "Temperature (Pressure Sensor)"
    data_child["value"] = hat.get_temperature_from_pressure()
    data_child["unit"] = " °C"
    data["temperature_pressure"] = data_child

    match p:
        case "hpa":
            data_child = {}
            data_child["name"] = "Pressure"

            data_child["value"] = hat.pressure
            data_child["unit"] = " hPa"
            data["pressure"] = data_child
        case "mmhg":
            data_child = {}
            data_child["name"] = "Pressure"

            data_child["value"] = hat.pressure * 0.75006157584566
            data_child["unit"] = " mmHg"
            data["pressure"] = data_child

    match h:
        case "perc":
            data_child = {}
            data_child["name"] = "Humidity"
            data_child["value"] = hat.humidity
            data_child["unit"] = "%"
            data["humidity"] = data_child
        case "norm":
            data_child = {}
            data_child["name"] = "Humidity"
            data_child["value"] = hat.humidity / 100
            data_child["unit"] = ""
            data["humidity"] = data_child

    match ro:
        case "deg":
            roll = hat.get_orientation_degrees()["roll"]
            if roll > 180:
                roll = roll - 360
            data_child = {}
            data_child["name"] = "Roll"
            data_child["value"] = roll
            data_child["unit"] = "°"
            data["roll"] = data_child
        case "rad":
            data_child = {}
            data_child["name"] = "Roll"
            data_child["value"] = hat.get_orientation_radians()["roll"]
            data_child["unit"] = ""
            data["roll"] = data_child

    match pi:
        case "deg":
            pitch = hat.get_orientation_degrees()["pitch"]
            if pitch > 180:
                pitch = pitch - 360
            data_child = {}
            data_child["name"] = "Pitch"
            data_child["value"] = pitch
            data_child["unit"] = "°"
            data["pitch"] = data_child
        case "rad":
            data_child = {}
            data_child["name"] = "Pitch"
            data_child["value"] = hat.get_orientation_radians()["pitch"]
            data_child["unit"] = ""
            data["pitch"] = data_child

    match ya:
        case "deg":
            yaw = hat.get_orientation_degrees()["yaw"]
            if yaw > 180:
                yaw = yaw - 360
            data_child = {}
            data_child["name"] = "Yaw"
            data_child["value"] = yaw
            data_child["unit"] = "°"
            data["yaw"] = data_child
        case "rad":
            data_child = {}
            data_child["name"] = "Yaw"
            data_child["value"] = hat.get_orientation_radians()["yaw"]
            data_child["unit"] = ""
            data["yaw"] = data_child

    # Commented out because it's not working on the emulator
    # data_child = {}
    # data_child["name"] = "Compass"
    # data_child["value"] = hat.get_compass()
    # data_child["unit"] = "°"
    # data["compass"] = data_child

    data_child = {}
    data_child["name"] = "Accelerometer (X)"
    data_child["value"] = hat.get_accelerometer_raw()["x"] * 9.80665
    data_child["unit"] = "m/s²"
    data["accelerometer_x"] = data_child

    data_child = {}
    data_child["name"] = "Accelerometer (Y)"
    data_child["value"] = hat.get_accelerometer_raw()["y"] * 9.80665
    data_child["unit"] = "m/s²"
    data["accelerometer_y"] = data_child

    data_child = {}
    data_child["name"] = "Accelerometer (Z)"
    data_child["value"] = hat.get_accelerometer_raw()["z"] * 9.80665
    data_child["unit"] = "m/s²"
    data["accelerometer_z"] = data_child

    data_child = {}
    data_child["name"] = "Gyroscope (X)"
    data_child["value"] = hat.get_gyroscope_raw()["x"]
    data_child["unit"] = "rad/s"
    data["gyroscope_x"] = data_child

    data_child = {}
    data_child["name"] = "Gyroscope (Y)"
    data_child["value"] = hat.get_gyroscope_raw()["y"]
    data_child["unit"] = "rad/s"
    data["gyroscope_y"] = data_child

    data_child = {}
    data_child["name"] = "Gyroscope (Z)"
    data_child["value"] = hat.get_gyroscope_raw()["z"]
    data_child["unit"] = "rad/s"
    data["gyroscope_z"] = data_child

    data_child = {}
    data_child["name"] = "Magnetometer (X)"
    data_child["value"] = hat.get_compass_raw()["x"]
    data_child["unit"] = "μT"
    data["magnetometer_x"] = data_child

    data_child = {}
    data_child["name"] = "Magnetometer (Y)"
    data_child["value"] = hat.get_compass_raw()["y"]
    data_child["unit"] = "μT"
    data["magnetometer_y"] = data_child

    data_child = {}
    data_child["name"] = "Magnetometer (Z)"
    data_child["value"] = hat.get_compass_raw()["z"]
    data_child["unit"] = "μT"
    data["magnetometer_z"] = data_child

    data_child = {}
    data_child["name"] = "Joystick (H)"
    data_child["value"] = joy_h_count
    data_child["unit"] = "-"
    data["joystick_x"] = data_child

    data_child = {}
    data_child["name"] = "Joystick (V)"
    data_child["value"] = joy_v_count
    data_child["unit"] = "-"
    data["joystick_y"] = data_child

    data_child = {}
    data_child["name"] = "Joystick (C)"
    data_child["value"] = joy_c_count
    data_child["unit"] = "-"
    data["joystick_c"] = data_child

    return data


@app.get("/sensors/temperature")
async def get_temperature(u: Units.Temperature | None = None):
    data = {}
    data["name"] = "Temperature"

    if u == Units.Temperature.fahrenheit:
        data["value"] = hat.temperature * 9 / 5 + 32
        data["unit"] = " F"
    else:
        data["value"] = hat.temperature
        data["unit"] = " °C"

    return data


@app.get("/sensors/pressure")
async def get_pressure(u: Units.Pressure | None = None):
    data = {}
    data["name"] = "Pressure"

    if u == Units.Pressure.mercury:
        data["value"] = hat.pressure * 0.75006157584566
        data["unit"] = " mmHg"
    else:
        data["value"] = hat.pressure
        data["unit"] = " hPa"

    return data


@app.get("/sensors/humidity")
async def get_humidity(u: Units.Humidity | None = None):
    data = {}
    data["name"] = "Humidity"

    if u == Units.Humidity.normalized:
        data["value"] = hat.humidity / 100
        data["unit"] = ""
    else:
        data["value"] = hat.humidity
        data["unit"] = "%"

    return data


@app.get("/sensors/orientation/roll")
async def get_roll(u: Units.Orientation | None = None):
    data = {}
    data["name"] = "Roll"

    if u == Units.Orientation.radians:
        data["value"] = hat.get_orientation_radians()["roll"]
        data["unit"] = ""
    else:
        roll = hat.get_orientation_degrees()["roll"]
        if roll > 180:
            roll = roll - 360
        data["value"] = roll
        data["unit"] = "°"

    return data


@app.get("/sensors/orientation/pitch")
async def get_pitch(u: Units.Orientation | None = None):
    data = {}
    data["name"] = "Pitch"

    if u == Units.Orientation.radians:
        data["value"] = hat.get_orientation_radians()["pitch"]
        data["unit"] = ""
    else:
        pitch = hat.get_orientation_degrees()["pitch"]
        if pitch > 180:
            pitch = pitch - 360
        data["value"] = pitch
        data["unit"] = "°"

    return data


@app.get("/sensors/orientation/yaw")
async def get_yaw(u: Units.Orientation | None = None):
    data = {}
    data["name"] = "Yaw"

    if u == Units.Orientation.radians:
        data["value"] = hat.get_orientation_radians()["yaw"]
        data["unit"] = ""
    else:
        yaw = hat.get_orientation_degrees()["yaw"]
        if yaw > 180:
            yaw = yaw - 360
        data["value"] = yaw
        data["unit"] = "°"

    return data


@app.get("/leds/get/all")
async def get_all_leds_colors():
    return hat.get_pixels()


@app.get("/leds/get/{led}")
async def get_led_color(led: Annotated[int, Path(ge=0, le=63)]):
    (x, y) = led_to_pos(led)
    return hat.get_pixel(x, y)


@app.post("/leds/set/all")
async def set_all_leds_colors(arr: list):
    return hat.set_pixels(arr)


@app.get("/leds/set/{led}")
async def set_led_color(
    led: Annotated[int, Path(ge=0, le=63)],
    hex: str | None = None,
    r: int | None = None,
    g: int | None = None,
    b: int | None = None,
):
    (x, y) = led_to_pos(led)

    if hex:
        (r, g, b) = hex_to_rgb(hex)

    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        return

    return hat.set_pixel(x, y, r, g, b)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
