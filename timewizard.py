import ntptime
import utime
import machine
import config

class TimeWizard:
    def __init__(self):
        self._rtc = machine.RTC()
        self._timer = machine.Timer(-1)
        self._alarms = dict()
        self._last_alarm = dict()
        self._last_hour = 0
        self._synced = False
        self.sync()
    
    
    def time(self):
        _, _, _, _, hours, minutes, _, _ = self._rtc.datetime()
        return ((hours + config.TIMEZONE)%24, minutes)
    
    
    def add_alarm(self, hour, minute, label, callback):
        time = hour*60+minute
        if time not in self._alarms:
            self._alarms[time] = dict()
        self._alarms[time][label] = {'hour': hour, 'minute': minute, 'cb': callback, 'done':False}
        print("Alarm for {:s} at {:02}:{:02} has been added".format(label, hour, minute))
    
    
    def del_alarm(self, hour, minute, label, callback=None):
        time = hour*60+minute
        if time in self._alarms and label in self._alarms[time]:
            del self._alarms[label][time]
            if self._alarms[time].isEmpty:
                del self._alarms[time]
            print("Alarm for {:s} at {:02}:{:02} has been removed".format(label, hour, minute))
    

    def get_alarms(self):
        alarms = []
        for time, item in self._alarms.items():
            for label, context in item.items():
                alarms.append((context['hour'], context['minute'], label))
        return alarms


    def sync(self):
        try:
            ntptime.settime()
            self._synced = True
            print("Sync RTC {}".format(self._rtc.datetime()))
        except OSError:
            print("Error during syncing")
    
    
    def stop(self):
        self._timer.deinit()
    
    
    def start(self, sync_period=config.NTP_SYNC, check_period=config.CHECK_ALARM):
        self._last_hour, _ = self.time()
        self._timer.init(period=sync_period, mode=machine.Timer.PERIODIC, callback=self.sync)
        self._timer.init(period=check_period, mode=machine.Timer.PERIODIC, callback=self._check_alarms)


    def get_last(self, label):
        if label in self._last_alarm:
            return self._last_alarm[label]
        return None

          
    def _check_alarms(self, t):
        if not self._synced:
            print("Trying to sync ...")
            self.sync()
            return
        hour, minute = self.time()
        time = hour*60 + minute
        if time in self._alarms:
            for label, context in self._alarms[time].items():
                if not context['done']:
                    print("{:s} at {:02}:{:02}".format(label, context["hour"], context["minute"]))
                    context['cb']()
                    self._last_alarm[label] = (hour, minute)
                    self._alarms[time][label]['done'] = True
        
        if hour == 0 and self._last_hour == 23:
            for time, item in self._alarms.items():
                for label in item:
                    self._alarms[time][label]['done'] = False
        self._last_hour = hour
                    
                
            
        
        