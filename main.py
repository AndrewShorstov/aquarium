from umqtt.robust import MQTTClient
from messageparser import MessageParser
import config


def main():
    mp = MessageParser(dict())
    mqtt = MQTTClient(config.CLIENT_ID, config.SERVER)
    mqtt.set_callback(mp.parse)
    mqtt.connect()
    mqtt.subscribe(config.TOPIC)
    try:
        while True:
            mqtt.wait_msg()
    finally:
        mqtt.disconnect()
    
if __name__ == "__main__":
    main()
    