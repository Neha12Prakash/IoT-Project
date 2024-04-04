(define (problem Change)

	(:domain BPE)

	(:objects
		TemperatureSensor LuminositySensor Camera WeatherAPI WindowStatus - sensor
		Thermostat LightSource Display - actuator
	)

	(:init 
		(Thermostat_Exists Thermostat) 
		(LightSource_Exists LightSource) 
		(CameraExists Camera)

		(LuminosityLow LuminositySensor)
		
		(GloomyWeather WeatherAPI)
		(WindowOpen WindowStatus) 
		(TemperatureSuitable TemperatureSensor)
		

	)

	(:goal
		(and (TemperatureSuitable TemperatureSensor)
			(FavourableLighting LuminositySensor)
			(ProficientDisplay Display))
	)
)