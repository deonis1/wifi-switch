from wifi_switch import HttServ
try:
    HttServ()
except OSError:
    import machine
    machine.reset()
    pass
    
