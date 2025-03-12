from machine import Pin, SoftI2C
import network
import socket
import ssd1306

# Station Mode Setup
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("TECNO SPARK 8C", "safder510")

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


title = "Calculator"

def OledDisplay(text):
    oled.fill(0)
    oled.text(title, 30, 0)
    lines = text.split("\n")
    for i, line in enumerate(lines[:6]):
        oled.text(line, 0, 12 + (i * 10))
    oled.show()



i2c = SoftI2C(sda=Pin(9), scl=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def WebPage():
    page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESP32 Calculator</title>
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(to right, #000428, #004e92);
                color: white;
                text-align: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                display: inline-block;
                max-width: 320px;
            }
            .display {
                width:95%;
                height: 50px;
                background: rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                font-size: 24px;
                text-align: right;
                padding: 10px;
                color: white;
                margin-bottom: 15px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
            }
            button {
                width: 70px;
                height: 70px;
                border-radius: 10px;
                background: #004e92;
                color: white;
                border: none;
                font-size: 24px;
                cursor: pointer;
            }
            .equal {
                grid-column: span 2;
                background: #d32f2f;
            }
            .plus {
                grid-column: span 1;
                background: #ff9800;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 Calculator</h1>
            <div class="display" id="display">0</div>
            <div class="grid">
                <button onclick="appendNumber('7')">7</button>
                <button onclick="appendNumber('8')">8</button>
                <button onclick="appendNumber('9')">9</button>
                <button onclick="setOperator('/')">/</button>
                <button onclick="appendNumber('4')">4</button>
                <button onclick="appendNumber('5')">5</button>
                <button onclick="appendNumber('6')">6</button>
                <button onclick="setOperator('*')">*</button>
                <button onclick="appendNumber('1')">1</button>
                <button onclick="appendNumber('2')">2</button>
                <button onclick="appendNumber('3')">3</button>
                <button onclick="setOperator('-')">-</button>
                <button onclick="clearDisplay()">C</button>
                <button onclick="appendNumber('0')">0</button>
                <button onclick="calculate()" >=</button>
                <button onclick="setOperator('+')">+</button>
            </div>
        </div>

        <script>
            let num1 = "";
            let num2 = "";
            let operator = "";
            let display = document.getElementById("display");

            function appendNumber(number) {
                if (operator === "") {
                    num1 += number;
                    display.innerText = num1;
                } else {
                    num2 += number;
                    display.innerText = num2;
                }
            }

            function setOperator(op) {
                if (num1 !== "") {
                    operator = op;
                }
            }

            function clearDisplay() {
                num1 = "";
                num2 = "";
                operator = "";
                display.innerText = "0";
            }

            function calculate() {
                fetch(`/?CALC&num1=${num1}&op=${operator}&num2=${num2}`)
                    .then(response => response.text())
                    .then(data => {
                        display.innerText = data;
                        num1 = data;
                        num2 = "";
                        operator = "";
                    });
            }
        </script>
    </body>
    </html>
    """
    return page

while True:
    conn, addr = s.accept()
    print(f'Connected to {addr}')
    request = conn.recv(1024).decode()
    print(request)
    
    if "GET /?CALC" in request:
        try:
            params = request.split(" ")[1].split("&")
            num1 = float(params[1].split("=")[-1])
            operator = params[2].split("=")[-1]
            num2 = float(params[3].split("=")[-1])
            
            if operator == "+":
                result = num1 + num2
            elif operator == "-":
                result = num1 - num2
            elif operator == "*":
                result = num1 * num2
            elif operator == "/":
                result = num1 / num2 if num2 != 0 else "Error"
            else:
                result = "Invalid"
            
            OledDisplay(f"{num1} {operator} {num2}\n= {result}")
            response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + str(result)
        except Exception as e:
            response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nError"
    else:
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + WebPage()
    
    conn.send(response.encode())
    conn.close()