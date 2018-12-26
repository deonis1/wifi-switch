from wifi_switch import wifi_switch
try:
    wifi_switch()
except OSError:
    import machine
    machine.reset()
    pass
    
