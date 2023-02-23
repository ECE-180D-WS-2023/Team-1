/*
  example1-basic

  This example shows the basic settings and functions for retrieving accelerometer
	and gyroscopic data. 
	Please refer to the header file for more possible settings, found here:
	..\SparkFun_6DoF_ISM330DHCX_Arduino_Library\src\sfe_ism330dhcx_defs.h

  Written by Elias Santistevan @ SparkFun Electronics, August 2022

	Product:

		https://www.sparkfun.com/products/19764

  Repository:

		https://github.com/sparkfun/SparkFun_6DoF_ISM330DHCX_Arduino_Library

  SparkFun code, firmware, and software is released under the MIT 
	License	(http://opensource.org/licenses/MIT).
*/

#include <Wire.h>
#include "SparkFun_ISM330DHCX.h"

SparkFun_ISM330DHCX myISM; 

// Structs for X,Y,Z data
sfe_ism_data_t accelData; 
sfe_ism_data_t gyroData; 

#define LED_BLUE 12

void setup(){
    pinMode(LED_BLUE, OUTPUT);
	Wire.begin();

	Serial.begin(115200);

	if( !myISM.begin() ){
		Serial.println("Did not begin.");
		while(1);
	}

	// Reset the device to default settings. This if helpful is you're doing multiple
	// uploads testing different settings. 
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
	myISM.setAccelDataRate(ISM_XL_ODR_104Hz);
	myISM.setAccelFullScale(ISM_4g); 

	// Set the output data rate and precision of the gyroscope
	myISM.setGyroDataRate(ISM_GY_ODR_104Hz);
	myISM.setGyroFullScale(ISM_500dps); 

	// Turn on the accelerometer's filter and apply settings. 
	myISM.setAccelFilterLP2();
	myISM.setAccelSlopeFilter(ISM_LP_ODR_DIV_100);

	// Turn on the gyroscope's filter and apply settings. 
	myISM.setGyroFilterLP1();
	myISM.setGyroLP1Bandwidth(ISM_MEDIUM);


}

bool calibrated = 0;
bool idle = 1;

float temp_x;
float temp_y;
float temp_z;

float gyr_x;
float gyr_y;
float gyr_z;

void loop() {

	// Check if both gyroscope and accelerometer data is available.
	if( myISM.checkStatus() ) {
		myISM.getAccel(&accelData);
		myISM.getGyro(&gyroData);
        if (!calibrated) {
            SERIAL_PORT.println("Calibrating idle movement"); 
            digitalWrite(LED_BLUE, HIGH);
            for (int i = 0; i < 10; i++) {
                delay(1000);
                // Get Max & Min Acceleration
                if (accelData.xData > max_x) {
                    max_x = accelData.xData;
                }
                if (accelData.yData > max_y) {
                    max_y = accelData.yData;
                }
                if (accelData.zData > max_z) {
                    max_z = accelData.zData;
                }
                //Get min
                if (accelData.xData < min_x) {
                    min_x = accelData.xData;
                }
                if (accelData.yData < min_y) {
                    min_y = accelData.yData;
                }
                if (accelData.zData < min_z) {
                    min_z = accelData.zData;
                }
            }
            SERIAL_PORT.println("Idle values:");
            SERIAL_PORT.println( min_x);
            SERIAL_PORT.println( max_x);
            SERIAL_PORT.println( min_y);
            SERIAL_PORT.println( max_y);
            SERIAL_PORT.println( min_z);
            SERIAL_PORT.println( max_z); 
            digitalWrite(LED_BLUE, LOW);
            calibrated = 1; //Set calibration mode to true
        }

        //SERIAL_PORT.println("OUT OF CALIBARTION");
        
        temp_y = accelData.xData;
        temp_z = accelData.yData;
        temp_x = accelData.zData;
        
        gyr_y = gyroData.yData;
        gyr_z = gyroData.zData;
        gyr_x = gyroData.xData;
        
        delay(50);
        myISM.getAccel(&accelData);
		myISM.getGyro(&gyroData);
        float diff_x = accelData.xData - temp_x;
        float diff_y = accelData.yData - temp_y;
        float diff_z = accelData.zData - temp_z;

        float dgyr_x = gyroData.xData - gyr_x;
        float dgyr_y = gyroData.yData - gyr_y;
        float dgyr_z = gyroData.zData - gyr_z;

        //Detect forward movement
        if (accelData.zData < max_z + 100 && accelData.zData > min_z - 100
        && accelData.xData < max_x + 100 && accelData.xData > min_x - 100
        && accelData.yData < max_y + 100 && accelData.yData > min_y - 100) {
            SERIAL_PORT.println("IDLE!");
        }
        else if (abs(diff_x) > 800 && abs(diff_y) < 500 && abs(diff_z) < 500) {
            SERIAL_PORT.println("FORWARD MOVEMENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
        }
        else if (abs(diff_z) > 800 && abs(diff_y) < 500 && abs(diff_x) < 500) {
            SERIAL_PORT.println("UPWARD MOVEMENT********************************");
        }
        else if (abs(dgyr_x) > 100 && abs(dgyr_y) < 50 && abs(dgyr_z) < 50) {
            SERIAL_PORT.println("CIRCULAR MOVEMENTs---------------------------------------");
        }
        //printScaledAGMT(&myICM); // This function takes into account the scale settings from when the measurement was made to calculate the values with units
        //delay(30);
    }
    else
    {
        SERIAL_PORT.println("Waiting for data");
        delay(500);
    }
	//delay(100);
}

