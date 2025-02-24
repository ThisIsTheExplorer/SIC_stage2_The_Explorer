from umqtt.robust import MQTTClient
from machine import Pin, SoftI2C
from machine import ADC
import machine as m
import ssd1306
import dht

ubidotsToken = "BBUS-pCxGOtGH2ItfCdtidQtG79BsVq3JcM"
clientID = "man3medan"
client = MQTTClient("clientID", "industrial.api.ubidots.com", 1883, user = ubidotsToken, password = ubidotsToken)

print("Loading...")

def checkwifi():
    while not sta_if.isconnected():
        time.sleep_ms(500)
        print(".")
        sta_if.connect()

# Inisialisasi OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(4))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Inisialisasi LED pada GPIO 2
led_Hijau = Pin(17, Pin.OUT)
led_Kuning = Pin(18, Pin.OUT)
led_Merah = Pin(19, Pin.OUT)
buzzer = Pin(23, Pin.OUT)

# Inisialisasi DHT11 pada GPIO 16
dht11 = dht.DHT11(Pin(16))

# Inisialisasi LDR
adc = ADC(Pin(33, mode=Pin.IN))
adc.atten(ADC.ATTN_11DB)

def publish():
    while True:
        checkwifi()
        client.connect()
        lat = 3.63755
        lng = 98.665721
        ldr_value = adc.read()
        
        try:
            # Mengambil data dari sensor DHT11
            dht11.measure()
            suhu = dht11.temperature()  # Suhu dalam Celsius
            kelembaban = dht11.humidity()  # Kelembaban dalam %

            # Menampilkan data ke OLED
            oled.fill(0)  # Bersihkan layar
            oled.text("  The Explorer  ", 0, 0)
            oled.text("----------------", 0, 9)
            
            oled.text("LDR  :{} Lux".format(ldr_value), 0, 20)
            oled.text("Temp :{} Celcius".format(suhu), 0, 30)
            oled.text("Humi :{}%".format(kelembaban), 0, 40)            

            # Cek kelembaban dan kontrol LED
            if suhu <32:
                led_Hijau.on()
                led_Kuning.off()
                led_Merah.off()
                buzzer.off()
                oled.text("Buzz :OFF  ", 0, 50)
                msg = b'{"buzzer": {"value":%s}}' % (0)
                print(msg)
                client.publish(b"/v1.6/devices/esp32", msg)
                time.sleep(0.2)
                
            elif suhu <35:
                led_Hijau.off()
                led_Kuning.on()
                led_Merah.off()
                buzzer.off()
                oled.text("Buzz :OFF  ", 0, 50)
                msg = b'{"buzzer": {"value":%s}}' % (0)
                print(msg)
                client.publish(b"/v1.6/devices/esp32", msg)
                time.sleep(0.2)
                
            else :
                led_Hijau.off()
                led_Kuning.off()
                led_Merah.on()
                buzzer.on()
                oled.text("Buzz :ON  ", 0, 50)
                msg = b'{"buzzer": {"value":%s}}' % (1)
                print(msg)
                client.publish(b"/v1.6/devices/esp32", msg)
                time.sleep(0.2)

            oled.show()

        except OSError as e:
            oled.fill(0)
            oled.text("Error reading DHT11", 10, 20)
            oled.show()
            print(f"Error Reading sensor")
            time.sleep(1)
            
        var = 4
        msg = b'{"location": {"value":%s, "context":{"lat":%s, "lng":%s}}}' % (var, lat, lng)
        print(msg)
        client.publish(b"/v1.6/devices/esp32", msg)
        time.sleep(0.2)
        
        msg = b'{"ldr": {"value":%s}}' % (ldr_value)
        print(msg)
        client.publish(b"/v1.6/devices/esp32", msg)
        time.sleep(0.2)
        
        msg = b'{"suhu": {"value":%s}}' % (suhu)
        print(msg)
        client.publish(b"/v1.6/devices/esp32", msg)
        time.sleep(0.2)
        
        msg = b'{"kelembaban": {"value":%s}}' % (kelembaban)
        print(msg)
        client.publish(b"/v1.6/devices/esp32", msg)
        time.sleep(0.2)
         
        time.sleep(2)
publish()