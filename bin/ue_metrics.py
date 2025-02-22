#!/usr/bin/env python3
import time

import quectel_control

ue_client = quectel_control.QuectelControlClient()
while True:
    response = ue_client.servingcell()
    if "QENG" in response:
        print(response)
    time.sleep(1)
