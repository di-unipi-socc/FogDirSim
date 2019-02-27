SAMPLE_INTERVAL = 8

# Setting profile (mean, deviation) given type
profile_low = (0.5, 0.05)
profile_normal = (0.7, 0.07)
profile_high = (0.9, 0.1)

# Functions determining energy consumption for every device
energy_consumption = {}
# energy_consumption[deviceId] = (lambda cpu_usage, mem_usage: return cpu_usage, mem_usage)
#energy_consumption["1"] = (lambda cpu_usage, mem_usage: cpu_usage+mem_usage)

def large_devs(cpu_usage, mem_usage):
    if cpu_usage < 425:
        return 7
    if cpu_usage < 850:
        return 12
    if cpu_usage < 1275:
        return 20
    return 30
def medium_devs(cpu_usage, mem_usage):
    if cpu_usage < 425:
        return 6
    if cpu_usage < 850:
        return 10
    if cpu_usage < 1275:
        return 20
    return 25

for i in range(1, 6):
    energy_consumption[str(i)] = large_devs
for i in range(6, 11):
    energy_consumption[str(i)] = medium_devs
#energy_consumption["3"] = (lambda *args: 100)

# Costo medie energia: 0,25€/kW

def getEnergyConsumed(deviceId, cpu_usage, mem_usage):
    try:
        fun = energy_consumption[str(deviceId)]
        return fun(cpu_usage, mem_usage)
    except KeyError:
        val = 0
        if cpu_usage < 425:
            val = 5
        elif cpu_usage < 850:
            val = 10
        elif cpu_usage < 1275:
            val = 18
        else:
            val = 25
        return val