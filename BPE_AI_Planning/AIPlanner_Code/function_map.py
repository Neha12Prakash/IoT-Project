def increase_temperature(**kwargs):
    print(kwargs)


def decrease_temperature(**kwargs):
    print(kwargs)


def increase_brightness(**kwargs):
    print(kwargs)


def decrease_brigthness(**kwargs):
    print(kwargs)


def display_sunny(**kwargs):
    print(kwargs)


def show_live_feed(**kwargs):
    print(kwargs)


def stop_display(**kwargs):
    print(kwargs)


function_map = {
    "increasetemperature": {
        "function": increase_temperature,
        "args": {"temp": 29, "delta": 4},
    },
    "decreasetemperature": {
        "function": decrease_temperature,
        "args": {"temp": 29, "delta": 4},
    },
    "increasebrightness": {
        "function": increase_brightness,
        "args": {"luminance": 29, "delta": 4},
    },
    "decreasebrightness": {
        "function": decrease_brigthness,
        "args": {"luminance": 29, "delta": 4},
    },
    "displaysunny": {
        "function": display_sunny,
        "args": {"random_int": 54},
    },
    "showlivefeed": {
        "function": show_live_feed,
        "args": {"random_int": 54},
    },
    "stopdisplay": {
        "function": stop_display,
        "args": {"random_int": 54},
    },
}
