import time
import DAN
import random
import threading
import sys
from collections import deque


class DAI2Device:
    def __init__(self):
        self.ServerURL = "https://4.iottalk.tw"
        self.Reg_addr = None
        self.mac_addr = "CD8600D38" + str(random.randint(100, 999))
        self.Reg_addr = self.mac_addr
        self.d_name = str(random.randint(100, 999)) + "_Dummy_Device"

        DAN.profile["dm_name"] = "Dummy_Device"
        DAN.profile["df_list"] = ["Dummy_Sensor", "Dummy_Control"]
        DAN.profile["d_name"] = self.d_name
        DAN.device_registration_with_retry(self.ServerURL, self.Reg_addr)
        print("dm_name is ", DAN.profile["dm_name"])
        print("Server is ", self.ServerURL)

        self.gotInput = False
        self.theInput = "haha"
        self.allDead = False
        self.previous_input = 0
        self.queue = deque()

        thread_read = threading.Thread(target=self.doRead)
        thread_read.daemon = True
        thread_read.start()

        thread_send = threading.Thread(target=self.run)
        thread_send.daemon = True
        thread_send.start()

    def doRead(self):
        while True:
            while self.gotInput:
                time.sleep(0.1)
                continue
            try:
                self.theInput = input("Give me data: ")
            except Exception:
                self.allDead = True
                print("\n\nDeregister " + DAN.profile["d_name"] + " !!!\n", flush=True)
                DAN.deregister()
                sys.stdout = sys.__stdout__
                print(" Thread say Bye bye ---------------", flush=True)
                sys.exit(0)
            if self.theInput == "quit" or self.theInput == "exit":
                self.allDead = True
            else:
                print("Will send " + self.theInput, end="   , ")
                self.gotInput = True
            if self.allDead:
                break

    def enqueue(self, val):
        print("val sent: ", val)
        if val == 1:
            self.queue.append('l')
        elif val == 2:
            self.queue.append('d')
        elif val == 3:
            self.queue.append('r')
        elif val == 4:
            self.queue.append('s')

    def run(self):
        while True:
            try:
                if self.allDead:
                    break
                value1 = DAN.pull("Dummy_Control")
                if value1 is not None:
                    if value1[0] != self.previous_input:
                        self.previous_input = value1[0]
                        print(value1[0])
                        self.enqueue(value1[0])
                    else:
                        print("same input")

                if self.gotInput:
                    try:
                        value2 = float(self.theInput)
                    except:
                        value2 = 0
                    if self.allDead:
                        break
                    self.gotInput = False
                    DAN.push("Dummy_Sensor", value2, value2)

            except Exception as e:
                print(e)
                if str(e).find("mac_addr not found:") != -1:
                    print("Reg_addr is not found. Try to re-register...")
                    DAN.device_registration_with_retry(self.ServerURL, self.Reg_addr)
                else:
                    print("Connection failed due to unknown reasons.")
                    time.sleep(1)
            try:
                time.sleep(0.2)
            except KeyboardInterrupt:
                break
