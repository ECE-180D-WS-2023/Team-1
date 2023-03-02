#include <WiFi.h>
#include <PubSubClient.h>
#include "arduino_secrets.h"
#include <Wire.h>
#include "SparkFun_ISM330DHCX.h"
#define LED_BLUE 13 //for calibration indication

#define SERIAL_PORT Serial

// WiFi
const char *ssid = SECRET_SSID; // Enter your WiFi name
const char *password = SECRET_PASS;  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "mqtt.eclipseprojects.io";
const char *topic = "ktanna/test";
// const char *mqtt_username = "emqx";
// const char *mqtt_password = "public";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Motion detection vars
SparkFun_ISM330DHCX myISM; 

// Structs for X,Y,Z data
sfe_ism_data_t accelData; 
sfe_ism_data_t gyroData; 

// floats for X, Y, Z data
float ax;
float ay;
float az;
float gx;
float gy;
float gz;
// end motion detection vars

void setup() {
  pinMode(LED_BLUE, OUTPUT); //declare onboard LED output

	Wire.begin();

 // Set software serial baud to 115200;
 Serial.begin(115200);
 // connecting to a WiFi network
 WiFi.begin(ssid, password);
 while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.println("Connecting to WiFi..");
 }
 Serial.println("Connected to the WiFi network");
 //connecting to a mqtt broker
 client.setServer(mqtt_broker, mqtt_port);
 client.setCallback(callback);
 while (!client.connected()) {
     String client_id = "esp32-client-";
     client_id += String(WiFi.macAddress());
     Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());
     if (client.connect(client_id.c_str())) { //, mqtt_username, mqtt_password)) {
         Serial.println("mqtt broker connected");
     } else {
         Serial.print("failed with state ");
         Serial.print(client.state());
         delay(2000);
     }
 }
 // publish and subscribe
 client.publish(topic, "Hi I'm ESP32 ^^");
 client.subscribe(topic);

  if( !myISM.begin() ){
		Serial.println("Did not begin.");
		while(1);
	}
  
	// Reset the device to default settings
	myISM.deviceReset();

	// Wait for it to finish reseting
	while( !myISM.getDeviceReset() ){ 
		delay(1);
	} 

	Serial.println("Reset.");
	Serial.println("Applying settings.");
	delay(100);
	myISM.setDeviceConfig();
	myISM.setBlockDataUpdate();
	
	// Set the output data rate and precision of the accelerometer
	myISM.setAccelDataRate(ISM_XL_ODR_208Hz);
	myISM.setAccelFullScale(ISM_4g); 

	// Set the output data rate and precision of the gyroscope
	myISM.setGyroDataRate(ISM_GY_ODR_208Hz);
	myISM.setGyroFullScale(ISM_500dps); 

	// Turn on the accelerometer's filter and apply settings. 
	myISM.setAccelFilterLP2();
	myISM.setAccelSlopeFilter(ISM_LP_ODR_DIV_100);

	// Turn on the gyroscope's filter and apply settings. 
	myISM.setGyroFilterLP1();
	myISM.setGyroLP1Bandwidth(ISM_MEDIUM);
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++) {
    Serial.print((char) payload[i]);
  }
  Serial.println();
  Serial.println("-----------------------");
}

bool calibrated = 0;

//Accelerometer threshold vals for idle motion
float min_x = 0;
float min_y = 0;
float min_z = 0;
float max_x = 0;
float max_y = 0;
float max_z = 0;
unsigned long threshold = 20;
char move;
int play_num = 1;

void loop()
{
  // Check if both gyroscope and accelerometer data is available.
	if( myISM.checkStatus() ){
    if (!calibrated) {
      Serial.println("Calibrating idle movement"); 
      digitalWrite(LED_BLUE, HIGH);
      for (int i = 0; i < 10; i++) {
        myISM.getAccel(&accelData);
        myISM.getGyro(&gyroData);
        ax = accelData.xData;
        ay = accelData.yData;
        az = accelData.zData;
        delay(500);
        // Get min
        if (ax < min_x) {
          min_x = ax;
        }
        if (ay < min_y) {
          min_y = ay;
        }
        if (az < min_z) {
          min_z = az;
        }
        // Get max
        if (ax > max_x) {
          max_x = ax;
        }
        if (ay > max_y) {
          max_y = ay;
        }
        if (az > max_z) {
          max_z = az;
        }
      }
      Serial.println("Idle values:");
      Serial.println( min_x);
      Serial.println( max_x);
      Serial.println( min_y);
      Serial.println( max_y);
      Serial.println( min_z);
      Serial.println( max_z); 
      digitalWrite(LED_BLUE, LOW);
      calibrated = 1; 
	  }
    myISM.getAccel(&accelData);
		myISM.getGyro(&gyroData);
    ax = accelData.xData;
    ay = accelData.yData;
    az = accelData.zData;
    gx = gyroData.xData;
    gy = gyroData.yData;
    gz = gyroData.zData;
    if (az < max_z + 100 && az > min_z - 100
    && ax < max_x + 100 && ax > min_x - 100
    && ay < max_y + 100 && ay > min_y - 100) {
    }
    else if (gx > 400000 && gy < 350000 && gz < 350000) {
      Serial.println("Rotate ++++++++++++++++++++++");
      move = 'r';
      pubMove(move, play_num);
    }
    else if (ax > 400 && az < 0) {
      Serial.println("Forward ==================");
      move = 'f';
      pubMove(move, play_num);
    }
    else if (ay > 1500 && ax < 500 && az < 500) {
      Serial.println("Left ----------------------");
      move = 'l';
      pubMove(move, play_num);
    }
    else if (az > 900 && ax < 500 && ay < az - 300 && gx < 100000) {
      Serial.println("Up *********************");
      move = 'u';
      pubMove(move, play_num);
    }
  }
	delay(threshold);
}

void pubMove(char move, int player) {
  char buf[32];
  snprintf(buf, 32, "%d%c", player, move); 
  client.publish(topic, buf);
}