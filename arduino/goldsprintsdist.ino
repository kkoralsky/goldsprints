const int hall1Pin = 7;
const int hall2Pin = 8;
int hall1,old_hall1,hall2,old_hall2, hall1_dist=0, hall2_dist=0;
bool changed=false;

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
  if(Serial.read()=='C') {
	hall1_dist = 0;
	hall2_dist = 0;
        Serial.print('('+String(hall1_dist, DEC)+" "+String(hall2_dist, DEC)+')');
  }
  hall1 = digitalRead(hall1Pin);
  if (hall1!=old_hall1 && hall1==LOW) {
    digitalWrite(13,HIGH);
    hall1_dist++;
    changed=true;
  } else digitalWrite(13,LOW);
  old_hall1=hall1;

  hall2 = digitalRead(hall2Pin);
  if (hall2!=old_hall2 && hall2==LOW) {
    digitalWrite(13,HIGH);
    hall2_dist++;
    changed=true;
  } else digitalWrite(13, LOW);
  old_hall2=hall2;

  if(changed) {
	Serial.print('('+String(hall1_dist, DEC)+" "+String(hall2_dist, DEC)+')');
	changed=false;
  }
}
