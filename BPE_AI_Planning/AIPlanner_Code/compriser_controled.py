from weather_api.Weather import OWMClient
from env.config import OWM_KEY

from AIPlanner.AIPlannerExceptions import CompriserOptimum
from AIPlanner.logger import logger


class Interpret:
    """
    Builds the replacement dictionary from the input values

    *** IF WINDOW OPEN : window_status = True ***
    *** IF WINDOW CLOSED : window_status = False ***

    """

    def __init__(
        self,
        temperature_threshold: tuple,
        luminance_threshold: tuple,
        city: str = "Stuttgart, Germany",
    ) -> None:

        self.owm_client = OWMClient(key=OWM_KEY, city=city)

        # Temperature States :          Uses MQTT
        self.temperature_low = "TemperatureLow"
        self.temperature_high = "TemperatureHigh"

        # Luminance States :            Uses MQTT
        self.luminosity_low = "LuminosityLow"
        self.luminosity_high = "LuminosityHigh"

        # Weather states :              Uses Openweather
        self.sunny_weather = "SunnyWeather"
        self.gloomy_weather = "GloomyWeather"

        # Window states :               Uses MQTT
        self.window_open = "WindowOpen"
        self.window_closed = "WindowClosed"

        # Optimal States :
        self.temperature_optimality = "(TemperatureSuitable TemperatureSensor)"
        self.luminosity_optimality = "(FavourableLighting LuminositySensor)"

        # Thresholds
        self.temperature_threshold = temperature_threshold
        self.luminosity_threshold = luminance_threshold

        # Main Dictions
        self.main_dict = {
            "%%(Thermostat_Exists Thermostat)%%": "(Thermostat_Exists Thermostat)",
            "%%(LightSource_Exists LightSource)%%": "(LightSource_Exists LightSource)",
            "%%(CameraExists Camera)%%": "(CameraExists Camera)",
        }

    def __evaluate_temperature(self, temp_val: float):
        logger.debug(f"Temperature: {temp_val} check for {self.temperature_threshold}")
        if int(temp_val) <= self.temperature_threshold[0]:
            self.main_dict["%%TemperatureLow_High%%"] = self.temperature_low

        elif int(temp_val) >= self.temperature_threshold[1]:
            self.main_dict["%%TemperatureLow_High%%"] = self.temperature_high

    def __evaluate_luminosity(self, luma_val: float):

        logger.debug(f"Luminosity: {luma_val} check for {self.luminosity_threshold}")

        if int(luma_val) <= self.luminosity_threshold[0]:
            self.main_dict["%%Brilliance_Dull%%"] = self.luminosity_low
        elif int(luma_val) >= self.luminosity_threshold[1]:
            self.main_dict["%%Brilliance_Dull%%"] = self.luminosity_high

    def __evaluate_window_status(self, window_stat: bool):
        if window_stat:
            self.main_dict["%%WindowClosed_Open%%"] = self.window_open
        else:
            self.main_dict["%%WindowClosed_Open%%"] = self.window_closed

    def __evaluate_weather(self, weather_string: str):
        gloomy_word_list = ["clouds", "rain", "snow"]
        if weather_string in gloomy_word_list:
            self.main_dict["%%GloomyWeather_SunnyWeather%%"] = self.gloomy_weather
        else:
            self.main_dict["%%GloomyWeather_SunnyWeather%%"] = self.sunny_weather

    def __check_optimality(self, val: float, threshold: tuple) -> bool:
        if (threshold[0] < val) and (val < threshold[1]):
            return True
        return False

    def __throw_optimality_error(self, bool_1: bool, bool_2: bool):
        if bool_1 and bool_2:
            raise CompriserOptimum

    def give_dict(
        self,
        temperature_val: float,
        luminance_val: float,
        window_status: bool,
        weather_string: str,
    ) -> dict:
        temp_optimal = self.__check_optimality(
            val=temperature_val, threshold=self.temperature_threshold
        )
        # Check for temperature optimality
        if not temp_optimal:
            self.__evaluate_temperature(temp_val=temperature_val)

            # try to remove the optimality condition
            try:
                self.main_dict.pop("%%(TemperatureOptimality)%%")
            except Exception as e:
                pass
        else:
            self.main_dict["%%(TemperatureOptimality)%%"] = self.temperature_optimality

        luma_optimal = self.__check_optimality(
            val=luminance_val, threshold=self.luminosity_threshold
        )

        # Check for luminance optimality
        if not luma_optimal:
            self.__evaluate_luminosity(luma_val=luminance_val)
            # try to remove the optimality condition
            try:
                self.main_dict.pop("%%(LuminosityOptimality)%%")
            except Exception as e:
                pass
        else:
            self.main_dict["%%(LuminosityOptimality)%%"] = self.luminosity_optimality

        self.__evaluate_weather(weather_string=weather_string)
        self.__evaluate_window_status(window_stat=window_status)

        return self.main_dict, temp_optimal and luma_optimal
