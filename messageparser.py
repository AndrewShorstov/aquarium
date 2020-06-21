import config
from stepper import Stepper
from timewizard import TimeWizard
from lamp import Lamp
from pump import Pump
import ujson

#                       send               answer
# aquarium/feeder       feed, 1000
# aquarium/add_alarm    15:10, feed
# aquarium/del_alarm    15:20, daylight
# aquarium/alarms       show               15:10,feed; 15:20, daylight; 15:30, nightlight; 15:40, offlight
#                       save
# aquarium/lamp         daylight or nightlight or offlight
# aquarium/pump         pump_on, pump_off
# aquarium/status       daylight, last feed at 15:20

class MessageParser:
    def __init__(self, settings):
        self._settings = settings
        self._feeder = Stepper(*config.FEEDER_PINS)    
        self._feeder.setSpeed(config.FEEDER_SPEED)
        self._tw = TimeWizard()
        self._lamp = Lamp(*config.LAMP_PINS)
        self._pump = Pump(*config.PUMP_PINS)
        self._alarm_actions = {
            config.FEEDER_LABEL: self._feeder.fullRound,
            config.DAYLIGHT_LABEL: self._lamp.daylight,
            config.NIGHTLIGHT_LABEL: self._lamp.nightlight,
            config.OFFLIGHT_LABEL: self._lamp.offlight,
            config.PUMP_ON_LABEL: self._pump.on,
            config.PUMP_OFF_LABEL: self._pump.off,
            config.ALARMS_SHOW_LABEL: self._show_alarms,
            config.ALARMS_SAVE_LABEL: self._save_alarms
            }
        self._funcs = {
            b'/'.join((config.TOP_TOPIC, config.FEEDER_TOPIC)): self.feed,
            b'/'.join((config.TOP_TOPIC, config.ADD_ALARM_TOPIC)): self.add_alarm,
            b'/'.join((config.TOP_TOPIC, config.DEL_ALARM_TOPIC)): self.del_alarm,
            b'/'.join((config.TOP_TOPIC, config.ALARMS_TOPIC)): self.alarms,
            b'/'.join((config.TOP_TOPIC, config.LAMP_TOPIC)): self.set_lamp,
            b'/'.join((config.TOP_TOPIC, config.STATUS_TOPIC)): self.get_status,
            b'/'.join((config.TOP_TOPIC, config.PUMP_TOPIC)): self.set_pump,
            }
        self._load_alarms()
        self._tw.start()
        
        
    def parse(self, topic, msg):
        if topic in self._funcs:
            self._funcs[topic](msg)
        

    def feed(self, msg):
        args = msg.split(b',')
        if args[0] == config.FEEDER_LABEL:
            if len(args) > 1:
                try:
                    new_speed = int(args[1])
                except ValueError:
                    new_speed = config.FEEDER_SPEED
                self._feeder.setSpeed(new_speed)
            self._feeder.fullRound()
  
  
    def set_lamp(self, msg):
        if msg in (config.DAYLIGHT_LABEL, config.NIGHTLIGHT_LABEL, config.OFFLIGHT_LABEL):
            self._alarm_actions[msg]()
    
    
    def set_pump(self, msg):
        if msg in (config.PUMP_ON_LABEL, config.PUMP_OFF_LABEL):
            self._alarm_actions[msg]()
    
    def get_status(self, msg):
        time = self._tw.get_last(config.FEEDER_LABEL)
        if time is None:
            print("{:s}, {:s}".format(self._lamp.status(), self._pump.status()))
        else:
            print("{:s}, {:s}, last feed at {:02}:{:02}".format(self._lamp.status(), self._pump.status(), *time))


    def add_alarm(self, msg):
        args = self._prepare_timer_args(msg)
        if args is None:
            print('Incorrect time string {:s}'.format(msg))
            return
        hour, minute, label, _ = args
        self._tw.add_alarm(*args)
    
    
    def del_alarm(self, msg):
        args = self._prepare_timer_args(msg)
        if args is None:
            print('Incorrect time string {:s}'.format(msg))
            return
        hour, minute, label, _ = args
        self._tw.del_alarm(*args)
    
    
    def alarms(self, msg):
        if msg in (config.ALARMS_SHOW_LABEL, config.ALARMS_SAVE_LABEL):
            self._alarm_actions[msg]()
    
    
    def _show_alarms(self):
        alarms = self._tw.get_alarms()
        print( b'; '.join((b'{:02}:{:02}, {:s}'.format(*alarm) for alarm in alarms)))
    
    
    def _save_alarms(self):
        alarms = self._tw.get_alarms()
        data = [(hour, minute, label.decode('utf-8')) for hour, minute, label in alarms]
        with open(config.SETTINGS_FILE, 'w') as f:
            ujson.dump(data, f)
        print("Settings is saved")
    
    def _load_alarms(self):
        with open(config.SETTINGS_FILE, 'r') as f:
            data = ujson.load(f)
        
        for item in data:
            hour, minute, label = item
            self._tw.add_alarm(hour, minute, label.encode('utf-8'), self._alarm_actions[label.encode('utf-8')])
    

    def _prepare_timer_args(self, msg):
        args = msg.split(b',')
        if len(args) == 2:
            time = self._extract_time(args[0])
            if time is not None:
                hour, minute = time
                label = args[1].strip()
                if label in config.LABELS and label != config.STATUS_LABEL:
                    return (hour, minute, label, self._alarm_actions[label])
        return None


    def _extract_time(self, time):
        args = time.split(b':')
        if len(args) == 2:
            time_is_correct = False
            try:
                hour = int(args[0])
                minute = int(args[1])
                time_is_correct = True
            except ValueError:
                time_is_correct = False
        if time_is_correct and (0 <= hour <= 23) and (0 <= minute <= 59):
            return (hour, minute)
        else:
            return None
        
