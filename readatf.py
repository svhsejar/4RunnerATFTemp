import serial
import time
import re
# Check 221627
# For ATF
# USB serial port examples: Windows e.g. COM3, Linux e.g. /dev/ttyUSB0 or /dev/tty.usbserial-1460
PORT = "/dev/tty.usbserial-14610"   # change this depending on your Operating System and device
BAUD = 38400

def send(ser, cmd, delay=0.3):
    ser.write((cmd + "\r").encode())
    time.sleep(delay)
    resp = ser.read_all().decode(errors="ignore")
    return resp

def parse_atf(resp):
    m = re.search(r"61\s*82\s*([0-9A-Fa-f]{2})", resp)
    if not m:
        return None
    x = int(m.group(1), 16)
    return x - 40

def parse_coolant(resp):
    m = re.search(r"41\s*05\s*([0-9A-Fa-f]{2})", resp)
    if not m:
        return None
    x = int(m.group(1), 16)
    return x - 40

def c_to_f(celsius):
    return celsius * 9.0 / 5.0 + 32.0

def init(ser):
    cmds = ["ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP6"]
    for c in cmds:
        ser.write((c + "\r").encode())
        time.sleep(0.5)
        ser.read_all()

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)

    init(ser)

    print("Monitoring ATF + Coolant...\n")

    while True:
        atf_resp = send(ser, "2182")
        cool_resp = send(ser, "0105")

        atf = parse_atf(atf_resp)
        cool = parse_coolant(cool_resp)

        if atf is not None:
            atf_f = c_to_f(atf)
            print(f"ATF Temp: {atf} °C / {atf_f:.1f} °F")
            if atf < 36:
                print("ATF cold, wait for warm-up")
            elif atf <= 45:
                print("Remove the overflow plug and adjust ATF level")
            else:
                print("ATF temperature high; switch off ignition and wait for cooldown before adjusting overflow")
        else:
            print("ATF: no data")

        if cool is not None:
            print(f"Coolant Temp: {cool} °C")
        else:
            print("Coolant: no data")

        print("-" * 30)
        time.sleep(30)

if __name__ == "__main__":
    main()