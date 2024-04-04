(define (domain BPE)

    (:requirements :strips :typing :negative-preconditions

    )

    (:types
        sensor actuator - object
    )

    (:predicates
        (TemperatureHigh ?th - sensor)
        (TemperatureLow ?tl - sensor)
        (TemperatureSuitable ?ts - sensor)
        (Thermostat_Exists ?e - actuator)
        (Thermostat_High ?tth - actuator)
        (Thermostat_Low ?ttl - actuator)

        (LuminosityHigh ?b - sensor)
        (LuminosityLow ?d - sensor)
        (FavourableLighting ?fl - sensor)
        (LightSource_Exists ?le - actuator)
        (LightSource_High ?lh - actuator)
        (LightSource_Low ?ll - actuator)

        (SunnyWeather ?sw - sensor)
        (GloomyWeather ?gw - sensor)
        (WindowClosed ?wc - sensor)
        (WindowOpen ?wo - sensor)
        (CameraOn ?co - sensor)
        (CameraExists ?ce - sensor)
        (ProficientDisplay ?pd - actuator)

    )

    (:action IncreaseTemperature
        :parameters (?tl ?ts - sensor ?e ?tth - actuator)
        :precondition (and (TemperatureLow ?tl)
            (not (TemperatureSuitable ?ts))
            (Thermostat_Exists ?e))
        :effect (and (TemperatureSuitable ?ts)
            (not (TemperatureLow ?tl))
            (Thermostat_High ?tth))
    )

    (:action DecreaseTemperature
        :parameters (?th ?ts - sensor ?e ?ttl - actuator)
        :precondition (and (TemperatureHigh ?th)
            (not (TemperatureSuitable ?ts))
            (Thermostat_Exists ?e))
        :effect (and (TemperatureSuitable ?ts)
            (not (TemperatureHigh ?th))
            (Thermostat_Low ?ttl))
    )

    (:action IncreaseBrightness
        :parameters (?d ?fl - sensor ?le ?lh - actuator)
        :precondition (and (LuminosityLow ?d)
            (not (FavourableLighting ?fl))
            (LightSource_Exists ?le))
        :effect (and (FavourableLighting ?fl)
            (not (LuminosityLow ?d))
            (LightSource_High ?lh))
    )

    (:action DecreaseBrightness
        :parameters (?b ?fl - sensor ?le ?ll - actuator)
        :precondition (and (LuminosityHigh ?b)
            (not (FavourableLighting ?fl))
            (LightSource_Exists ?le))
        :effect (and (FavourableLighting ?fl)
            (not (LuminosityHigh ?b))
            (LightSource_Low ?ll))
    )

    (:action DisplaySunny
        :parameters (?gw ?wc - sensor ?pd - actuator)
        :precondition (and (GloomyWeather ?gw)
            (not (ProficientDisplay ?pd))
            (WindowClosed ?wc))
        :effect (and (ProficientDisplay ?pd)
        )
    )
    (:action ShowLiveFeed
        :parameters (?sw ?wc ?ce ?co - sensor ?pd - actuator)
        :precondition (and (SunnyWeather ?sw)
            (WindowClosed ?wc)
            (CameraExists ?ce))
        :effect (and (CameraOn ?co)
            (ProficientDisplay ?pd))
    )
    (:action StopDisplay
        :parameters (?wo - sensor ?pd - actuator)
        :precondition (WindowOpen ?wo)
        :effect (and (ProficientDisplay ?pd)
        )
    )

)