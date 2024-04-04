(define

(problem Change)

(:domain BPE)

(:objects	TemperatureSensor LuminositySensor Camera WeatherAPI WindowStatus - sensor
		Thermostat LightSource Display - actuator
)

(:init	( TemperatureLow TemperatureSensor) 
(Thermostat_Exists Thermostat)
(LuminosityHigh LuminositySensor)
(LightSource_Exists LightSource)
(GloomyWeather WeatherAPI)
(WindowClosed WindowStatus)
(CameraExists Camera)
)

(:goal	(and (TemperatureSuitable TemperatureSensor) 
 (FavourableLighting LuminositySensor) 
 (ProficientDisplay Display)))
)