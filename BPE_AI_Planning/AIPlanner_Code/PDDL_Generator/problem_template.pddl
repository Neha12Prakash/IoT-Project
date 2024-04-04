(define (problem Change)

	(:domain BPE)

	(:objects
		TemperatureSensor LuminositySensor Camera WeatherAPI WindowStatus - sensor
		Thermostat LightSource Display - actuator
	)

	(:init 
		%%(Thermostat_Exists Thermostat)%% 
		%%(LightSource_Exists LightSource)%% 
		%%(CameraExists Camera)%%

		(%%Brilliance_Dull%% LuminositySensor)
		(%%TemperatureLow_High%% TemperatureSensor)
		(%%GloomyWeather_SunnyWeather%% WeatherAPI)
		(%%WindowClosed_Open%% WindowStatus) 
		%%(TemperatureOptimality)%%
		%%(LuminosityOptimality)%%

	)

	(:goal
		(and (TemperatureSuitable TemperatureSensor)
			(FavourableLighting LuminositySensor)
			(ProficientDisplay Display))
	)
)