/**
 * Author  : Celeste Valambhia
 * Module  : DHT11, Limit Switch and LDR interfacing module with ESP32
 * Usecase : Based on Limit Switch state -
 *           - Measure the ambient temperature of the room and control the thermostat accordingly.
 *           - Measure the ambient light and control the lighting of the room.
 */

/*
 * REQUIRES the following Arduino libraries:
 * - DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library
 * - Adafruit Unified Sensor Lib: https://github.com/adafruit/Adafruit_Sensor
 */
#include "DHT.h"
#include <WiFi.h>
#include <PubSubClient.h>

#define BPE_MQTT "bpe/data/location"
#define DELAY 1000

/* PINS */
#define LDRPIN 34
/*
 * Analog pin connected to LDR (Luminance Sensor)
 * Connect pin 1 (on the left) of the sensor to Analog IN
 * Connect pin 2 of the sensor to +3V3
 * Connect pin 3 (on the right) of the sensor to GROUND
 */
#define LED_STRIP_PIN 16
/*
 * PWM pin connected to Led Strip
 */
#define LIMIT_SWITCH_PIN 32
/*
 * Digital pin connected to limit switch
 */
#define DHTPIN 4
/*
 * Digital pin connected to the DHT sensor (Temperature Sensor)
 * ESP8266 note: use pins 3, 4, 5, 12, 13 or 14
 * Connect pin 1 (on the left) of the sensor to +3V3
 * Connect pin 2 of the sensor to whatever your DHTPIN is i.e. 4
 * Connect pin 4 (on the right) of the sensor to GROUND
 * Connect a 10K resistor from pin 2 (data) to pin 1 (power) of the sensor
 */
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE); /*Initializing DHT sensor*/

byte limitSwitchState = 0;  /*Initial switch state*/

/* Setting PWM properties for LED Strip */
const int LS_Freq = 5000;
const int LS_Channel = 0;
const int LS_Resolution = 8;

/* MQTT Details */
const char* ssid = "CV_TP-Link_2BA6";
const char* password = "celestev";
const char* mqtt_server = "52.27.104.32";
const int mqtt_port = 1883;
const char* willTopic = "BPE_Topic";
const char* willMessage = "Check BPE connection!";
byte willQoS = 1;
boolean willRetain = false;
/* Optional */
const char* mqtt_user = "bpe_blues";
const char* mqtt_password = "bpe_blues";

char temp_buf[10] = {'\0'};
char lum_buf[20] = {'\0'};
char hum_buf[20] = {'\0'};

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
	Serial.begin(9600);
	Serial.println(F("Sensors test!"));

	WiFi.begin(ssid, password);
	while (WiFi.status() != WL_CONNECTED) {
		delay(1000);
		Serial.println("Connecting to WiFi..");
	}
	Serial.println("Connected to the WiFi network");

	client.setServer(mqtt_server, mqtt_port);
	mqtt_connect();
	client.publish("esp/test/", "Hello from ESP32");

	/* MQTT Subscribing */
	client.setCallback(callback);
	client.subscribe(BPE_MQTT"/actuator/luminance",1); /*QoS = 1*/

	/* PWM Setup */
	ledcSetup(LS_Channel, LS_Freq, LS_Resolution);
	ledcAttachPin(LED_STRIP_PIN, LS_Channel);  /*Attaching the channel to the GPIO-16*/

	dht.begin();
}

void mqtt_connect() {
	while (!client.connected()) {
		Serial.println("Connecting to MQTT...");
		if (client.connect("Buro_Pro_Enh_Client", willTopic, willQoS, willRetain, willMessage)) {
			Serial.println("connected");
		} else {
			Serial.print("failed with state = ");
			Serial.print(client.state());
		}
	}
}

void callback(char* topic, byte* message, unsigned int length) {
	Serial.print("Message arrived on topic: ");
	Serial.print(topic);
	Serial.print(". Message: ");
	String message_buf;

	for (int i = 0; i < length; i++) {
		Serial.print((char)message[i]);
		message_buf += (char)message[i];
	}
	Serial.println();
	if (String(topic) == BPE_MQTT"/actuator/luminance") {
		/* Setting LED Brightness */
		Serial.print("Setting brightness to - ");
		int PWM_Output = message_buf.toInt();
		Serial.print(PWM_Output);
		ledcWrite(LS_Channel,PWM_Output);
	}
}

void loop() {

	if (!client.connected()) {
		//Serial.print("\n-------------------debug------------------------\n");
		mqtt_connect();
	}
	client.loop();
	delay(DELAY);  /*Wait a few seconds between measurements*/
	Serial.print("\n-------------------------------------------\n");

	/* Reading Temperature */
	float temp_c = dht.readTemperature(); /*In Celsius*/
	float temp_f = dht.readTemperature(true); /*In Fahrenheit*/
	if (isnan(temp_c) || isnan(temp_f)) {
		Serial.println(F("Failed to read from DHT sensor!"));
		return;
	}
	float humidity =  dht.readHumidity(); /*Reading humidity*/

	/* Printing Sensor Values */
	Serial.print(F("Temperature = "));
	Serial.print(temp_c);
	Serial.print(F("°C "));
	Serial.print(temp_f);
	Serial.print(F("°F \nHumidity = "));
	Serial.println(humidity);

	/* Getting ambient luminance */
	int ldr_value = ((100*(4096-analogRead(LDRPIN)))/4096);
	Serial.print(F("Luminance = "));
	Serial.println(ldr_value);

	/* Getting window status */
	byte limitSwitchState = analogRead(LIMIT_SWITCH_PIN);
	if (limitSwitchState){
		Serial.print(F("Window Open\n"));
		client.publish(BPE_MQTT"/sensor/window", "Open");
	} else {
		Serial.print(F("Window Closed\n"));
		client.publish(BPE_MQTT"/sensor/window", "Closed");
	}

	/* MQTT Publishing */
	temp_buf[10] = {'\0'};
	lum_buf[20] = {'\0'};
	hum_buf[20] = {'\0'};

	snprintf (temp_buf, sizeof(temp_buf), "%f", temp_c);
	snprintf (lum_buf, sizeof(lum_buf), "%d", ldr_value);
	snprintf (hum_buf, sizeof(hum_buf), "%f", humidity);

	client.publish("bpe/test/", "Hello from Buro Productivity Enhancer!");
	client.publish(BPE_MQTT"/sensor/temperature", temp_buf);
	client.publish(BPE_MQTT"/sensor/luminance", lum_buf);
	client.publish(BPE_MQTT"/sensor/humidity", hum_buf);
	Serial.print("\n-------------------------------------------\n");
}
