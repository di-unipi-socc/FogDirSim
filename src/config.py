# Setting profile (mean, deviation) given type
profile_low = (70, 5)
profile_normal = (80, 10)
profile_high = (90, 10)

# Functions determining energy consumption for every device
energy_consumption = {}
# energy_consumption[deviceId] = (lambda cpu_usage, mem_usage: return cpu_usage, mem_usage)
energy_consumption["1"] = (lambda cpu_usage, mem_usage: cpu_usage+mem_usage)

def device2_energy(cpu_usage, mem_usage):
    return 2*cpu_usage+mem_usage
energy_consumption["2"] = device2_energy
energy_consumption["3"] = (lambda *args: 100)

def getEnergyConsumed(deviceId, cpu_usage, mem_usage):
    try:
        fun = energy_consumption[str(deviceId)]
        return fun(cpu_usage, mem_usage)
    except KeyError:
        return cpu_usage+mem_usage