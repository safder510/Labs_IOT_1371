from machine import Pin, SoftI2C
import dht
import time
import network
import socket
import neopixel
import ure
import ssd1306

# Station Mode Setup
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Talha", "_--_--_--")

# Access Point mode setup
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP-32-S3', password='12345678', authmode= network.AUTH_WPA2_PSK)

for i in range(10):
    if wifi.isconnected():
        print("WiFi Connected")
        print(f'STA IP Address: {wifi.ifconfig()[0]}')
        print(f'AP IP Address: {ap.ifconfig()[0]}')
        break
    else:
        print("Not Connected")
        time.sleep(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 80))
s.listen(5)

def WebPage():
    page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Futuristic Interactive Page</title>
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(to right, #141E30, #243B55);
                color: white;
                text-align: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                display: inline-block;
                max-width: 500px;
            }
            textarea {
                width: 90%;
                height: 100px;
                background: rgba(255, 255, 255, 0.15);
                border: none;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 16px;
            }
            input {
                width: 60px;
                text-align: center;
                margin: 5px;
                border: none;
                padding: 8px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 8px;
                font-size: 16px;
            }
            h1, h3 {
                font-weight: 300;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 S3</h1>
            <h3>Temperature: <span id="temperature">Collecting Data...</span></h3>
            <h3>Humidity: <span id="humidity">Collecting Data...</span></h3>
            <form>
                <input type="text" id="oled_text" placeholder="OLED Text (1 line, max 128 chars)" maxlength="128" style="width: 300px;">
                <br><br>
                <button onclick="submitText()">Submit Text</button>
                <br><br>
            </form>
            <form>
                <label>R:</label>
                <input type="number" id="red" min="0" max="255" value = "0" oninput="validateInput(this)">
                <label>G:</label>
                <input type="number" id="green" min="0" max="255" value = "0" oninput="validateInput(this)">
                <label>B:</label>
                <input type="number" id="blue" min="0" max="255" value = "0" oninput="validateInput(this)">
                <br><br>
                <button onclick="submitRGB()">Submit RGB</button>
            </form>
        </div>

        <script>
            function validateInput(input) {
                if (input.value < 0) input.value = 0;
                if (input.value > 255) input.value = 255;
                input.value = input.value.replace(/[^0-9]/g, '');
            }

            function GetTemperature() {
                fetch('/temperature')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById("temperature").innerText = data + "°C";
                    });
            }
            setInterval(GetTemperature, 1000);

            function GetHumidity() {
                fetch('/humidity')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById("humidity").innerText = data + "%";
                    });
            }
            setInterval(GetHumidity, 1000);

            function submitRGB() {
                let r = document.getElementById("red").value;
                let g = document.getElementById("green").value;
                let b = document.getElementById("blue").value;

                localStorage.setItem("red", r);
                localStorage.setItem("green", g);
                localStorage.setItem("blue", b);

                fetch(`/?RGB&r=${r}&g=${g}&b=${b}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("HTTP error : ${response.status}");
                        }
                    });
            }

            function submitText() {
                let text = document.getElementById("oled_text").value;

                localStorage.setItem("oled_text", text);

                fetch(`/?TEXT&text=${encodeURIComponent(text)}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("HTTP error : ${response.status}");
                        }
                    });
            }

            window.onload = function() {
                let red = localStorage.getItem("red");
                let green = localStorage.getItem("green");
                let blue = localStorage.getItem("blue");

                if (red) document.getElementById("red").value = red;
                if (green) document.getElementById("green").value = green;
                if (blue) document.getElementById("blue").value = blue;

                let text = localStorage.getItem("oled_text");
                if(text) document.getElementById("oled_text").value = text;
            };
        </script>
    </body>
    </html>
    """
    return page

sensor = dht.DHT11(Pin(4))
neo = neopixel.NeoPixel(Pin(48),1)
i2c = SoftI2C( sda = Pin(8), scl = Pin(9))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
def SendTemperature():
    try:
        sensor.measure()
        temp = sensor.temperature()
        return str(temp)
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return "N/A"
def SendHumidity():
    try:
        sensor.measure()
        humidity = sensor.humidity()
        return str(humidity)
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return "N/A"
def UpdateNeoPixel(r,g,b):
    neo[0] = (r,g,b)
    neo.write()
def OledDisplay(text):
    text = text.replace("%20", " ")
    text = text.replace("%0A", "\n")
    oled.fill(0)
    lines = []
    while len(text) > 0 and len(lines) < 8:
        lines.append(text[:16])
        text = text[16:]
    for i, line in enumerate(lines):
        oled.text(line, 0, 8 * i)
    oled.show()
while True:
    conn, addr = s.accept()
    print(f'Connected to {addr}')
    request = conn.recv(1024).decode() #decode here.
    print(request)
    if "GET /temperature" in request:
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + SendTemperature()
        conn.send(response.encode())
    elif "GET /humidity" in request:
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + SendHumidity()
        conn.send(response.encode())
    elif "GET /?RGB" in request:
        params = request.split(" ")[1].split("&")
        r = int(params[1].split("=")[-1])
        g = int(params[2].split("=")[-1])
        b = int(params[3].split("=")[-1])
        UpdateNeoPixel(r,g,b)
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + "RGB Updated"
        conn.send(response.encode())
    elif "GET /?TEXT" in request:
        params = request.split(" ")[1]
        text = params.split("=")[1]
        OledDisplay(text)
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + "OLED Updated"
        conn.send(response.encode())
    else:
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + WebPage()
        conn.send(response.encode())
    conn.close()
