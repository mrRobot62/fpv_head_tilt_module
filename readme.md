# FPV Goggle - Head tilt warning module (Vibrator)
Ein häufiges Problem bei FPV-Piloten, die mit Analog-Brille fliegen, ist das der Empfang hier und da schlecht ist.
Häufig dann der Fall, wenn man auf den Boden schaut oder in die Luft. Insbesondere dann nicht sehr effektiv, wenn man als Antenne einen Patch-Antenne und eine Clover-Leave verwendet.
Ist die Brille waagerecht, die der Empfang in der Regel am besten. Am aller besten wäre es, man könnte seinen Kopf grundsätzlich Richtung Copter drehen, geht aber eben in der Regel nicht.
Daher ist eine waagerecht Position definitiv besser als auf den Boden zu schauen

## Funktionsweise 
Auf diesem [Video](https://youtu.be/1WZ-5cJUQDE) wird kurz die Funktion des FVP Goggle Vibrators gezeigt.

Über einen Microcontroller wird ein Gyro-Sensor abgefragt, bewegt sich eine Achse ausserhalb eines definierten Nullpunkts, wird ein kleiner Vibrationsmotor eingeschaltet. Je mehr man außerhalb des Nullpunktes ist, um so kräftiger vibriert es.

Bewegt man sich wieder in die Nullposition, hören die Vibrationen auf

## Technik
* [RP2040 ZERO](https://www.waveshare.com/rp2040-zero.htm) based on Raspberry PICO (Alternativ kann auch ein Raspberry PICO eingesetzt werden). Der RP2040 Zero ist von Waveshare

<img width="165" alt="pico_zero_frei" src="https://user-images.githubusercontent.com/949032/194769770-72424601-ffb1-4bca-a6e1-eeb169fcb0a9.png">

* [MPU6050](https://www.amazon.de/ARCELI-Beschleunigungsmesser-Gyroskop-Beschleunigungssensor-Datenausgang/dp/B07BVXN2GP/ref=sr_1_3?keywords=mpu6050&qid=1665312544&qu=eyJxc2MiOiIzLjYzIiwicXNhIjoiMy4zMCIsInFzcCI6IjMuMTcifQ%3D%3D&sr=8-3) (Gyro)

![MPU6050](https://user-images.githubusercontent.com/949032/194769779-df939d6f-498f-4515-9833-05c638b296f3.jpg)

* [0.49" OLED Display I2C](https://www.ebay.de/itm/274101897584?chn=ps&_trkparms=ispr%3D1&amdata=enc%3A1eqin1ldXRbulkwwG6EjTDA92&norover=1&mkevt=1&mkrid=707-134425-41852-0&mkcid=2&mkscid=101&itemid=274101897584&targetid=1716911581439&device=c&mktype=pla&googleloc=9043417&poi=&campaignid=17943303986&mkgroupid=140642150118&rlsatarget=pla-1716911581439&abcId=9301060&merchantid=112143330&gclid=Cj0KCQjw4omaBhDqARIsADXULuVNMtXGmQVQi-vVaXVg5F0MubSr5O0EkHdSjAeiGJy8hpLhxXdTruoaArmoEALw_wcB) mit einem SSD1306 Chipset für eine Anzeige

![oled_ssd1306](https://user-images.githubusercontent.com/949032/194769789-19d6cde1-6f5a-4627-b89d-366d06c360b5.jpg)

* 4.7k - 10k Poti zur Einstellung der Sensibilität
* 2N3904 NPN-Transistor zur Ansteuerung des Motors
* 1N4007 Freilaufdiode
* Taster für Kalibration
* ON/OFF Schalter
* Spannungsversorgung über die Brille
* [StepDown-Wandler auf 5V - AMS1117, 5V](https://eckstein-shop.de/miniAMS1117-55VDC-DCStep-DownSpannungsreglerVoltageRegulatorConvertor)
![AMS1117](https://user-images.githubusercontent.com/949032/194769795-37d84487-62e2-44bf-823d-29b3abf44d24.jpg)

* Eingesetzte Firmware : [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/what-is-circuitpython)

# Installation
## MicroPython vs CircuitPython
Ich hab mich für CircuitPython entschieden, da es von der Handhabung aus meiner Sicht einfacher ist, abgesehen davon habe ich viele Libraries von Adafruit eingesetzt - und das hat mir das Leben einfacher gemacht. Ansonsten läßt sich das Ganze sicherlich auch unter MicroPython implementieren, man muss halt schauen, wie kompatibel die Libraries sind .

## Circuit-Python installieren
Detaillierte Beschreibung zur Installation von CircuitPython findet ihr auf den Seiten von [Adafruit](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython). Die Installation auf einem Zero ist exakt das gleiche Vorgehen.

> Die Software wurde **nicht** unter Micropython getestet und wird vermutlich ohne Anpassungen nicht lauffähig sein 
## KISS-I - Keep it super simple installation ;-)
Der einfachste Weg ist nachdem Circuitpython installiert wurde und der PICO lauffähig ist. Verbindet den PICO via USB mit Eurem Computer. Es sollt nun im Explorer ein neues Device erscheinen "CIRCUITPYTN". letztendlich verhält sich der Pico jetzt wie ein USB-Stick. Schiebt einfach den kompletten Ordner ins Hauptverzeichnis auf dem PICO. Wartet bis alles einwandfrei übertragen wurde. Kontrolliert zur Sicherheit ob die `code.py` auch im Root-Verzeichnis gelandet ist. Es sollte dann so aussehen:

PICO von USB trennen - und neu verbinden. Circuitpython sollte nun nach dem booten automatisch die `code.py` Datei starten und ihr solltet auf dem Display drei horizontale Balken sehen und die Kalibration wird direkt beginnen.

Hört ihr ein kurzes Brummen des Motors, sieht man was auf dem Display - dann ist der FPV-Goggle-Vibrator einsatzbereit.

## MU-Editor vs Thonny vs VSCode
Geschmacksache, Adafruit favorisiert MU-Editor ich persönlich bevorzuge den Thonny-Editor obwohl ich absoluter Fan von VSCode bin. Wer VS-Code am laufen hat und dort schon mit CircuitPython arbeiten kann - Prima - dann das verwenden.

Für jemanden, der weder das eine noch das Andere kennt, dem empfehle ich [Thonny](https://thonny.org) 

Hier eine deutsche Beschreibung von [AZ-Delivery zum Thema Thonny & Circuit-Python](https://www.az-delivery.de/blogs/azdelivery-blog-fur-arduino-und-raspberry-pi/raspberry-pi-pico-und-thonny-mit-micropython-teil-1)

# DeepDive
Für die wenigen die sich mehr für die Software/Hardware interessieren, nachfolgen ein paar Erläuterungen. Ansonsten ist der Source-Code recht gut mit Kommentaren versehen und Erweiterungen sollten somit kein Problem sein.

## Software
Geschrieben in Python. Im ersten Schritt wird der Gyro-Sensor kalibriert. Die aktuelle (gewünschte) Lage der Brille wird als Nullpunkt (dies soll die Position der Brille sein, während des Fluges) definiert. Der Sensor liefert sowohl negative als auch positive Werte. Für unser System benötigen wir nicht die Information ob es sich um einen positiven oder negativen Wert handelt. Daher werden alle Werte als positive Werte (absolute Werte) verarbeitet. Anschließend wird der gemessene Wert von 0.0 abgezogen, die Differenz ist ein Offset der grundsätzlich später zum  gemessenen Wert addiert wird. Zusätzlich wird der Sensorwert in einen Wertebereich von 0.0 bis 1.0 konvertiert. Je höher der Wert desto weiter ist die Brille vom Nullpunkt entfernt.

Um die Sensitivität der Brille zu verringern/vergrößern, wird der Wert des Potentiometers kontinuierlich gemessen und ebenfalls in einen Wertebereich zwischen 0.0 bis 1.0 umgerechnet und mit einem Faktor multipliziert und anschließend mit dem Gyro-Wert verrechnet. Je höher der Analogwert des Potentiometers umso weniger sensibel reagiert das System. 

Eine Normierung von Werten in einen einheitlichen Wertebereich (hier 0.0 bis 1.0) hat den großen Vorteil, das alle Eingangssignale (Gyro & Poti) anschließend gleich behandelt werden können. Da es sich hier um keine zeitkritische Anwendung handelt sind die wenigen Millisekunden für dieses mapping auch irrelevant.

Die Ausgabe auf dem Display ist lediglich eine Visualisierung der drei Achsenwerte. Der Balken mit dem höchsten Ausschlag, wird zusätzlich noch mit einem kleinen Punkt symbolisiert.

## Kalibration
Die Kalibration des Systems wird grundsätzlich beim Start des Systems durchgeführt. Der User kann durch drücken des Tasters (ca. 1sek) manuell eine Kalibration starten

Die Kalibration besteht aus zwei Teilen und beginnt mit einer kurzen Vibration.
### MPU6050 kalibrieren 
Auf dem Display wird "**CALIBRATION**" angezeigt. In einer Schleife werden mehrere Messungen des Gyro-Sensors über alle Achsen getrennt aufaddiert. Anschließend wird der Durchschnitt pro Achse berechnet.
### Analog-Port Kalibrieren (Damping)
Anlogports und Potentiometer haben in der Regel immer eine kleine Fluktuation der des gemessen Wertes. Mit der Kalibration soll ein Durchschnittlicher Wert ermittelt werden. Die Kalibration wird als "**DAMPING**" im Display angezeigt. Auch hier werden in einer Schleife die Werte aufaddiert und anschließend der Durchschnitt berechnet.

Die Kalibration wird mit zwei kurzen Vibrationen beendet.

## Elektronik
Im Prototyp wurde die Elektronik auf einer Lochrasterplatine aufgebaut. Eine geätzte Platine existiert derzeit nicht. Die Bauteile sind huckepack auf beiden Seiten der Lochrasterplatine platziert.
Der Schaltplan ist super simpel und bedarf nur wenig Löterfahrung. Einzig die Platzierung der Bauteile im beengten Raum ist ein wenig tricky und muss entsprechend auf die jeweilige Brille angepasst werden.
### Schaltplan
[circuit_v0.1.pdf](https://github.com/mrRobot62/fpv_head_tilt_module/files/9742140/circuit_v0.1.pdf)

### Bauteile
1. **RP2040-PICO Zero (von Waveshare)** (wenn man den Vibrator wie auf dem Bild) direkt in die Brille integrieren möchte. Alternative für ist eine flaches Gehäuse irgendwo auf der Brille anzubringen. Hier kann dann auch ein Raspberry PICO verwendet werden. **BEACHTEN** bei der Verwendung eines Raspberry PICO (große Platine) muss in der Software der Motor-PIN von A3 auf A1 umgestellt werden und entsprechend muss der Motor-Pin (zb. Pin zur Basis des Transistors) auf A1 verlötet werden. [Waveshare RP2040-Zero](https://www.waveshare.com/wiki/RP2040-Zero).
2. **Motor** Als Motor wird ein Micro-Vibrationsmotor verwendet, hier muss man im Internet suchen und ggf. das Gehäuse anpassen. Der Motor wird über einen NPN 2S3904 Transistor angesteuert. Um genügend Anlaufstrom zu erhalten ist ein Widerstand von 220Ohm zwischen Basis und dem Analog-Port geschaltet. Hier muss ggf experimentiert werden ob diese Größe für einen Motor auch funktioniert. Die Größe des Widerstands sollt minimal bei ca. 150Ohm liegen und nicht über 470Ohm gehen. Wichtig der Motor muss mit einer Freilaufdiode versehen werden (siehe Schaltplan)
3. **MPU6050** Dieser günstige Gyro-Sensor gibt es schon fertig montiert auf kleinen Platinen. Angeschlossen wird er über I2C (SDA/SCL) und 5V (VCC) und Masse (GND). Alle anderen Pins werden nicht benötigt.
4. **OLED 0.49" Display**. Eingesetzt werden muss ein Display mit einem SSD1306 Chipsatz ansonsten muss die FW angepasst werden. Das Display ist ebenfalls über I2C verbunden und hat schon auf der Platine zwei Pull-Up Widerstände. **Wichtig** hat ein Display keine Pull-Up Widerstände müssen zwei Pullups (1k) zusätzlich eingebaut werden !
5. **Taster** hier kann letztendlich jeder Mini-Taster verwendet werden, Hauptsache er passt ins Gehäuse. Der Taster wird zwischen 5V (VCC) und einem DigitalIOPin am Pico angeschlossen 
6. **Potentiometer** Über den Analogport (A2) wird das Poti angeschlossen. Hier sollte man ein Poti zwischen 4.7k und 10k verwendet. Circuitpython verarbeitet eine Signal und gibt einen Wertebereich zwischen 0 und 65520 zurück. Das Poti wird mit 5V, GND und Schleiferausgang (A2) am Pico angeschlossen.
7. **DropDown Regulator** Eine Fatshark hat im Expansion-Slot einen Stecker der die Lipo-Spannung zur Verfügung stellt (> 5V). Diese Spannung muss auf 5V geregelt werden, sonst brennt der PICO ab. Der Regulator hat drei Pins: VIN (6-9V), VOUT (5V), GND
8. **ON/OFF Schalter** Dieser Schalter sitzt vor dem DropDown-Regler und schaltet diesen über VIN an oder aus. Somit wird auch kein Strom zusätzlich verbraucht, wenn der Vibrator komplett ausgeschaltet wird
