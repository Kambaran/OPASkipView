#import asyncio
import time
import sys
sys.path.insert(0,"..")

import logging
#from IPython import embed
from opcua import ua, Client


class SubHandler(object):

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)

def Main():
    logging.basicConfig(level=logging.WARN)

    client=Client("opc.tcp://localhost:4840/freeopcua/server/")

    try:    
        while True:
            client.connect()
            root = client.get_root_node()
            print("Object node is: ", root)
            print("Children root are: ", root.get_children())

            myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
            obj = root.get_child(["0:Objects", "2:MyObject"])
            obj2 = root.get_child(["0:Objects"])

            print("myvar is: ", myvar)
            print("myobj is: ", obj)
            print("myobj is: ", obj2)

            #embed()        

            count = 0        
            while True:
                time.sleep(0.2)
                count += 0.1
                print("myvar is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value())

                if (( root.get_children()[0].get_children()[1].get_variables()[0].get_value()) > 40):
                    print("Teperature value too high !")
                    time.sleep(2)
                    break




    finally:
        client.disconnect() 

if __name__=="__main__":

    Main()