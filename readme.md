# FPV Goggle Vibrator
Ein häufiges Problem bei FPV-Piloten, die mit Analog-Brille fliegen, ist das der Empfang hier und da schlecht ist.
Häufig dann der Fall, wenn man auf den Boden schaut oder in die Luft. Insbesondere dann nicht sehr effektiv, wenn man als Antenne einen Patch-Antenne und eine Clover-Leave verwendet.
Ist die Brille waagerecht, die der Empfang in der Regel am besten. Am aller besten wäre es, man könnte seinen Kopf grundsätzlich Richtung Copter drehen, geht aber eben in der Regel nicht.
Daher ist eine waagerecht Position definitiv besser als auf den Boden zu schauen

## Funktionsweise 
Auf diesem [Video]() wird kurz die Funktion des FVP Goggle Vibrators gezeigt.

Über einen Microcontroller wird ein Gyro-Sensor abgefragt, bewegt sich eine Achse ausserhalb eines definierten Nullpunkts, wird ein kleiner Vibrationsmotor eingeschaltet. Je mehr man außerhalb des Nullpunktes ist, um so kräftiger vibriert es.

Bewegt man sich wieder in die Nullposition, hören die Vibrationen auf

## Technik
* Raspberry PICO-Zero
* MPU6050 (Gyro)
* 0.49" OLED Display für eine Anzeige
* 10k Poti zur Einstellung der Sensibilität
* ON/OFF Schalter
* Spannungsversorgung über die Brille
* StepDown-Wandler auf 5V
* Eingesetzte Firmware : CircuitPython

## Software
Geschrieben in Python. Der Sensor wird ausgelesen und seine Werte werden pro Achse in normalisiert in einen Wertebereich zwischen 0 und 1.0. Je höher der Wert ist umso höher ist die Abweichung des Sensors zur Ausgangslage