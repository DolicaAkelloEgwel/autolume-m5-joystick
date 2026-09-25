import asyncio

from bleak import BleakClient
from numpy import arcsin, arctan, sqrt
from pythonosc import udp_client

M5_STICK_ADDR = "00:4B:12:A0:9B:32"
DATA_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

MAX_ROTATE = 45
MAX_SCALE = 2
MAX_TRANSLATE = 20
MAX_SPEED = 2.5
MIN_DIVERSITY = -1
MAX_DIVERSITY = 2

JOY_MIN = -128
JOY_MAX = 72

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 5005)


def map(value, inMin, inMax, outMin, outMax):
    return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))


def callback(sender, data):
    data = eval(data.decode())

    osc_client.send_message(f"/speed", map(data[0], 63, -128, -MAX_SPEED, MAX_SPEED))
    osc_client.send_message(
        f"/diversity", map(data[1], JOY_MIN, JOY_MAX, MIN_DIVERSITY, MAX_DIVERSITY)
    )
    osc_client.send_message(
        f"/x_translate", map(data[2], JOY_MAX, JOY_MIN, -MAX_TRANSLATE, MAX_TRANSLATE)
    )
    osc_client.send_message(
        f"/y_translate", map(data[3], JOY_MAX, JOY_MIN, -MAX_TRANSLATE, MAX_TRANSLATE)
    )

    x_acc, y_acc, z_acc = data[4:]
    pitch = arcsin(x_acc / sqrt(x_acc**2 + y_acc**2 + z_acc**2))
    roll = arctan(y_acc / z_acc)

    osc_client.send_message(f"/rotate", map(pitch, -1.5, 1.5, -MAX_ROTATE, MAX_ROTATE))
    osc_client.send_message(f"/scale", map(roll, -1.5, 1.5, 0.5, 1.5))


async def main(ble_address):

    async with BleakClient(ble_address) as client:

        print("Connected to BLE device:", client.is_connected)
        await client.start_notify(DATA_UUID, callback=callback)

        while True:
            await asyncio.sleep(1)


asyncio.run(main(M5_STICK_ADDR))
