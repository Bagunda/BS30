#!/usr/bin/python

import logging
import datetime
import os
import time
sleep1 = 1

from subprocess import call

def tologread(msg):
    call(["logger", "-t", "d30", msg])

def tozabbix(tag, msg):
    string = "zabbix_sender -z bagsus.ru -s 'OrehBS30' -k '" + tag + "' -o " + "'" + str(msg) + "'"
    myCmd = os.popen(string).read()
    # zabbix_sender -z bagsus.ru -s 'OrehBS30' -k 'i2c_write_error' -o 1
    # print(myCmd)
    c2 = myCmd.split("sent: ")
    c3 = c2[1].split(";")
    sent = int(c3[0])
    if (myCmd.find("failed: 1") != -1):
        tologread("Send to zabbix FAILURE")
        tologread(string)
        tologread(str(myCmd))
        # print(myCmd)
        return False
    else:
        # tologread("Send to zabbix OK: " + string)
        return True

os.chdir("/root")
#logging.basicConfig(filename="/root/logs/mqtt_to_relay.log", filemode="w", level=logging.INFO)
logging.basicConfig(filename="/root/d30.log", level=logging.INFO)

msg = "Programm started. Paused to " + str(sleep1) + "sec"

tologread(msg)
msg = ''

time.sleep(sleep1)

from OmegaExpansion import onionI2C
import sys
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import unicodedata
import json

my_file = open("device_id")
device_id = my_file.read()
my_file.close()

my_file = open("/root/mqtt_credentials")
my_string = my_file.read()
my_file.close()
mqtt_credentials_from_file_dict = json.loads(my_string)

MQTTtopic_header = "BS"
MQTT_client_id_publisher = device_id + '_publisher_in_listener'
MQTT_client_id_subscriber = device_id + '_listener'

# DEVICES = dict(MO1=0x21)
# MCPs = dict(MO1=0x21, MO2=0x22, MI1=0x23, MI2=0x24, M_INT=0x27, MB1=0x25, MB2=0x26)
i2c = onionI2C.OnionI2C()

ERRtoConnMQTT = False

previousGPIO = {}
InputsMap = {'MB1' : {'A' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}, 'B' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}}, 'MB2' : {'A' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}, 'B' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}}, 'MI1' : {'A' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}, 'B' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}}, 'MI2' : {'A' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}, 'B' : {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0}}}
OutputsStates = {'MO1' : {'A' : 0, 'B' : 0}, 'MO2' : {'A' : 0, 'B' : 0}}



def setup_MCPs():
    if (MI2.set_byte('A', 'IODIR', 0xFF)): #0xFF - as input
        version16 = False
    else:
        version16 = False
        
    RelaysStatesAfterReboot = {'MO1': {'A': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}, 'B': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}, 'MO2': {'A': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}, 'B': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}}

    MB1a={}
    MB2a={}
    MI1a={}
    MI2a={}
    M_INTa={}

    for bank in MCP.Registers.get('IODIR'):
        MB1.set_byte(bank, 'IODIR', 0xFF) #0xFF - all directions as input
        MB1.set_byte(bank, 'GPINTEN', 0xFF) #0xFF - interrupt enable
        MB1.set_byte(bank, 'INTCON', 0x00)
        MB1.set_byte(bank, 'GPPU', 0xFF) #0xFF - pullup enable
        MB2.set_byte(bank, 'IODIR', 0xFF) #0xFF - all directions as input
        MB2.set_byte(bank, 'GPINTEN', 0xFF) #0xFF - interrupt enable
        MB2.set_byte(bank, 'INTCON', 0x00)
        MB2.set_byte(bank, 'GPPU', 0xFF) #0xFF - pullup enable
        
        MI1.set_byte(bank, 'IODIR', 0xFF) #0xFF - all directions as input
        MI1.set_byte(bank, 'GPINTEN', 0xFF) #0xFF - interrupt enable
        MI1.set_byte(bank, 'INTCON', 0x00)
        MI1.set_byte(bank, 'GPPU', 0xFF) #0xFF - pullup enable

        if (version16 == False):
            MI2.set_byte(bank, 'IODIR', 0xFF) #0xFF - all directions as input
            MI2.set_byte(bank, 'GPINTEN', 0xFF) #0xFF - interrupt enable
            MI2.set_byte(bank, 'INTCON', 0x00)
            MI2.set_byte(bank, 'GPPU', 0xFF) #0xFF - pullup enable
        
        
        MB1a[bank] = MB1.get_byte(bank, "GPIO")  #read state for reset interrupt to default

        MB2a[bank] = MB2.get_byte(bank, "GPIO")  #read state for reset interrupt to default
        MI1a[bank] = MI1.get_byte(bank, "GPIO")  #read state for reset interrupt to default
        if (version16 == False):
            MI2a[bank] = MI2.get_byte(bank, "GPIO")  #read state for reset interrupt to default
        
        M_INTa[bank] = M_INT.get_byte(bank, "GPIO") #read state for reset interrupt to default
        
        
    M_INT.set_byte('A', 'IODIR', 0xFF) #0xFF - all directions as input
    M_INT.set_byte('A', 'GPINTEN', 0xFF) #0xFF - interrupt enable
    M_INT.set_byte('A', 'INTCON', 0xFF)
    M_INT.set_byte('A', 'GPPU', 0xFF) #0xFF - pullup enable
    M_INT.set_byte('A', 'DEFVAL', 0xFF)

    M_INT.set_byte('B', 'OLAT', 0xFF) #0xFF - high level
    M_INT.set_byte('B', 'IODIR', 0x00) #0xFF - all directions as input
    
    previousGPIO['MB1'] = MB1a
    previousGPIO['MB2'] = MB2a
    previousGPIO['MI1'] = MI1a
    if (version16 == version16):
        previousGPIO['MI2'] = MI2a
        MIi = {'MI1' : MI1a}
    else:
        MIi = {'MI1' : MI1a, 'MI2' : MI2a}
    previousGPIO['M_INT'] = M_INTa
    
    
    InputsMap['MB1']['A'][7] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 0}}}
    InputsMap['MB1']['A'][6] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 1}}}
    InputsMap['MB1']['A'][5] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 2}}}
    InputsMap['MB1']['A'][4] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 3}}}
    InputsMap['MB1']['A'][3] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 6}}}
    InputsMap['MB1']['A'][2] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 5}}}
    InputsMap['MB1']['A'][1] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 4}}}
    InputsMap['MB1']['A'][0] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 3}}}
    
    InputsMap['MB1']['B'][6] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 2}}}
    InputsMap['MB1']['B'][5] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 1}}}
    InputsMap['MB1']['B'][4] = {'action' : 'toggle', 'devices' : {'M1' : {'B' : 0}}}
    InputsMap['MB1']['B'][3] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 4}}}
    InputsMap['MB1']['B'][2] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 5}}}
    InputsMap['MB1']['B'][1] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 6}}}
    InputsMap['MB1']['B'][0] = {'action' : 'toggle', 'devices' : {'M1' : {'A' : 7}}}
    
    InputsMap['MB2']['A'][0] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 4}}}
    InputsMap['MB2']['A'][1] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 5}}}
    InputsMap['MB2']['A'][2] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 6}}}
    InputsMap['MB2']['A'][3] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 7}}}
    InputsMap['MB2']['A'][4] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 3}}}
    InputsMap['MB2']['A'][5] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 2}}}
    InputsMap['MB2']['A'][6] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 1}}}
    InputsMap['MB2']['A'][7] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 0}}}
    
    InputsMap['MB2']['B'][0] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MB2']['B'][1] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 5}}}
    InputsMap['MB2']['B'][2] = {'action' : 'toggle', 'devices' : {'M2' : {'B' : 4}}}
    InputsMap['MB2']['B'][3] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 0}}}
    InputsMap['MB2']['B'][4] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 1}}}
    InputsMap['MB2']['B'][5] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 2}}}
    InputsMap['MB2']['B'][6] = {'action' : 'toggle', 'devices' : {'M2' : {'A' : 3}}}
    
    InputsMap['MI2']['B'][0] = {'action' : 'push', 'devices' : {'M2' : {'A' : 4}}}
    InputsMap['MI2']['B'][1] = {'action' : 'prohodnoy', 'devices' : {'M1' : {'B' : 1}}}
    InputsMap['MI2']['B'][2] = {'action' : 'push', 'devices' : {'M1' : {'A' : 7}}}
    InputsMap['MI2']['B'][3] = {'action' : 'push', 'devices' : {'M1' : {'A' : 6}}}
    InputsMap['MI2']['B'][4] = {'action' : 'push', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MI2']['B'][5] = {'action' : 'push', 'devices' : {'M1' : {'A' : 5}}}
    InputsMap['MI2']['B'][6] = {'action' : 'push', 'devices' : {'M2' : {'A' : 3}}}
    InputsMap['MI2']['B'][7] = {'action' : 'push', 'devices' : {'M1' : {'A' : 3}}}
    
    InputsMap['MI1']['A'][0] = {'action' : 'mqtt', 'devices' : {'M1' : {'A' : 4}}}
    InputsMap['MI1']['A'][1] = {'action' : 'push', 'devices' : {'M1' : {'A' : 2}, 'M1' : {'A' : 2}}}
    InputsMap['MI1']['A'][2] = {'action' : 'push', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MI1']['A'][3] = {'action' : 'push', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MI1']['A'][4] = {'action' : 'push', 'devices' : {'M1' : {'A' : 2}}}
    InputsMap['MI1']['A'][5] = {'action' : 'push', 'devices' : {'M1' : {'A' : 1}}}
    InputsMap['MI1']['A'][6] = {'action' : 'prohodnoy', 'devices' : {'M1' : {'B' : 1}}}
    InputsMap['MI1']['A'][7] = {'action' : 'push', 'devices' : {'M1' : {'A' : 0}}}
    
    InputsMap['MI1']['B'][0] = {'action' : 'mqtt', 'devices' : {'M1' : {'A' : 7}}}
    InputsMap['MI1']['B'][1] = {'action' : 'push', 'devices' : {'M1' : {'A' : 7}}}
    InputsMap['MI1']['B'][2] = {'action' : 'push', 'devices' : {'M1' : {'A' : 6}}}
    InputsMap['MI1']['B'][3] = {'action' : 'push', 'devices' : {'M1' : {'A' : 5}}}
    InputsMap['MI1']['B'][4] = {'action' : 'push', 'devices' : {'M1' : {'A' : 4}}}
    InputsMap['MI1']['B'][5] = {'action' : 'push', 'devices' : {'M1' : {'B' : 0}}}
    InputsMap['MI1']['B'][6] = {'action' : 'push', 'devices' : {'M1' : {'B' : 1}}}
    InputsMap['MI1']['B'][7] = {'action' : 'push', 'devices' : {'M1' : {'B' : 2}}}
    
    InputsMap['MI2']['A'][0] = {'action' : 'push', 'devices' : {'M2' : {'A' : 4}}}
    InputsMap['MI2']['A'][1] = {'action' : 'push', 'devices' : {'M2' : {'A' : 5}}}
    InputsMap['MI2']['A'][2] = {'action' : 'push', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MI2']['A'][3] = {'action' : 'push', 'devices' : {'M2' : {'B' : 6}}}
    InputsMap['MI2']['A'][4] = {'action' : 'push', 'devices' : {'M2' : {'B' : 3}}}
    InputsMap['MI2']['A'][5] = {'action' : 'push', 'devices' : {'M2' : {'B' : 2}}}
    InputsMap['MI2']['A'][6] = {'action' : 'push', 'devices' : {'M2' : {'B' : 1}}}
    InputsMap['MI2']['A'][7] = {'action' : 'push', 'devices' : {'M2' : {'B' : 0}}}
    

    Inputs_map_jsonstring = json.dumps(InputsMap)
    my_file = open("Inputs_map.json", "w")
    my_file.write(Inputs_map_jsonstring)
    my_file.close()
    
    
    my_file = open("OutputsStates.json")
    my_string = my_file.read()
    OutputsStates_from_file = json.loads(my_string)
    my_file.close()        
        
        
    my_file = open("RelaysStatesAfterReboot.json")
    my_string = my_file.read()
    RelaysStatesAfterReboot_dict = json.loads(my_string)
    my_file.close()
    
    for MCP_name_u in RelaysStatesAfterReboot_dict:
        MCP_name = str(MCP_name_u)
        for bank_u in RelaysStatesAfterReboot_dict.get(MCP_name):
            bank = str(bank_u)
            for pin_number_u, value in RelaysStatesAfterReboot_dict.get(MCP_name).get(bank).items():
                pin_number = int(pin_number_u)
                RelaysStatesAfterReboot[MCP_name][bank][pin_number] = RelaysStatesAfterReboot_dict.get(MCP_name_u).get(bank_u).get(pin_number_u)
                if (isinstance(value, dict)):
                    input_MCP_name_0 = value.keys()[0]
                    input_MCP_name = str(input_MCP_name_0)
                    input_device_bank_u, input_device_pin_number_u = value.get(input_MCP_name_0).items()[0]
                    input_device_bank = str(input_device_bank_u)
                    input_device_pin_number = int(input_device_pin_number_u)
                    input_gpio = MIi.get(input_MCP_name).get(input_device_bank)
                    value_on_pin_0 = int(input_gpio & (1 << input_device_pin_number) > 0)
                    if (value_on_pin_0 == 1): value_on_pin = 0
                    if (value_on_pin_0 == 0): value_on_pin = 1
                    RelaysStatesAfterReboot[MCP_name][bank][pin_number] = value_on_pin
                if (value == 0):
                    RelaysStatesAfterReboot[MCP_name][bank][pin_number] = 0
                if (value == 1):
                    RelaysStatesAfterReboot[MCP_name][bank][pin_number] = 1
                if (value == 'before_reboot'):
                    GPIO_bank = int(OutputsStates_from_file.get(MCP_name).get(bank))
                    value_on_pin = int(GPIO_bank & (1 << pin_number) > 0)
                    RelaysStatesAfterReboot[MCP_name][bank][pin_number] = value_on_pin
            
    
    for MCP_name in RelaysStatesAfterReboot:
        for bank, values in RelaysStatesAfterReboot.get(MCP_name).items():
            OutputsStates[MCP_name][bank] = ((values[0])) + ((2*values[1]) ** 1) + ((2*values[2]) ** 2) + ((2*values[3]) ** 3) + ((2*values[4]) ** 4) + ((2*values[5]) ** 5) + ((2*values[6]) ** 6) + ((2*values[7]) ** 7)
    
    
    for bank in MCP.Registers.get('IODIR'):
        if (MO1.status != False):
            MO1.set_byte(bank, 'OLAT', OutputsStates.get('MO1').get(bank)) #0xFF - hight state (relays ON)
            MO1.set_byte(bank, 'IODIR', 0x00) #0xFF - all directions as input

        if (MO2.status != False):
            MO2.set_byte(bank, 'OLAT', OutputsStates.get('MO2').get(bank)) #0xFF - hight state (relays ON)
            MO2.set_byte(bank, 'IODIR', 0x00) #0xFF - all directions as input
        



def myi2c_write(device, register, value):
    try:
        val = i2c.writeByte(device, register, value)
    except Exception as error_string:
        for name in MCP_list.keys():
            addr = MCP_list[name].addr
            if (addr == device):
                device_name = name
                
        print(str(datetime.datetime.now()) +  ' Error to write i2c: ' + device_name + ' ' + str(hex(device)) + ' register=' + str(hex(register)))
        msg='Error to write i2c: ' + device_name + ' ' + str(hex(device)) + ' register=' + str(hex(register))
        tologread(msg)
        logging.info(str(datetime.datetime.now()) + ' ' + msg)
        tozabbix("i2c_write_error", "1")
        # sys.exit()
        return False
    else:
        return val
    
def myi2c_read(device, register):
    try:
        val = i2c.readBytes(device, register, 1)
    except Exception as error_string:
        for name in MCP_list.keys():
            addr = MCP_list[name].addr
            if (addr == device):
                device_name = name
                
        print(str(datetime.datetime.now()) +  ' Error to read i2c: ' + device_name + ' ' + str(hex(device)) + ' register=' + str(hex(register)))
        msg='Error to read i2c: ' + device_name + ' ' + str(hex(device)) + ' register=' + str(hex(register))
        tologread(msg)
        logging.info(str(datetime.datetime.now()) + ' ' + msg)
        tozabbix("i2c_read_error", "1")
        # sys.exit()
        return 'False'
    else:
        return val[0]


class MyMQTTClass(mqtt.Client):
    rc_txt = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised"
    }

    def setPlaces(self, name, host, port, user, password, topic_header, subscribe_to_topic):
        self.BRname = name
        self.BRhost = str(host)
        self.BRport = str(port)
        self.BRuser = str(user)
        self.BRpassword = str(password)
        self.BRclient_id = str(self._client_id)
        self.BRtopic_header = str(topic_header)
        self.subscribe_to_topic = subscribe_to_topic
        self.connected_flag = False

    def BRinfo(self):
        tologread ("Connection data: {} ({}:{}), u={}, pass={}, client_id={}, topic_header={}, topic={}".format(self.BRname, self.BRhost, self.BRport, self.BRuser, self.BRpassword, self.BRclient_id, self.BRtopic_header, self.subscribe_to_topic))
        pass

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            self.connected_flag = False
            msg="Unexpected disconnection"
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)
            tozabbix("mqtt_disconnect", "1")

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0:
            tologread("Brocker=" + self.BRname + ", rc: " + str(rc) + " (" + self.rc_txt[rc] + ")")
            self.connected_flag=True

            topicall = self.BRtopic_header + self.subscribe_to_topic
            res = self.subscribe(topicall)
            if rc == mqtt.MQTT_ERR_SUCCESS:
                tologread("Successfully subscribed to topic: " + topicall)
                tozabbix("mqtt_disconnect", "0")
            else:
                msg="Error! Client is not subscribed to topic " + topicall
                tologread(msg)
                logging.info(str(datetime.datetime.now()) + ' ' + msg)
                tozabbix("mqtt_disconnect", "1")
        else:
            self.connected_flag = False
            tozabbix("mqtt_disconnect", "1")
            msg="Unexpected disconnection"
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)


    def on_message(self, mqttc, obj, msg):
        print("Brocker=" + self.BRname + ". Recieved msg: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        tologread("Brocker=" + self.BRname + ", topic=" + self.BRtopic_header + self.subscribe_to_topic + ", subscribed: mid=" + str(mid) + ", granted_qos=" + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        # print(string)
        # tologread("onlog: " + str(string))
        pass

    def bag_pub(self, topic, payload):
        if (self.connected_flag == True):
            # BRuser = "" if self.BRuser == "" else ", user=" + self.BRuser

            topic2 = self.BRtopic_header + topic

            (rc, mid) = self.publish(topic2, payload)
            if (rc != 0):
                self.connected_flag = False
                msg="Error to send mqtt. rc=" + str(rc) + ". " + str(self.rc_txt[rc]) + ". mid=" + str(mid)
                tologread(msg)
                logging.info(str(datetime.datetime.now()) + ' ' + msg)
                tozabbix("mqtt_pub_err", str(rc) + ": " + str(self.rc_txt[rc]))
            else:
                tologread ("Send mqtt: {}, t={}, msg={}".format(self.BRname, topic2, payload))
        else:
            tologread ("Scipped trying send mqtt because connected_flag = False")

    def run2(self):
        self.username_pw_set(username=self.BRuser,password=self.BRpassword)

        try:
            self.connect(self.BRhost, self.BRport, 60)
        except Exception as error_string:
            msg="Error to connect mqtt. {}. Broker={}".format(str(error_string), self.BRname)
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)
            tozabbix("mqtt_connect_error", 1)
            pass
        else:
            tozabbix("mqtt_connect_error", "0")

        self.loop_start()

    def exit(self):
        self.disconnect()
        self.loop_stop()


class Localnet_on_message(MyMQTTClass):
    def on_message(self, mqttc, obj, msg):
        # tologread("Recieved msg: {}, topic={}, brocker={}".format(str(msg.payload), msg.topic, self.BRname))

        msg01 = msg.topic.split('/command/')
        if (msg01):
            msg01 = str(msg01[1])
            if (len(msg01) == 0):
                if (msg.payload == 'getstates'):
                    msg = 'Recive request reley states'
                    tologread(msg)

                    MO1.get_states_and_send_mqtt('A')
                    MO1.get_states_and_send_mqtt('B')
                    MO2.get_states_and_send_mqtt('A')
                    MO2.get_states_and_send_mqtt('B')
                    
            if (len(msg01) == 7):
                msg01 = msg01.split('/')
                device_name = msg01[0]
                bank = msg01[1]
                pin_number = int(msg01[2])
                if (msg.payload == 'ON'):
                    value_on_pin = 1
                if (msg.payload == 'OFF'):
                    value_on_pin = 0
                if (msg.payload == '1'):
                    value_on_pin = 1
                if (msg.payload == '0'):
                    value_on_pin = 0
        
                msg = 'Recive request to change relay ' + device_name + bank + str(pin_number) + ' ' + msg.payload
                tologread(msg)
                MCP_list[device_name].ChangeRelayState(bank, pin_number, value_on_pin)

MQTTtopic_header = "BS/" + device_id + "/relays/"

localnet = Localnet_on_message(client_id=device_id)
localnet.setPlaces(
    name="localnet", 
    host=mqtt_credentials_from_file_dict.get("localnet").get("host"), 
    port=int(mqtt_credentials_from_file_dict.get("localnet").get("port")), 
    user=mqtt_credentials_from_file_dict.get("localnet").get("user"), 
    password=mqtt_credentials_from_file_dict.get("localnet").get("password"), 
    topic_header=MQTTtopic_header,
    subscribe_to_topic = "command/#")
localnet.BRinfo()
localnet.run2()


class MCP: # MCP23017
    Registers = dict(IODIR = dict(A=0x00, B=0x01), OLAT = dict(A=0x14, B=0x15), GPIO = dict(A=0x12, B=0x13), GPPU = dict(A=0x0C, B=0x0D), GPINTEN = dict(A=0x04, B=0x05), INTCON = dict(A=0x08, B=0x09), IOCON = dict(A=0x0A, B=0x0B), INTF = dict(A=0x0E, B=0x0F), DEFVAL = dict(A=0x06, B=0x07))

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.status = False
        self.statusAB = {
            "A" : False,
            "B" : False
        }

    def REGISTER(self, name):
        # return REGISTER_MAPPING[self.BANK]
        return 1

    def check_device(self):
        bank = "A"
        res = self.get_for_check_devices(bank, "GPPU")
        if (res != 'False'):
            self.statusAB[bank] = True
            tozabbix("mcp_error_" + self.name + bank, 0)
        else:
            self.statusAB[bank] = False
            msg="check_device says error! " + self.name + " " + bank
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)
            tozabbix("mcp_error_" + self.name + bank, 1)
        
        bank = "B"
        res = self.get_for_check_devices(bank, "GPPU")
        if (res != 'False'):
            self.statusAB[bank] = True
            tozabbix("mcp_error_" + self.name + bank, 0)
        else:
            self.statusAB[bank] = False
            msg="check_device says error! " + self.name + " " + bank
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)
            tozabbix("mcp_error_" + self.name + bank, 1)

        
        if (self.statusAB["A"] == True and self.statusAB["B"] == True):
            self.status = True
        else:
            self.status = False

        tologread("Device " + self.name + " addr=" + str(hex(self.addr)) + " statusAB[A]=" + str(self.statusAB["A"]) + " statusAB[B]=" + str(self.statusAB["B"]) + " status=" + str(self.status))

        return self.status

    def set_byte(self, bank_name, register_name, value):
        if (self.statusAB[bank_name] == True):
            val = myi2c_write(self.addr, self.Registers.get(register_name).get(bank_name), value)
            read_value = self.get_byte(bank_name, register_name)
            if read_value == value:
                return True
            else:
                tozabbix("mcp_set_byte_error", 1)
                msg="set_byte error! " + self.name + " " + bank_name
                tologread(msg)
                logging.info(str(datetime.datetime.now()) + ' ' + msg)
                return False
            return val
        else:
            tologread("Error! Write to " + self.name + " " + str(hex(self.addr)) + " register " + register_name + " " + str(hex(self.Registers.get(register_name).get(bank_name))) + " canceled, because status of bank " + bank_name + " set to error at the start of the program")
            return False


    def get_for_check_devices(self, bank_name, register_name):
        res = myi2c_read(self.addr, self.Registers.get(register_name).get(bank_name))
        return res

    def get_byte(self, bank_name, register_name):
        if (self.statusAB[bank_name] == True):
            res = myi2c_read(self.addr, self.Registers.get(register_name).get(bank_name))
            return res
        else:
            tologread("Error! Reading from " + self.name + " " + str(hex(self.addr)) + " register " + register_name + " " + str(hex(self.Registers.get(register_name).get(bank_name))) + " canceled, because status of bank " + bank_name + " set to error at the start of the program")
            return False

    def ChangeRelayState(self, bank_name, pin_number, value_on_pin):
        device_name = self.name
        GPIO_byte = self.get_byte(bank_name, "GPIO")
        GPIOstate = GPIO_byte
        
        if(value_on_pin == 0):
            GPIOnewstate = GPIOstate &~ (1 << (pin_number))
            
        if(value_on_pin == 1):
            GPIOstate |= 1 << (pin_number)
            GPIOnewstate = GPIOstate
        
        self.set_byte(bank_name, 'OLAT', GPIOnewstate)

        GPIO_byte = self.get_byte(bank_name, "GPIO")
        new_value_on_pin = int(GPIO_byte & (1 << pin_number) > 0)
        
        if (new_value_on_pin == value_on_pin):
            if (value_on_pin == 1):
                payload = 'ON'
            if (value_on_pin == 0):
                payload = 'OFF'

            msg = 'Relay ' + device_name + bank_name + str(pin_number) + ' successfully changed to ' + payload
            tologread(msg)
                
            topic = 'states/' + device_name + '/' + bank_name + '/' + str(pin_number)
            localnet.bag_pub(topic, payload)
        else:
            msg="ChangeRelayState ERROR! " + device_name + bank_name + str(pin_number) + " desired_val=" + str(value_on_pin)
            tologread(msg)
            logging.info(str(datetime.datetime.now()) + ' ' + msg)
            tozabbix("change_relay_state_error", 1)

    def get_states_and_send_mqtt(self, bank_name):
        if (localnet.connected_flag == True):
            GPIO = self.get_byte(bank_name, 'GPIO')
            
            for pin_number in [0,1,2,3,4,5,6,7]:
                value_on_pin = int(GPIO & (1 << pin_number) > 0)
                
                if (value_on_pin == 1):
                    payload = 'ON'
                if (value_on_pin == 0):
                    payload = 'OFF'
                
                topic = 'states/' + self.name + '/' + bank_name + '/' + str(pin_number)
                localnet.bag_pub(topic, payload)
        else:
            tologread("get_states_and_send_mqtt scipped because localnet.connected_flag = False")
                            

MO1 = MCP("MO1", 0x21)
MO2 = MCP("MO2", 0x22)
MI1 = MCP("MI1", 0x23)
MI2 = MCP("MI2", 0x24)
MB1 = MCP("MB1", 0x25)
MB2 = MCP("MB2", 0x26)
M_INT = MCP("M_INT", 0x27)

MCP_list = {'MO1' : MO1, 'MO2' : MO2, 'MI1' : MI1, 'MI2' : MI2, 'MB1' : MB1, 'MB2' : MB2, 'M_INT' : M_INT}

MO1.check_device()
MO2.check_device()
MI1.check_device()
MI2.check_device()
MB1.check_device()
MB2.check_device()
M_INT.check_device()

setup_MCPs()

MO1.get_states_and_send_mqtt('A')
MO1.get_states_and_send_mqtt('B')
MO2.get_states_and_send_mqtt('A')
MO2.get_states_and_send_mqtt('B')
# MI1.get_states_and_send_mqtt('A')
# MI1.get_states_and_send_mqtt('B')
# MI2.get_states_and_send_mqtt('A')
# MI2.get_states_and_send_mqtt('B')
# MB1.get_states_and_send_mqtt('A')
# MB1.get_states_and_send_mqtt('B')
# MB2.get_states_and_send_mqtt('A')
# MB2.get_states_and_send_mqtt('B')
# M_INT.get_states_and_send_mqtt('A')
# M_INT.get_states_and_send_mqtt('B')


try:
    while True:
        # a=a+1
        # print a
        # vdsina.bag_pub("D/BSR6/relays/test", "2")
        # print("connected_flag=" + str(vdsina.connected_flag))
        # if (vdsina.connected_flag == False):
        #     time.sleep(1)
        #     vdsina.run2()
        pass

except KeyboardInterrupt:
    print("Exiting by KeyboardInterrupt")
    tologread("Exiting by KeyboardInterrupt")
    localnet.exit()











