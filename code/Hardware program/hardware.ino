#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>

/* ================= WIFI ================= */

const char* ssid = "coreidea";
const char* password = "coreidea";

WebServer server(80);

bool manualMode = false;
String currentCommand = "";

/* ================= NEW AUTO DATA VARIABLES ================= */

String autoMovement = "IDLE";
int currentDistance = 0;
int currentNeckAngle = 90;
int leftObstacleCount = 0;
int rightObstacleCount = 0;

/* ================= SERVO DECLARATION ================= */

Servo joint2;
Servo joint3;
Servo joint4;
Servo joint5;
Servo joint6;
Servo joint7;
Servo joint8;
Servo joint9;
Servo neck_servo;

/* ================= HOME POSITIONS ================= */

int home_joint2 = 120;
int home_joint3 = 15;
int home_joint4 = 60;
int home_joint5 = 165;
int home_joint6 = 100;
int home_joint7 = 15;
int home_joint8 = 70;
int home_joint9 = 165;

#define neck_survoPin 17 
#define trigPin 2
#define echoPin 4

#define THERMISTOR_PIN 34

float R1 = 10000.0;      
float Beta = 3950.0;     
float To = 301.15;       
float Ro = 4300.0;       

float readTemperature() {

  int Vo = analogRead(THERMISTOR_PIN);
  if (Vo <= 0 || Vo >= 4095) return 0;

  float R2 = R1 * (4095.0 / (float)Vo - 1.0);
  float T = 1.0 / ((1.0 / To) + (1.0 / Beta) * log(R2 / Ro));
  T = T - 273.15;

  return T+28;
}

/* ================= WIFI HANDLER ================= */

void handleCommand() {

  if (server.hasArg("move")) {

    String cmd = server.arg("move");

    if (cmd == "MANUAL") {
      manualMode = true;
    }
    else if (cmd == "AUTO") {
      manualMode = false;
    }
    else {
      currentCommand = cmd;
    }
  }

  server.send(200, "text/plain", "OK");
}

/* ================= TEMP API ================= */

void handleTemp() {
  float temperatureC = readTemperature();
  server.send(200, "text/plain", String(temperatureC));
}

/* ================= NEW CAR DATA API ================= */

void handleCar() {

  String mode = manualMode ? "MANUAL" : "AUTO";
  float temperatureC = readTemperature();

  String response = "";
  response += "MODE:" + mode + "\n";
  response += "MOVE:" + autoMovement + "\n";
  response += "DIST:" + String(currentDistance) + "\n";
  response += "NECK:" + String(currentNeckAngle) + "\n";
  response += "LEFT_OBS:" + String(leftObstacleCount) + "\n";
  response += "RIGHT_OBS:" + String(rightObstacleCount) + "\n";
  response += "TEMP:" + String(temperatureC) + "\n";

  server.send(200, "text/plain", response);
}

/* ================= SETUP ================= */

void setup(){

  Serial.begin(115200);
  analogReadResolution(12);

  joint2.attach(25);
  joint3.attach(26);
  joint4.attach(18);
  joint5.attach(5);
  joint6.attach(19);
  joint7.attach(32);
  joint8.attach(33);
  joint9.attach(21);

  neck_servo.attach(neck_survoPin, 500, 2400);
  neck_servo.write(90);

  pinMode(echoPin,INPUT);
  pinMode(trigPin,OUTPUT);

  standhome();

  delay(2000);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connected!");
  Serial.println(WiFi.localIP());

  server.on("/cmd", handleCommand);
  server.on("/temp", handleTemp);
  server.on("/car", handleCar);   // 🔥 NEW ENDPOINT
  server.begin();
}

/* ================= LOOP ================= */

void loop(){

  server.handleClient();

  if (manualMode) {

    if (currentCommand == "F") { autoMovement="FORWARD"; forward(1); }
    else if (currentCommand == "B") { autoMovement="BACKWARD"; backward(1); }
    else if (currentCommand == "L") { autoMovement="LEFT"; leftturn(1); }
    else if (currentCommand == "R") { autoMovement="RIGHT"; rightturn(1); }
    else if (currentCommand == "S") { autoMovement="STOP"; standhome(); }

    return;
  }

  autoMovement = "FORWARD";
  standhome();
  forward(1);

  digitalWrite(trigPin,LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin,HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin,LOW);

  float Dulation = pulseIn(echoPin,HIGH);

  if(Dulation>0){

    int Distance = Dulation*340*100/2/1000000;
    currentDistance = Distance;

    if(Distance < 10){

      int sumright = 0;
      int sumleft = 0;

      int i = 170;

      while(i >= 120){

        neck_servo.write(i);
        currentNeckAngle = i;
        i -= 2;

        digitalWrite(trigPin,LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin,HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin,LOW);

        Dulation = pulseIn(echoPin,HIGH);
        int Distance = Dulation*340*100/2/1000000;

        if(Distance <15){
          sumleft++;
        }
        delay(10);
      }

      i = 10;

      while(i <= 60){

        neck_servo.write(i);
        currentNeckAngle = i;
        i += 2;

        digitalWrite(trigPin,LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin,HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin,LOW);

        Dulation = pulseIn(echoPin,HIGH);
        int Distance = Dulation*340*100/2/1000000;

        if(Distance <15){
          sumright++;
        }
        delay(10);
      }

      leftObstacleCount = sumleft;
      rightObstacleCount = sumright;

      neck_servo.write(90);
      currentNeckAngle = 90;

      if(sumright > sumleft){
        autoMovement="LEFT";
        leftturn(3);
      } else {
        autoMovement="RIGHT";
        rightturn(3);
      }

      if(sumright >= 20){
        autoMovement="BACKWARD";
        backward(3);
        leftturn(3);
      }
      else if(sumleft >= 20){
        autoMovement="BACKWARD";
        backward(3);
        rightturn(3);
      }
    }
  }

  delay(10);
}
/* ================= MOVEMENT FUNCTIONS ================= */

void idle(){
  delay(100);
}

void standhome(){
  joint2.write(home_joint2);
  joint3.write(home_joint3);
  joint4.write(home_joint4);
  joint5.write(home_joint5);
  joint6.write(home_joint6);
  joint7.write(home_joint7);
  joint8.write(home_joint8);
  joint9.write(home_joint9);
}

void forward(unsigned int step){
  while (step-- > 0){
    joint3.write(home_joint3+30);
    joint7.write(home_joint7+30);
    delay(100);
    joint2.write(home_joint2+30);
    joint8.write(home_joint8-30);
    delay(100);
    joint3.write(home_joint3);
    joint7.write(home_joint7);

    joint5.write(home_joint5-30);
    joint9.write(home_joint9-30);
    delay(100);
    joint2.write(home_joint2);
    joint8.write(home_joint8);
    joint4.write(home_joint4-30);
    joint6.write(home_joint6+30);
    delay(100);
    joint5.write(home_joint5);
    joint9.write(home_joint9);
  }
}

void backward(unsigned int step){
  while (step-- > 0){
    joint3.write(home_joint3+30);
    joint7.write(home_joint7+30);
    delay(100);
    joint2.write(home_joint2);
    joint8.write(home_joint8);
    joint4.write(home_joint4-30);
    joint6.write(home_joint6+30);
    delay(100);
    joint3.write(home_joint3);
    joint7.write(home_joint7);

    joint5.write(home_joint5-30);
    joint9.write(home_joint9-30);
    delay(100);
    joint2.write(home_joint2+30);
    joint8.write(home_joint8-30);
    delay(100);
    joint5.write(home_joint5);
    joint9.write(home_joint9);
  }
}

void leftturn(unsigned int step){
  neck_rightrotate();
  while (step-- > 0){
    joint5.write(home_joint5-30);
    joint9.write(home_joint9-30);
    delay(100);
    joint2.write(home_joint2+30);
    joint8.write(home_joint8-30);
    joint4.write(home_joint4-30);
    joint6.write(home_joint6+30);
    delay(100);
    joint5.write(home_joint5);
    joint9.write(home_joint9);
    idle();

    joint3.write(home_joint3+30);
    joint7.write(home_joint7+30);
    delay(100);
    joint2.write(home_joint2);
    joint8.write(home_joint8);
    joint4.write(home_joint4);
    joint6.write(home_joint6);
    delay(100);
    joint3.write(home_joint3);
    joint7.write(home_joint7);
    idle();
  }
  neck_home();
}

void rightturn(unsigned int step){
  neck_leftrotate();
  while (step-- > 0){
    joint3.write(home_joint3+30);
    joint7.write(home_joint7+30);
    delay(100);
    joint2.write(home_joint2+30);
    joint8.write(home_joint8-30);
    joint4.write(home_joint4-30);
    joint6.write(home_joint6+30);
    delay(100);
    joint3.write(home_joint3);
    joint7.write(home_joint7);
    idle();

    joint5.write(home_joint5-30);
    joint9.write(home_joint9-30);
    delay(100);
    joint2.write(home_joint2);
    joint8.write(home_joint8);
    joint4.write(home_joint4);
    joint6.write(home_joint6);
    delay(100);
    joint5.write(home_joint5);
    joint9.write(home_joint9);
    idle();
  }
  neck_home();
}

void neck_leftrotate(){
  int i=90;
  while(i < 150){
    neck_servo.write(i);
    i++;
    delay(5);
  }
}

void neck_rightrotate(){
  int i=90;
  while(i > 30){
    neck_servo.write(i);
    i--;
    delay(5);
  }
}

void neck_home(){
  neck_servo.write(90);
}