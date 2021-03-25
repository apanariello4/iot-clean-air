
int pin1_PM25 = 2;
int pin2_PM10 = 3;
unsigned long duration1;
unsigned long duration2;

unsigned long starttime;
unsigned long sampletime_ms = 10000;
unsigned long lowpulseoccupancy1 = 0;
unsigned long lowpulseoccupancy2 = 0;
float ratio1 = 0;
float ratio2 = 0;
unsigned long concentration_PM25 = 0;
unsigned long concentration_PM10 = 0;


void setup() {
  
  Serial.begin(9600);
  pinMode(2,INPUT); //PM2.5
  pinMode(3,INPUT); //PM10
  starttime = millis();

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

    int_PM25 = concentration_PM25 * 100;
    int_PM10 = concentration_PM10 * 100;


    Serial.write(0xff);
    Serial.write(0x02);
    Serial.write((char)(map(concentration_PM25,0,80000,0,253)));
    Serial.write((char)(map(concentration_PM10,0,80000,0,253)));
    Serial.write(0xfe);

    lowpulseoccupancy1 = 0;
    lowpulseoccupancy2 = 0;
    starttime = millis();
  }
}