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
        self._set_missed = False
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
            del self._alarms[time][label]
            if len(self._alarms[time]) == 0:
                del self._alarms[time]
            print("Alarm for {:s} at {:02}:{:02} has been removed".format(label, hour, minute))
    

    def get_alarms(self):
        alarms = []
        for time, item in self._alarms.items():
            for label, context in item.items():
                alarms.append((context['hour'], context['minute'], label))
        return alarms


    def synced(self):
        return self._synced


    def sync(self):
        try:
            ntptime.settime()
            self._synced = True
            print("Sync RTC {}".format(self._rtc.datetime()))
        except OSError:
            print("Error during syncing")
    
    
    def _set_missed_alarms(self):
        min_time = {config.DAYLIGHT_LABEL:None, config.NIGHTLIGHT_LABEL: None, config.PUMP_ON_LABEL: None}
        current_hour, current_minute = self.time()
        current_time = current_hour*60 + current_minute
        for time, actions in self._alarms.items():
            print(actions)
            if config.DAYLIGHT_LABEL in actions:
                if min_time[config.DAYLIGHT_LABEL] is None:
                    min_time[config.DAYLIGHT_LABEL] = time
                    continue
                min_time[config.DAYLIGHT_LABEL] = self._min_dist(current_time, time, min_time[config.DAYLIGHT_LABEL])
            if config.NIGHTLIGHT_LABEL in actions:
                if min_time[config.NIGHTLIGHT_LABEL] is None:
                    min_time[config.NIGHTLIGHT_LABEL] = time
                    continue
                min_time[config.NIGHTLIGHT_LABEL] = self._min_dist(current_time, time, min_time[config.NIGHTLIGHT_LABEL])
            if config.PUMP_ON_LABEL in actions:
                if min_time[config.PUMP_ON_LABEL] is None:
                    min_time[config.PUMP_ON_LABEL] = time
                    continue
                min_time[config.PUMP_ON_LABEL] = self._min_dist(current_time, time, min_time[config.PUMP_ON_LABEL])
        print(min_time)
        for label, time in min_time.items():
            if time is not None:
                self._alarms[time][label]["cb"]() 
        self._set_missed = True
                
                
    def _min_dist(self, current, new, old):
        day = 24*60
        old_dist = (day + current - old)%day
        new_dist = (day + current - new)%day
        if new_dist < old_dist:
            return new
        else:
            return old
    
    
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
#         if self._synced and not self._set_missed:
#             self._set_missed_alarms()

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
                    
                
            
        
        