#include "Adafruit_CCS811.h"
#include <Servo.h>
Adafruit_CCS811 ccs;


Servo myservo; // create servo object to control a servo 
int pos = 0; // variable to store the servo position
int state_zero = 0; //window is close (0,0: chiusa; 0,1: apertura; 1,0: chiusura; 1,1: chiusa)
int state_one = 0;
int iFutureState;
int iReceived;
int iState;
int changed = 0;
int changed_0 = 0;
int changed_2 = 0; 
int changed_1 = 0;

unsigned long lasttime,lasttime_servo;


void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600);

  if(!ccs.begin()){
    Serial.println("Failed to start sensor! Please check your wiring.");
  }
  
  myservo.attach(9); // attaches the servo on pin 9 to the servo object
  pos = 90; //dopo la configurazione la posizione si trova a 90°
  
  while(!ccs.available()); //calibrate temperature sensor
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);
  lasttime=millis();
  lasttime_servo=millis();
 
  iState=0;
  
}

void loop() {

 
  // ogni n secondi calcolo il valore di CO2
  if (millis() - lasttime > 4000){
    lasttime = millis();
    
    //se posso vado a calcolare i valori di CO2 interna
    if(ccs.available()){
      if(!ccs.readData()){
        Serial.print("CO2: ");
        Serial.print(ccs.geteCO2());
        Serial.print("ppm, TVOC: ");
        Serial.print(ccs.getTVOC());
  
        //se supero la soglia di CO2 valuto se settare i valori per chiudere la finestra
        if(ccs.geteCO2()>1000){
          //apro la finestra solo se non è già aperta
          if(state_zero!=1 && state_one!=1){
              state_zero=0; 
              state_one=1;
              changed=0; // ho finito di cambiare lo stato e lo comunico al Bridge
           }
        }
        else{
          //chiudo la finestra se non è già chiusa
          if(state_zero!=0 && state_one!=0){
             state_zero=1; 
             state_one=0;
             changed=0; // ho finito di cambiare lo stato e lo comunico al Bridge
          }
        }   
      }
      else{
        Serial.println("ERROR!");
      }
    }
  }
  
  //se mi trovo in questo stato => apro finestra. Non metto cicli for/while "bloccanti" ma permetto al sistema di comunicare con il bridge anche mentre sta aprendo
  //o chiudendo la finestra. L'incremento della finestra ha un ritardo di 15 ms perchè non è verosimile si apra/chiuda in moda istantaneo
  if(state_zero==0 && state_one==1){
         
    if (millis() - lasttime_servo > 15) {
      myservo.write(pos); // modifico la posizione ogni 15ms
      lasttime_servo = millis();   
      pos+=1;
    }  
    
    //setto stato finestra: aperta
    if(pos==270){
      state_zero=1; 
      state_one=1;
      changed=0; // ho finito di cambiare lo stato e lo comunico al Bridge
    }
  }
  
  //se mi trovo in questo stato => chiudo finestra (entro nell'if fino alla fine della transizione
  // così facendo non blocco la ricezione Arduino-Bridge come se fossi in un ciclo for/while)
  if(state_zero==1 && state_one==0){
    // goes from 180 degrees to 0 degrees
    if (millis() - lasttime_servo > 15) {
        myservo.write(pos); // modifico la posizione ogni 15ms
        lasttime_servo = millis();   
        pos-=1;
    }
    
    //setto stato finestra: chiusa
    if(pos==90){
      state_zero=0; 
      state_one=0;
      changed=0; // ho finito di cambiare lo stato e lo comunico al Bridge
    }
  }

  // Scrittura del dato sul Bridge, se lo stato del Bridge non era aggiornato
  //if(changed == 0){
  if(changed==0){  
    // mando lo stato della finestra al Bridge se è stato aggiornato
    Serial.write(0xff);
    Serial.write(0x01);

    if(state_zero == 0 && state_one == 0){
      Serial.write(0x00);
      // incremento uno e azzero gli altri per considerare un invio consecutivo dello stesso valore e non un invio alternato di valori
      // voglio che al Bridge arrivi 0,0,0 per essere sicuro che l'abbia letto e non 0,1,1,0,2,2,0 (tre 0 non consecutivi)
      changed_0++;
      changed_1 = 0;
      changed_2 = 0;
    }
    if(state_zero == 1 && state_one == 1){
      Serial.write(0x01);
       changed_1++;
      changed_0 = 0;
      changed_2 = 0;
    }
    //stato di transizione
    if ((state_zero == 1 && state_one == 0)||(state_zero == 0 && state_one == 1)){ 
      Serial.write(0x02);
      changed_2++;
      changed_0 = 0;
      changed_1 = 0;
    }
    Serial.write(0xfe); //fine del file
    
    // se ho mandato per tre volte consecutive lo stesso valore allora sono sicuro che sia arrivato correttamente (empirico)
    if(changed_0 == 3 || changed_1 == 3 || changed_2 == 3){
         changed_0 = changed_2 = changed_1 = 0;
         changed=1;
      }
  }

  //se ho un dato disponibile sulla seriale lo uso, altrimenti faccio altro
  if (Serial.available()>0)
  { 
    iReceived = Serial.read();

    FSM_ON_OFF(iReceived);
    // default: back to the first state
    iFutureState=0;

    if (iState==0 && iReceived=='O') iFutureState=1;
    if (iState==1 && iReceived=='N') iFutureState=2;
    if (iState==1 && iReceived=='F') iFutureState=3;
    if (iState==3 && iReceived=='F') iFutureState=4;
    if (iState==4 && iReceived=='O') iFutureState=1;
    if (iState==2 && iReceived=='O') iFutureState=1;
    
    // CR and LF always skipped (no transition)
    if (iReceived==10 || iReceived==13) iFutureState=iState;

     // onEnter Actions
    
     if (iFutureState==2 && iState==1){
        //se ho ricevuto il comando dal bridge di aprire la finestra e non è già aperta => apro 
        if(state_zero!=1 && state_one!=1){
          state_zero=0;
          state_one=1;
          // non c'è bisogno di aggiornare changed perchè il Bridge è già al corrente dello stato
        }
     }
     
     //se ho ricevuto il comando dal bridge di chiudere la finestra e non è già chiusa => chiudo
     if (iFutureState==4 && iState==3){
        if(state_zero!=0 && state_one!=0){
          state_zero=1;
          state_one=0;
        }
     }
     
     // state transition
     iState = iFutureState;
   
  }

}
