#include <Servo.h>

#define PinEcho 6
#define PinTrigger 7
#define Sound01 8
#define Sound02 9
#define Sound03 10
#define PinMotor 13

Servo motorController;

const int TriggerDistanceDelta = 25; // 9,84 inc
const int TriggerDistance = 100; // 39,37 inch
const int FigureUpTimeOut = 10000;
const int FigureDownTimeOut = 5000;
const int AngleSleep = 174; 
const int AnglePopup = 70; 

unsigned long durationEcho = 0;
int distance = 0, lastTriggeredDistance = 0;


void setup() 
{  
  Serial.begin(9600);

  motorController.attach(PinMotor);
  motorController.write(AngleSleep);

  pinMode(PinTrigger, OUTPUT);
  pinMode(PinEcho, INPUT);
  pinMode(Sound01, OUTPUT);
  pinMode(Sound02, OUTPUT);
  pinMode(Sound03, OUTPUT);
  
  digitalWrite(Sound01,HIGH);
  digitalWrite(Sound02,HIGH);
  digitalWrite(Sound03,HIGH);

  Serial.write("setup done");
}

void loop() 
{
  digitalWrite(PinTrigger, LOW);
  delay(5);
  digitalWrite(PinTrigger, HIGH);
  delay(10);
  digitalWrite(PinTrigger, LOW);

  durationEcho = pulseIn(PinEcho, HIGH);
  distance = 0.03432 * (durationEcho/2); // distance cm

  delay(100);

  // Boundary Check so we do not trigger any time, ONLY if distance was change AND we are outside the offset of previous distance defined by the delta
  if (((lastTriggeredDistance - TriggerDistanceDelta) > distance) || (distance > (lastTriggeredDistance + TriggerDistanceDelta)))
  {
    if (distance < TriggerDistance && distance > 0)
    {
      lastTriggeredDistance = (unsigned long)distance;

      Serial.println("Trigger Prop");

      //////////////////////////////////////////////////////////////////////
      //
      // Trigger Sound
      
      long sound = random(Sound01, Sound03 + 1);
      Serial.println(sound);
      digitalWrite(sound, LOW);
      delay(50);
      digitalWrite(sound, HIGH);

      //////////////////////////////////////////////////////////////////////
      //
      // Trigger Servo of Prop
      
      motorController.write(AnglePopup);
      delay(FigureUpTimeOut);
      for(int angle = AnglePopup; angle < AngleSleep; angle++)
      {
        motorController.write(angle);
        delay(25);
      }
      // Animation Timeout so a pause for the prop
      delay(FigureDownTimeOut);
    }
  }
}







