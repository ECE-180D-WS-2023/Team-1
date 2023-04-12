#include <WiFi.h>
#include <PubSubClient.h>
#include "arduino_secrets.h"
#include <Wire.h>
#include "ICM_20948.h" // Click here to get the library: http://librarymanager/All#SparkFun_ICM_20948_IMU
//#define USE_SPI       // Uncomment this to use SPI
#define SERIAL_PORT Serial
#define SPI_PORT SPI // Your desired SPI port.       Used only when "USE_SPI" is defined
#define CS_PIN 2     // Which pin you connect CS to. Used only when "USE_SPI" is defined
#define WIRE_PORT Wire // Your desired Wire port.      Used when "USE_SPI" is not defined
#define AD0_VAL 1

#ifdef USE_SPI
ICM_20948_SPI myICM; // If using SPI create an ICM_20948_SPI object
#else
ICM_20948_I2C myICM; // Otherwise create an ICM_20948_I2C object
#endif

#define LED_BLUE 13 //for calibration indication
#define BUTTON 14 //for button

#define SERIAL_PORT Serial




// WiFi
const char *ssid = SECRET_SSID; // Enter your WiFi name
const char *password = SECRET_PASS;  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "mqtt.eclipseprojects.io";
const char *topic = "ktanna/motion2";
// const char *mqtt_username = "emqx";
// const char *mqtt_password = "public";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);



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
  pinMode(BUTTON, INPUT); // declare button as input
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
 #ifdef USE_SPI
  SPI_PORT.begin();
#else
  WIRE_PORT.begin();
  WIRE_PORT.setClock(400000);
#endif
  //myICM.enableDebugging(); // Uncomment this line to enable helpful debug messages on Serial
  bool initialized = false;
  while (!initialized)
  {
#ifdef USE_SPI
    myICM.begin(CS_PIN, SPI_PORT);
#else
    myICM.begin(WIRE_PORT, AD0_VAL);
#endif
    SERIAL_PORT.print(F("Initialization of the sensor returned: "));
    SERIAL_PORT.println(myICM.statusString());
    if (myICM.status != ICM_20948_Stat_Ok)
    {
      SERIAL_PORT.println("Trying again...");
      delay(500);
    }
    else
    {
      initialized = true;
    }
  }

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
char move = 'x';
char trans_m = 'q';
int play_num = 2;
long int last_time = millis();
long int thresh_send = 600;

int buttonState;            // the current reading from the input pin
int lastButtonState = LOW;  // the previous reading from the input pin

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
unsigned long debounceDelay = 50;    // the debounce time; increase if the output flickers

void loop()
{
  int reading = digitalRead(BUTTON);
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
    // delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;

      // only toggle the LED if the new button state is HIGH
      if (buttonState == HIGH) {
        client.publish(topic, "BUTTON PUSHED");
        Serial.println("BUTTON PUSHED");
      }
    }
  }
  lastButtonState = reading;
  // if (buttonState == HIGH) {
  //   char pause = 'P';
  //   char buf[32];
  //   snprintf(buf, 32, "%c", pause); 
  //   client.publish(topic, buf);
  //   Serial.println("BUTTON PUSHED");
  // }
  // Check if both gyroscope and accelerometer data is available.
  if (myICM.dataReady()){
    myICM.getAGMT(); // The values are only updated when you call 'getAGMT'
    if (!calibrated) {
       SERIAL_PORT.println("Calibrating idle movement"); 
       digitalWrite(LED_BLUE, HIGH);
       for (int i = 0; i < 10; i++)
        {
          delay(1000);
          // Get Max & Min Acceleration
          if (myICM.accX()> max_x) {
            max_x = myICM.accX();
          }
          if (myICM.accY()> max_y) {
            max_y = myICM.accY();
          }
          if (myICM.accZ()> max_z) {
            max_z = myICM.accZ();
          }
          //Get min
          if (myICM.accX()< min_x) {
            min_x = myICM.accX();
          }
          if (myICM.accY()< min_y) {
            min_y = myICM.accY();
          }
          if (myICM.accZ()< min_z) {
            min_z = myICM.accZ();
          }
        }
        SERIAL_PORT.println("Idle values:");
        SERIAL_PORT.println( min_x);
        SERIAL_PORT.println( max_x);
        SERIAL_PORT.println( min_y);
        SERIAL_PORT.println( max_y);
        SERIAL_PORT.println( min_z);
        SERIAL_PORT.println(max_z); 
        digitalWrite(LED_BLUE, LOW);
        calibrated = 1; //Set calibration mode to true
    }

    ay = myICM.accY();
    az = myICM.accZ();
    ax = myICM.accX();
    
    gy = myICM.gyrY();
    gz = myICM.gyrZ();
    gx = myICM.gyrX();

    //SERIAL_PORT.println(ax);

    //SERIAL_PORT.println(ay);
    // SERIAL_PORT.println(az);
    //SERIAL_PORT.println(gx); 
    //SERIAL_PORT.println(gy); 
    //SERIAL_PORT.println(gz); 

    if (az < max_z + 100 && az > min_z - 100
    && ax < max_x + 100 && ax > min_x - 100
    && ay < max_y + 100 && ay > min_y - 100) {
      trans_m = 'q';
    }
    else if (gx > 200 && gy < 200 && gz < 100) {
     Serial.println("r");
      move = 'r';
      trans_m = pubMove(move, trans_m, play_num, last_time);
    }
    else if (ax > 1000 && az < 2000) {
      Serial.println("f");
      move = 'f';
      trans_m = pubMove(move, trans_m, play_num, last_time);
    }
    else if (ay > 1500 && ax < 500 && az < 500) {
      Serial.println("l");
      move = 'l';
      trans_m = pubMove(move, trans_m, play_num, last_time);
    }    
    else if (az > 1800 && ax < 500 && ay < 500) {
      Serial.println("u");
      move = 'u';
      trans_m = pubMove(move, trans_m, play_num, last_time);
    }
    // if (millis() - last_time > thresh_send) {
    //   trans_m = 'q';
    // }
  }
  //move = 'x';
	delay(threshold);
}

//upon registering a motion:
// registered_motion = motion
// if registered_motion != transmitted_motion
  // send regitered_motion
  // transmitted_motion = registered_motion
// /every t time, reset transmitted_motion = ""

char pubMove(char move, char trans_m, int player, long int &last_time) { //returns transmitted motions
  if (move != trans_m) {
    char buf[32];
    snprintf(buf, 32, "p%d,%c", player, move); 
    client.publish(topic, buf);
    last_time = millis();  
    return move; // set equal to trans_m
  }
  return trans_m;
}