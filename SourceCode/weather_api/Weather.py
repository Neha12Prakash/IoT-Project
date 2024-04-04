from pyowm import OWM
import pyowm
from weather_api.logger import logger
from weather_api.weather_exceptions import *
from tqdm import tqdm


class OWMClient:
    def __init__(self, key: str, city: str = None, location: tuple = None) -> None:
        try:
            logger.info("Connecting to OpenWeatherMap API")
            logger.info("https://www.openweathermap.org/")
            for i in tqdm(range(100)):
                pass
            self.__owm = OWM(key)
            logger.info("Connected!")
        except Exception as e:
            logger.error(str(e))
            logger.warning("Please check for the API key Validity")
            raise OWMConnectionError

        if city == None and location == None:
            logger.error("No location found")
            logger.warning("Please enter a valid city or location")
            raise UnknownLocationError

        else:
            self.__city = city
            self.__location = location
        self.__observation = self.__get_observation()

    def __get_observation(self):
        if not (self.__city == None):
            return self.__owm.weather_at_place(str(self.__city))
        loc_lat, loc_long = self.__location
        return self.__owm.weather_at_coords(loc_lat, loc_long)

    def __get_weather(self):
        return self.__observation.get_weather()

    def get_status(self) -> str:
        return self.__get_weather().get_status()

    def get_temperature(self, unit: str = None):
        if unit == None:
            return self.__get_weather().get_temperature()
        return self.__get_weather().get_temperature(unit)

    def get_wind_status(self):
        return self.__get_weather().get_wind()

    def get_humidity(self) -> int:
        return self.__get_weather().get_humidity()
