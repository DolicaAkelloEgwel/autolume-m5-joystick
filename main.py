import asyncio

from bleak import BleakClient
from numpy import arcsin, arctan, sqrt
from pythonosc import udp_client

M5_STICK_ADDR = "00:4B:12:A0:9B:32"
DATA_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

ROTATE_MAX = 45
SCALE_MAX = 2
TRANSLATE_MAX = 20
SPEED_MAX = 2.5
DIVERSITY_MIN = -1
DIVERSITY_MAX = 2

JOY_MIN = -128
JOY_MAX = 72

osc_client = udp_client.SimpleUDPClient("127.0.0.1", 1338)


def map(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))


def callback(sender, data):
    data = eval(data.decode())

    osc_client.send_message(
        f"/speed", map(data[0], JOY_MAX, JOY_MIN, -SPEED_MAX, SPEED_MAX)
    )
    osc_client.send_message(
        f"/diversity", map(data[1], JOY_MIN, JOY_MAX, DIVERSITY_MIN, DIVERSITY_MAX)
    )
    osc_client.send_message(
        f"/x_translate", map(data[2], JOY_MAX, JOY_MIN, -TRANSLATE_MAX, TRANSLATE_MAX)
    )
    osc_client.send_message(
        f"/y_translate", map(data[3], JOY_MAX, JOY_MIN, -TRANSLATE_MAX, TRANSLATE_MAX)
    )

    x_acc, y_acc, z_acc = data[4:]
    pitch = arcsin(x_acc / sqrt(x_acc**2 + y_acc**2 + z_acc**2))
    roll = arctan(y_acc / z_acc)

    osc_client.send_message(f"/rotate", map(pitch, -1.5, 1.5, -ROTATE_MAX, ROTATE_MAX))
    osc_client.send_message(f"/scale", map(roll, -1.5, 1.5, 0.5, 1.5))


async def main(ble_address):

    async with BleakClient(ble_address) as client:

        print("Connected to BLE device:", client.is_connected)
        await client.start_notify(DATA_UUID, callback=callback)

        while True:
            await asyncio.sleep(1)


asyncio.run(main(M5_STICK_ADDR))
