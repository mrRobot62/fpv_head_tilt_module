# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import sys
import pwmio
import random


import displayio
import adafruit_ssd1306
import adafruit_displayio_ssd1306
from adafruit_display_text import label

import terminalio
import fontio
from adafruit_display_text import label, bitmap_label

import digitalio
import adafruit_mpu6050
from adafruit_simplemath import map_range, constrain
from adafruit_debouncer import Debouncer
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.roundrect import RoundRect
from analogio import AnalogIn

from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)

DEBUG_LEVEL = 1	# 0 - 2(verbose)
USE_MPU = 1	# nur für Testzwecke, im produktiven immer 1, 0=ignoriert MPU
TEST_MOTOR = 0

#------------------------------------------------------------------------
# Anlauf PWM-Wert für Vibrationsmotor
#------------------------------------------------------------------------
# DutyCycle (PWM) liegt zwischen 0 und 65535
# der Motor benötigt den MIN-Value als Mindest-DC
# Je nach Motor muss die 30000 angepasst werden
MOTOR_DC = (30000, 65535)
#------------------------------------------------------------------------


#------------------------------------------------------------------------
# Empfindlichkeit des Systems
#------------------------------------------------------------------------
#
# je höher der Wert, desto unempfindler ist der Sensor
# 
DAMPING_FACTOR = 5
LAST_DAMPING_FACTOR = 1.0

MIN_DSF = 1.0
MAX_DSF = 5.0
MIN_POTI = 5000
MAX_POTI = 65520
MAX_ANALOG = 65520

# alle Werte die < dem NULL_POINT liegen werden auf 0.0 gesetzt
#
# letztendlich wird dieser Wert mit dem DAMPING_FACTOR multipliziert und ergeben den tatsächlichen Nullpunkt
# diesen Wert ist für einen MPU6050 das Minimum
NULL_POINT = 0.075
#------------------------------------------------------------------------


#------------------------------------------------------------------------
# Min-Max Werte des MPU-6050 Sensors
# Beim Einsatz eines anderen Sensors, müssen ggf. diese Werte angepasst werden
#------------------------------------------------------------------------
#
# Wertebereich des MPU-Sensors
#			(min, max)
VALUES_X = (0, 10.5)
VALUES_Y = (0, 10.5)
VALUES_Z = (0, 10.5)
#------------------------------------------------------------------------

SCL = board.GP1
SDA = board.GP0

ADR_DISP = 0x3C
ADR_MPU  = 0x68

PIN_BTN	 = board.GP2
PIN_MTR = board.A3
PIN_POT = board.A2

#
# OLED
OLED_W = 96	# das 0.49" Display hat aber nur 64x32 Pixel, warum auch immer die Library funktioniert mit diesem China-Ding nur mit dieser Einstellung
OLED_H = 64
OLED_H2 = int(32/2)
OLED_W2 = int(64/2)

BAR_W = OLED_W2
BAR_W = 48	# Progressbar nur 3/4 des Screens, da noch ein Punkt dargestellt werden soll
BAR_H = 8

#
# sehr seltsam, das ich bei dem 0.49 Display mit diesen Offsets arbeiten muss
# x0y0 wird irgendwie nicht angezeigt
OFF_X = 0	# siehe oben, China-SSD1306 Implementierung :-(
OFF_Y = 0	# siehe oben, China-SSD1306 Implementierung :-(

CIRCLE_R = 4 # Durchmesser für Punkt des höchsten Wertes recht neben der PBar
BARS_XYZ = {
    #     [x, y, w, h]
    "x" : [0+OFF_X,0+OFF_Y,BAR_W,BAR_H],
    "y" : [0+OFF_X,12+OFF_Y,BAR_W,BAR_H],
    "z" : [0+OFF_X,24+OFF_Y,BAR_W,BAR_H],
}


#
# Vereinheitlichung alle Werte auf einen Wertebereich von 0.0 bis 1.0
MAP_X_Y_Z = (0.0, 1.0)
#
# Anzahl der Messungen während der Kalibrierung
CAL_AVG = 10

# Array für Korrekturwerte nach einer Kalbrierung.
# das System versucht in der gewünschten Ausrichtung der Brille, die Werte immer auf 0.0 zu bekommen.
#
xyz_offset = [0,0,0]


oled = None
mpu = None

# Gibt alle Displays frei und den I2C Bus
# muss vor einer I2C Init Sequenz stehen
displayio.release_displays()

#
# I2C bus init
try:
    i2c = busio.I2C(SCL, SDA)
except Exception as err:
    print ("I2C not initialized");
    sys.exit(1)

# für alle Achsen gibt eine Progress-Bar - je mehr der Balken ausgefüllt wird umso mehr ist die Brille ausserhalb ihrer Soll-Position
# 
xb_left = HorizontalProgressBar(
        (BARS_XYZ["x"][0],BARS_XYZ["x"][1]),	# x,y
        (BARS_XYZ["x"][2],BARS_XYZ["x"][3]),	# w,h
        min_value = MAP_X_Y_Z[0],				# 0.0
        max_value = MAP_X_Y_Z[1],        		# 1.0
        direction=HorizontalFillDirection.LEFT_TO_RIGHT
    )

yb_left = HorizontalProgressBar(
        (BARS_XYZ["y"][0],BARS_XYZ["y"][1]),
        (BARS_XYZ["y"][2],BARS_XYZ["y"][3]),
        min_value = MAP_X_Y_Z[0],
        max_value = MAP_X_Y_Z[1],        
        direction=HorizontalFillDirection.LEFT_TO_RIGHT
    )

zb_left = HorizontalProgressBar(
        (BARS_XYZ["z"][0],BARS_XYZ["z"][1]),
        (BARS_XYZ["z"][2],BARS_XYZ["z"][3]),
        min_value = MAP_X_Y_Z[0],
        max_value = MAP_X_Y_Z[1],        
        direction=HorizontalFillDirection.LEFT_TO_RIGHT
    )

#
# Display initialisieren

dbus = displayio.I2CDisplay(i2c_bus=i2c, device_address=ADR_DISP)
display = adafruit_displayio_ssd1306.SSD1306(dbus, width=OLED_W, height=OLED_H, rotation=180)
splash = displayio.Group()
display.show(splash)
color_bitmap = displayio.Bitmap(OLED_W+32, OLED_H+32, 1)
color_palette = displayio.Palette(2)
color_palette[0] = 0x000000  # BLACK
color_palette[1] = 0xFFFFFF  # White

main_group = displayio.Group()

background = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(background)

#
# nun die Progressbars in die Gruppe hinzufügen
main_group.append(xb_left)
main_group.append(yb_left)
main_group.append(zb_left)

#
# ein kleiner Punkt wird rechts am PBar für die aktuelle Achse mit dem höchsten Wert angezeigt
cx = Circle(
    BARS_XYZ["x"][0]+BAR_W+6,			# x
    BARS_XYZ["x"][1]+2,					# y
    CIRCLE_R, fill=color_palette[0])	# r, color
cy = Circle(
    BARS_XYZ["y"][0]+BAR_W+6,
    BARS_XYZ["y"][1]+2,
    CIRCLE_R, fill=color_palette[0])
cz = Circle(
    BARS_XYZ["z"][0]+BAR_W+6,
    BARS_XYZ["z"][1]+2,
    CIRCLE_R, fill=color_palette[0])
main_group.append(cx)
main_group.append(cy)
main_group.append(cz)



display.show(main_group)

#
# MPU initialisieren
if USE_MPU:
    try:
        sensor = adafruit_mpu6050.MPU6050(i2c,address=ADR_MPU)
        sensor.accelerometer_range = adafruit_mpu6050.Range.RANGE_2_G
        sensor.gyro_range = adafruit_mpu6050.GyroRange.RANGE_250_DPS
    except Exception as err:
        print ("MPU not intitalizeid")
        sys.exit(1)
else:
    sensor=None

# Kalibration-Button initialisieren
pin = digitalio.DigitalInOut(PIN_BTN)
pin.switch_to_input(pull=digitalio.Pull.DOWN)
btn = Debouncer(pin, interval=0.01	)

#
# PWM für Motor initialisieren
motor = pwmio.PWMOut(PIN_MTR, duty_cycle=0, frequency=5000)

#
# POTI für DAMPING_FACTOR aktivieren
poti  = AnalogIn(PIN_POT)  

def showDampingLine():
    global LAST_DAMPING_FACTOR
    #
    # Zeige Threshold-Linie und zwar am gewünschten Null-Punkt
    if DAMPING_FACTOR == LAST_DAMPING_FACTOR:
        return
    
    LAST_DAMPING_FACTOR = DAMPING_FACTOR
    main_group.pop()
    np = NULL_POINT * DAMPING_FACTOR
    x = int(map_range(np,0.0,1.0,1,BAR_W))
    y = 0 + OFF_Y
    #print (np,[x,y])
    x+= OFF_X
    line = Line(x,y,x,y+OLED_H, color_palette[1])
    main_group.append(line)
    
def get_DutyCycle(sensor_value):
    """
    Kalkuliert basieren auf den sensor_value einen DutyCycle für den Vibrationsmotor
    Gibt den duty_cycle zurück. Der Wert liegt zwischen MOTOR_DC[0] und MOTOR_DC[1]
    
    Der sensor_value liegt zwischen 0.0 und 1.0. Die Routine generiert daraus ein Mapping
    zwischen (min)..65535
    """
    dc = map_range(sensor_value, MAP_X_Y_Z[0], MAP_X_Y_Z[1], MOTOR_DC[0], MOTOR_DC[1]) 
    return dc

def motorON(motor, dc, ms=0.0):
    """
    Schaltet den Motor für ms Millisekunden ein. anschließend wird der duty_cycle auf 0 gesetzt
    
    Beachten:
    das hier ist blockierend ! Heißt, wenn der Motor mit einem Timeout läuft, geht nichts anderes mehr !
    Das System wartet soviele Millisekunden
    
    Args:
    dc - duty-Cycle Werte für PWM zwischen 0..65535
    ms - default 0.0 ms - oder übergebener Wert. Blockierend!
    """
    motor.duty_cycle = dc
    if ms > 0.0:
        time.sleep(ms/1000.0)
        motorOFF(motor,0)
    
    
def motorOFF(motor,ms=100):
    """ MotorOFF, blockierend für 100ms """
    motor.duty_cycle = 0
    if ms > 0.0:
        time.sleep((ms/1000))

def get_inclination(mpu, offset):
    """
    Liest die Sensorwerte aus der Lib und erhält x,y,z Werte zurück. In der Regel sind das Werte in der Range von -10 bis +10 (ungefähr)
    
    Diese Werte werden nun mit dem Kalibrationsoffset verrechnet und als absolute Zahl zurück gegeben.
    Da für diese Anwendung es uninteressant ist ob man sich im positiven oder negativen Bereich einer Inklination befindent, wird grundsätzlich
    ein positiver Wert zurück gegeben.
    
    Zum Schluß wird der mit dem Offset der jeweilige Achse errechnete Wert auf einen Wertebereich zwischen 0.0 bis 1.0 gemapped.
    
    """
    if mpu != None:
        x, y, z = mpu.acceleration
    else:
        x=y=z=0
     
    # sicherheitshalber auf MIN/MAX prüfen. Schnelle Bewegungen können hier höhere Werte verursachen
    x = constrain(abs(x), VALUES_X[0], VALUES_X[1]) 
    y = constrain(abs(y), VALUES_Y[0], VALUES_Y[1]) 
    z = constrain(abs(z), VALUES_Z[0], VALUES_Z[1]) 

    vx = x
    vy = y
    vz = z
    
    #
    # der Roh-Datenpunkt wird auf auf einen Standardwert zwischen 0.0 und 1.0 gemapped
    mx = map_range(vx, VALUES_X[0], VALUES_X[1], MAP_X_Y_Z[0], MAP_X_Y_Z[1])
    my = map_range(vy, VALUES_Y[0], VALUES_Y[1], MAP_X_Y_Z[0], MAP_X_Y_Z[1])
    mz = map_range(vz, VALUES_Z[0], VALUES_Z[1], MAP_X_Y_Z[0], MAP_X_Y_Z[1])

    mx = abs(mx - offset[0])
    my = abs(my - offset[1])
    mz = abs(mz - offset[2])

    #
    # Nullpunkt setzen um kleine Ausschläge zu eliminieren
    np = NULL_POINT * DAMPING_FACTOR
    mx = (mx if mx > np else 0.0)
    my = (my if my > np else 0.0)
    mz = (mz if mz > np else 0.0)

    if DEBUG_LEVEL >= 2:
        print ("RAW ACCEL x:{:5.3f}/vx:{:5.3f}\t\ty:{:5.3f}/vy:{:5.3f}\t\tz:{:5.3f}/vz:{:5.3f}\tOffset {:}".format(x,vx, y,vy, z,vz, offset))
        print ("MAP ACCEL vx:{:5.3f}/mx:{:5.3f}\t\tvy:{:5.3f}/my:{:5.3f}\t\tvz:{:5.3f}/mz:{:5.3f}".format(vx,mx, vy,my, vz,mz))

    return abs(mx), abs(my), abs(mz)

def damping_calibrate(avg=10, wait=150):
    global DAMPING_FACTOR
    avm = 0.0
    wait /= 1000
    for i in range(avg):
        r,m = readAnalog()
        avm += m
        time.sleep(wait) #  wait
    #
    # Durchschnitt berechnen
    DAMPING_FACTOR = avm / float(avg)
    if DEBUG_LEVEL >= 1:
        print ("DAMPING_FACTOR: {0} avm {1}".format(DAMPING_FACTOR, avm))
    
def mpu_calibrate(sensor, avg=10):
    """
    Startet eine Sensor-Kalibration und baut eine Offset-Tabelle für X/Y/Z auf
    )
    Arg:
        sensor -
        avg - default 10, Anzal der Messungen sollen durchgeführt werden und anschließend wird der Durchschnitt berechnet
    Return:
        Offset-Tabelle [x,y,z]
        
    """
    update_progressbar([0,0,0])
    showText("Calibrate")
    #
    # kurze Vibration des motors
    motorON(motor,35000,100)
    motorOFF(motor,250)
    #
    raw = [0,0,0]
    offset = [0,0,0]
    for i in range(avg):
        x,y,z = get_inclination(sensor, [0,0,0])
        motorON(motor,27000,50)
        motorOFF(motor,25)
        raw[0] += x
        raw[1] += y
        raw[2] += z
        if DEBUG_LEVEL >= 2 :
            print("RAW : {:5.3f}\t{:5.3f}\t{:5.3f}\t{}".format(x,y,z,raw))
    #
    # Durchschnitt für jede Achse berechnen
    offset[0] = abs(raw[0]) / avg
    offset[1] = abs(raw[1]) / avg
    offset[2] = abs(raw[2]) / avg
    
    if DEBUG_LEVEL >= 1:
        print ("OFFS: {0}".format(offset))
    #
    removeText()
    time.sleep(1) # 1sek warten
    
    #
    # Analog-Wert messen um den DAMPING_FACTOR zu definieren
    showText("DAMPING")
    damping_calibrate(avg=10, wait=200)
    removeText()
    showDampingLine()

    # zwei kurze Vibrationen zeigen das Ende der Kalibration
    motorON(motor,35000,150)
    time.sleep(0.5) # kurze Pause 500ms
    motorON(motor,35000,150)
    motorOFF(motor,0)
    time.sleep(0.5) # n sek warten
    
    return offset

def showText(txt, invert=True):
    """
    Anzeige eines Textes in einem Rahmen.
    """
    bc = color_palette[0]
    tc = color_palette[1]
    if invert:
        bc = color_palette[1]
        tc = color_palette[0]
        
    rrect = RoundRect(1+OFF_X, 2+OFF_Y, 60,28, 4, fill=bc, outline=color_palette[1])
    text_area = label.Label(terminalio.FONT, text=txt, color=tc)
    text_area.x = 5 + OFF_X
    text_area.y = OLED_H2 + OFF_Y
    main_group.append(rrect)
    main_group.append(text_area)
    
def removeText():
    main_group.pop()
    main_group.pop()
    
def update_progressbar(xyz):
    """
    Für ein Update der drei Progressbars durch.
    Beim dem Progressbar mit dem höchsten Wert, wird am Ende ein Punkt dargestellt
    Der Punkt symbolisiert auch, welche Achse den duty_cycle des Vibrationsmotors angepasst hat. 
    """
    cx.fill=cy.fill=cz.fill=color_palette[0]
    
    xb_left.value = xyz[0]
    yb_left.value = xyz[1]
    zb_left.value = xyz[2]
    maxV = max(xyz)
    if maxV == 0:
        return
    if maxV == xyz[0]:
        cx.fill=color_palette[1]
    if maxV == xyz[1]:
        cy.fill=color_palette[1]
    if maxV == xyz[2]:
        cz.fill=color_palette[1]

def readAnalog():
    """
    Liest den Analog-Port aus und mapped den Wertebereich von 0..65535 in eine Wertebereich für DAMPING_FACTOR
    Ist der Poti auf 0Ohm wird der DAMPING_FACTOR auf 1.0 gesetzt. Ist das Poti auf max, wird ein Faktor von 5 zurück gegeben.
    Damit ist das System recht träge
    
    Return:
    (RAW,Mapped) = Rückgabe als Tuple, Roh-Wert und gemappter Wert (
    """
    av = poti.value
    if av > 65500:
        av = MAX_POTI
    if av > 1000:
        avm = map_range(av, MIN_POTI,MAX_POTI, MIN_DSF,MAX_DSF)
    else:
        avm = 1.0
    if DEBUG_LEVEL > 0:
        print ([av,avm])
    return (av, avm)

#*******************************************************************************************
#
# Hauptschleife
#
#*******************************************************************************************
# 
# if TEST_MOTOR:
#     print ("MOTOR_TEST")
#     while True:
#         for dc in range(28000,60000,1000):
#             print ("MOTOR {}".format(dc))
#             motorON(motor,dc, 150)
#             motorOFF(motor,50)
#                    
# 

try:
    #
    # Grundsätzlich wird eine Kalibration nach dem Einschalten durchgeführt
    xyz_offset = mpu_calibrate(sensor, CAL_AVG)
    while True:
        btn.update()
        if btn.fell:
            print("Button pressed")
            xyz_offset = mpu_calibrate(sensor, CAL_AVG)
        damping_calibrate(avg=6,wait=50)
        
            
        #
        # akutelle MPU-Werte lesen und den Nullpunkt setzen
        # liegen die Werte über dem NP, dann den Vibrationsmotor laufen lassen.
        # jenachdem wie weit die Brille außerhalb ihres Nullpunkts ist, umso mehr (stärker) vibriert es
        xyz = get_inclination(sensor,xyz_offset)
        dc = 0
        np = NULL_POINT * DAMPING_FACTOR
        #
        # nur für DEMO
        #xyz = [random.random(),random.random(),random.random()]
        
        if max(xyz) > np:
            dc = int(get_DutyCycle(max(xyz)))
            update_progressbar(xyz)
            motorON(motor,dc,100)	# 100ms blockierend den Motor laufen lassen
            motorOFF(motor,100) 	# Abschalten und 100ms warten (default)
        else:
            update_progressbar(xyz)
        if DEBUG_LEVEL >= 1 :
            print("MEASUREMENT [{:5.3f}, {:5.3f}, {:5.3f}]\tDC [{}]".format(xyz[0],xyz[1],xyz[2],dc)) 
        #
        # kurze Pause
        #time.sleep(0.1)
finally:
    # displayio.release_displays()
    print("bye")
    