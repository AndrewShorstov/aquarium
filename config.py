import ubinascii
import machine

## Alarm settings file
SETTINGS_FILE = "settings.json"

# Default MQTT server to connect to
SERVER = "192.168.1.100"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

TOP_TOPIC = b'aquarium'
TOPIC = b'/'.join((TOP_TOPIC, b'+'))
FEEDER_TOPIC = b'feeder'
LAMP_TOPIC = b'lamp'
ADD_ALARM_TOPIC = b'add_alarm'
DEL_ALARM_TOPIC = b'del_alarm'
ALARMS_TOPIC = b'alarms'
PUMP_TOPIC = b'pump'
STATUS_TOPIC = b'status'

LABELS = (b'feed', b'daylight', b'nightlight', b'offlight', b'status', b'pump_on', b'pump_off', b'show', b'save')
FEEDER_LABEL, DAYLIGHT_LABEL, NIGHTLIGHT_LABEL, OFFLIGHT_LABEL, STATUS_LABEL, PUMP_ON_LABEL, PUMP_OFF_LABEL, ALARMS_SHOW_LABEL, ALARMS_SAVE_LABEL = LABELS

## Feeder settings
FEEDER_SPEED = 1000
FEEDER_PINS = (32, 33, 25, 26)

## Led
LED_PIN = 2

## Lamp
LAMP_PINS = (22, 23)

## Pump
PUMP_PINS = (21, )

##
## Time worker settings
##
#Timezone Moscow - UTC+3
TIMEZONE = 3
# Period of syncing with NTP server in miliseconds
NTP_SYNC = 24*60*60*1000
# Period of checking of alarms
CHECK_ALARM = 30*1000

