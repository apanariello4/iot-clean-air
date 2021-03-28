#include <LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 9, 8, 7, 6);

int gLed = A0;
int yLed = A1;
int rLed = A2;

int pin1_PM25 = 2;
int pin2_PM10 = 3;
unsigned long duration1;
unsigned long duration2;

unsigned long starttime;
unsigned long sampletime_ms = 5000;
unsigned long lowpulseoccupancy1 = 0;
unsigned long lowpulseoccupancy2 = 0;
float ratio1 = 0;
float ratio2 = 0;
float concentration_PM25 = 0;
float concentration_PM10 = 0;
float concentration_ugm3;
int concentration_ugm3_PM10;
int concentration_ugm3_PM25;

//Conversion parameters
const float pi = 3.14159;
const float density = 1.65 * pow(10, 12);
const float K = 3531.5;
const float r = 0.44 * pow(10, -6);
const float vol = (4/3) * pi * pow(r, 3);
const float mass = density * vol;


void setup() {
  
  Serial.begin(9600);
  pinMode(2,INPUT); //PM2.5
  pinMode(3,INPUT); //PM10

  pinMode(gLed,OUTPUT);
  pinMode(yLed,OUTPUT);
  pinMode(rLed,OUTPUT);
  
  starttime = millis();
  lcd.begin(16, 2);

}


void loop() {
  
  duration1 = pulseIn(pin1_PM25, LOW);
  duration2 = pulseIn(pin2_PM10, LOW);
  lowpulseoccupancy1 = lowpulseoccupancy1+duration1;
  lowpulseoccupancy2 = lowpulseoccupancy2+duration2;


  if ((millis() - starttime) > sampletime_ms)
  {
    ratio1 = lowpulseoccupancy1/(sampletime_ms*10.0);  // Integer percentage 0=>100
    concentration_PM25 = 1.1*pow(ratio1,3)-3.8*pow(ratio1,2)+520*ratio1+0.62; // using spec sheet curve

    ratio2 = lowpulseoccupancy2/(sampletime_ms*10.0);  // Integer percentage 0=>100
    concentration_PM10 = 1.1*pow(ratio2,3)-3.8*pow(ratio2,2)+520*ratio2+0.62; // using spec sheet curve

    concentration_ugm3_PM25 = round(convert_pm_from_pcs_to_ugm3(concentration_PM25));
    concentration_ugm3_PM10 = round(convert_pm_from_pcs_to_ugm3(concentration_PM10));
//    Serial.println(concentration_PM25);
//    Serial.println(concentration_ugm3_PM25);
//    Serial.println();
//    Serial.println(concentration_PM10);
//    Serial.println(concentration_ugm3_PM10);
//    Serial.println();


    lcd.setCursor(0, 0);
    lcd.print("PM10 ");
    lcd.print("   ");
    lcd.setCursor(6, 0);
    char str[4]; // enough room for 3 numbers and one NULL character
    snprintf(str, 4, "%3d", concentration_ugm3_PM10); // %3d = 3 digits, right aligned
    lcd.print(str);   

    Serial.write(0xff);
    Serial.write(0x02);
    Serial.write((char)(map(concentration_ugm3_PM25,0,500,0,253)));
    Serial.write((char)(map(concentration_ugm3_PM10,0,500,0,253)));
    Serial.write(0xfe);

    
    if (concentration_ugm3_PM10 < 50) {
      lcd.setCursor (0, 1);
      for (int i = 0; i < 16; ++i)
      {
        lcd.write(' ');
      }
        
      lcd.setCursor(4, 1);
      lcd.print("CLEAN");
      
      digitalWrite(gLed, HIGH);
      digitalWrite(yLed, LOW);
      digitalWrite(rLed, LOW);
    }
   
    if (concentration_ugm3_PM10 > 50 && concentration_ugm3_PM10 < 100) {
      lcd.setCursor (0, 1);
      for (int i = 0; i < 16; ++i)
      {
        lcd.write(' ');
      }
      
      lcd.setCursor(4, 1);
      lcd.print("GOOD");
       
      digitalWrite(gLed, HIGH);
      digitalWrite(yLed, LOW);
      digitalWrite(rLed, LOW);
    }
    
    if (concentration_ugm3_PM10 > 100 && concentration_ugm3_PM10 < 200) {
      lcd.setCursor (0, 1);
      for (int i = 0; i < 16; ++i)
      {
        lcd.write(' ');
      }
        
      lcd.setCursor(4, 1);
      lcd.print("UNHEALTY");
      
      digitalWrite(gLed, LOW);
      digitalWrite(yLed, HIGH);
      digitalWrite(rLed, LOW);
    }
      
    if (concentration_ugm3_PM10 > 200 && concentration_ugm3_PM10 < 300) {
      lcd.setCursor (0, 1);
      for (int i = 0; i < 16; ++i)
      {
        lcd.write(' ');
      }   
       
      lcd.setCursor(4, 1);
      lcd.print("HEAVY");
      
      digitalWrite(gLed, LOW);
      digitalWrite(yLed, LOW);
      digitalWrite(rLed, HIGH);
    }

    if (concentration_ugm3_PM10 > 300) {
      lcd.setCursor (0, 1);
      for (int i = 0; i < 16; ++i)
      {
        lcd.write(' ');
      }
        
      lcd.setCursor(4, 1);
      lcd.print("HAZARD");
      
      digitalWrite(gLed, LOW);
      digitalWrite(yLed, LOW);
      digitalWrite(rLed, HIGH);
    } 

    
    lowpulseoccupancy1 = 0;
    lowpulseoccupancy2 = 0;
    starttime = millis();
  }
}


float convert_pm_from_pcs_to_ugm3(float concentration_pcs){
  concentration_ugm3 = concentration_pcs * K * mass;
  return concentration_ugm3;
}
