import BlynkLib
import network
import time
import dht
import machine, neopixel

sensor = dht.DHT11(machine.Pin(4))

neo = neopixel.NeoPixel(machine.Pin(48),1)
# Your Blynk authentication token
BLYNK_AUTH = "sRXVwB9vnl5zT5wlBhiWsRt6LG7kOw1z"

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("TECNO SPARK 8C", "safder510")

while not wlan.isconnected():
    time.sleep(1)

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH, insecure=True)
r, g, b = 0, 0, 0
# Define a virtual pin function
@blynk.on("V0")
def v0_handler(value):
    global r
    r = 255 if int(value[0]) else 0  # Turn red on/off
    update_neopixel()

@blynk.on("V1")
def v1_handler(value):
    global g
    g = 255 if int(value[0]) else 0  # Turn green on/off
    update_neopixel()

@blynk.on("V2")
def v2_handler(value):
    global b
    b = 255 if int(value[0]) else 0  # Turn blue on/off
    update_neopixel()

def update_neopixel():
    neo[0] = (r, g, b)
    neo.write()
def send_value():
    try:
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()
        blynk.virtual_write(3, temp)
        blynk.virtual_write(4, humidity)
        
    except:
        print("Could not send data")

# Main loop
while True:
    blynk.run()
    send_value()
    time.sleep(0.05)
