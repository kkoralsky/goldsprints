const int hall1Pin = 7;
const int hall2Pin = 8;
int hall1,old_hall1,hall2,old_hall2;

void setup() {
  Serial.begin(115200);
  pinMode(hall1Pin, INPUT);
  pinMode(hall2Pin, INPUT);
  digitalWrite(hall1Pin, HIGH);
  digitalWrite(hall2Pin, HIGH);

  //pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
  
}

void loop() {
  
  hall1 = digitalRead(hall1Pin);
  if (hall1!=old_hall1 && hall1==LOW) {
    digitalWrite(13,HIGH);
    Serial.write('0');
  } else digitalWrite(13,LOW);
  old_hall1=hall1;

  hall2 = digitalRead(hall2Pin);
  if (hall2!=old_hall2 && hall2==LOW) {
    digitalWrite(13,HIGH);
    Serial.write('1');
  } else digitalWrite(13, LOW);
  old_hall2=hall2;
}
