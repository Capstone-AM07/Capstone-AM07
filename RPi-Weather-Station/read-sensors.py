import time
import board
import adafruit_bme280.basic as adafruit_bme280
import adafruit_veml7700

I2C_BUS_RESYNC_SECONDS = 2.0
PRINT_INTERVAL_SECONDS = 1.0
RESCAN_EVERY_N_LOOPS = 15

def scan_i2c(i2c):
    while not i2c.try_lock():
        pass
    try:
        return list(i2c.scan())
    finally:
        i2c.unlock()

def init_bme280(i2c, devices):
    # Prefer 0x76 then 0x77
    for addr in (0x76, 0x77):
        if addr in devices:
            try:
                sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=addr)
                return sensor, addr
            except Exception:
                return None, None
    return None, None

def init_veml7700(i2c, devices):
    # VEML7700 is typically 0x10
    if 0x10 in devices:
        try:
            return adafruit_veml7700.VEML7700(i2c)
        except Exception:
            return None
    return None

def fmt_devices(devs):
    return "[" + ", ".join(f"0x{d:02x}" for d in devs) + "]"

i2c = board.I2C()

# Initial scan + init
devices = scan_i2c(i2c)
print("I2C devices found:", fmt_devices(devices))

bme280, bme_addr = init_bme280(i2c, devices)
if bme280:
    print(f"BME280 detected at 0x{bme_addr:02x}")
else:
    print("BME280 not detected (expected 0x76 or 0x77)")

veml = init_veml7700(i2c, devices)
if veml:
    print("VEML7700 detected at 0x10")
else:
    print("VEML7700 not detected (expected 0x10)")

print("-" * 40)

loop = 0
while True:
    loop += 1

    # Read BME280
    if bme280 is not None:
        try:
            t = bme280.temperature
            h = bme280.humidity
            p = bme280.pressure
            print("BME280")
            print(f"  Temp: {t:.2f} C")
            print(f"  Hum : {h:.2f} %")
            print(f"  Pres: {p:.2f} hPa")
        except OSError:
            print("BME280")
            print("  DISCONNECTED (I2C read error)")
            bme280 = None
            bme_addr = None
    else:
        print("BME280")
        print("  DISCONNECTED")

    # Read VEML7700
    if veml is not None:
        try:
            lux = veml.light
            print("VEML7700")
            print(f"  Lux : {lux:.2f}")
            if hasattr(veml, "white"):
                print(f"  White: {veml.white:.2f}")
        except OSError:
            print("VEML7700")
            print("  DISCONNECTED (I2C read error)")
            veml = None
    else:
        print("VEML7700")
        print("  DISCONNECTED")

    print("-" * 40)

    # Rescan and try to re-init missing sensors
    need_rescan = (bme280 is None) or (veml is None) or (loop % RESCAN_EVERY_N_LOOPS == 0)
    if need_rescan:
        time.sleep(I2C_BUS_RESYNC_SECONDS)
        try:
            devices = scan_i2c(i2c)
        except OSError:
            devices = []

        if bme280 is None:
            bme280, bme_addr = init_bme280(i2c, devices)

        if veml is None:
            veml = init_veml7700(i2c, devices)

    time.sleep(PRINT_INTERVAL_SECONDS)
