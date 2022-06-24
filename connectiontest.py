from pylogix import PLC
import time

with PLC("192.168.100.250") as driver:

    tags = ['V_DOJAZDOWA_KW','V_JAZDA_WEJ','V_JAZDA_WYJ','S_WYJ']

    print(str(driver.GetTagList().Value))
"""
    while True:
        ret = driver.Read(tags)
        time.sleep(0.008)
        for r in ret:
            print(r.Value)
            """