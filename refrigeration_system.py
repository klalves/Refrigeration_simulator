import numpy as np
import matplotlib.pyplot as plt
import argparse

DELTA_AMBIENT_CONDENSER = 10
DELTA_CABINET_EVAP = 10

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24

COMPRESSOR_CONFIGS = {
    "EM2X3125U": {
        "power_base":4.3817710E+01,
        "power_N":0,
        "power_N2":0,
        "power_Tc":7.2250000E+00,
        "power_Tc2":-3.1875000E-02,
        "power_Te":-1.0023810E+00,
        "power_Te2":2.1428570E-03,
        "power_NTc":0,
        "power_NTe":0,
        "power_TcTe":1.1471430E-01,
        "cap_base":1307.635,
        "cap_N":0,
        "cap_N2":0,
        "cap_Tc":-10.0275,
        "cap_Tc2":-0.00875,
        "cap_Te":3.674702E+01,
        "cap_Te2":2.932143E-01,
        "cap_NTc":0,
        "cap_NTe":0,
        "cap_TcTe":-1.961429E-01
    },
    "VEMT406U": {
        "power_base": -2.1979500E+02,
        "power_N": 7.5982230E-02,
        "power_N2": 1.5065580E-06,
        "power_Tc": 7.0503120E+00,
        "power_Tc2": -4.5388890E-02,
        "power_Te": -3.6239470E+00,
        "power_Te2": -4.4393940E-03,
        "power_NTc": 2.8314120E-05,
        "power_NTe": 1.2972350E-03,
        "power_TcTe": 7.1033330E-02,
        "cap_base": 1.7837260E+02,
        "cap_N": 3.3139950E-01,
        "cap_N2": -5.1488730E-06,
        "cap_Tc": -2.1253380E+00,
        "cap_Tc2": -1.7722220E-02,
        "cap_Te": 1.8888690E+01,
        "cap_Te2": 2.0339390E-01,
        "cap_NTc": -1.9746320E-03,
        "cap_NTe": 4.4504770E-03,
        "cap_TcTe": -1.9982670E-01
    },
    "NT2180UV": {
        "power_base": 4.6173810E+02,
        "power_N": 0,
        "power_N2": 0,
        "power_Tc": 2.4728570E+01,
        "power_Tc2":-1.6285710E-01,
        "power_Te": 1.3143650E+01,
        "power_Te2": 1.3349210E-01,
        "power_NTc": 0,
        "power_NTe": 0,
        "power_TeTc": 2.4285710E-01,
        "cap_base": 3.635643E+03,
        "cap_N": 0,
        "cap_N2": 0,
        "cap_Tc": -2.261786E+01,
        "cap_Tc2": -8.785714E-02,
        "cap_Te": 1.077702E+02,
        "cap_Te2": 7.533333E-01,
        "cap_NTc": 0,
        "cap_NTe": 0,
        "cap_TeTc": -6.035714E-01
    },
    "FMFT213U": {
        "power_base": -4.2731630E+02,
        "power_N": 1.8293880E-01,
        "power_N2": -7.2509560E-06,
        "power_Tc": 1.4377700E+01,
        "power_Tc2": -1.0857140E-01,
        "power_Te": -5.1508460E+00,
        "power_Te2": -1.5901790E-01,
        "power_NTc": -3.6791980E-04,
        "power_NTe": 9.2011280E-04,
        "power_TeTc": 3.7875000E-02,
        "cap_base": 5.7151460E+02,
        "cap_N": 5.7762720E-01,
        "cap_N2": -2.4946030E-05,
        "cap_Tc": -5.4460000E-01,
        "cap_Tc2": -1.1848210E-01,
        "cap_Te": 4.2806580E+01,
        "cap_Te2": 1.3041670E-01,
        "cap_NTc": -3.2832360E-03,
        "cap_NTe": 4.3316620E-03,
        "cap_TeTc": -5.0403570E-01,
    },
    "NEU2168U": {
        "power_base": 4.2145240E+02,
        "power_N": 0,
        "power_N2": 0,
        "power_Tc": 1.5650000E+01,
        "power_Tc2": -9.0000000E-02,
        "power_Te": 7.0349210E+00,
        "power_Te2": 5.4126980E-02,
        "power_NTc": 0,
        "power_NTe": 0,
        "power_TeTc": 1.8714290E-01,
        "cap_base": 3.204098E+03,
        "cap_N": 0,
        "cap_N2": 0,
        "cap_Tc": -2.509464E+01,
        "cap_Tc2": 1.214286E-02,
        "cap_Te": 8.771528E+01,
        "cap_Te2": 5.960317E-01,
        "cap_NTc": 0,
        "cap_NTe": 0,
        "cap_TeTc": -4.546429E-01,
    },
    "EGAS70HLR": {
        "power_base": 1.2214290E+01,
        "power_N": 0,
        "power_N2": 0,
        "power_Tc": 4.5842860E+00,
        "power_Tc2": -2.5714290E-02,
        "power_Te": -6.7321430E-01,
        "power_Te2": 3.5714290E-04,
        "power_NTc": 0,
        "power_NTe": 0,
        "power_TeTc": 6.9357140E-02,
        "cap_base": 6.569732E+02,
        "cap_N": 0,
        "cap_N2": 0,
        "cap_Tc": -4.962857E+00,
        "cap_Tc2": 2.500000E-03,
        "cap_Te": 1.935357E+01,
        "cap_Te2": 1.350000E-01,
        "cap_NTc": 0,
        "cap_NTe": 0,
        "cap_TeTc": -9.442857E-02,
    },
    "EMX70CLC": {
        "power_base": 4.9196430E+01,
        "power_N": 0,
        "power_N2": 0,
        "power_Tc": 3.9228570E+00,
        "power_Tc2": -1.9285710E-02,
        "power_Te": 1.8595240E+00,
        "power_Te2": 2.8809520E-02,
        "power_NTc": 0,
        "power_NTe": 0,
        "power_TeTc": 5.1000000E-02,
        "cap_base": 7.467857E+02,
        "cap_N": 0,
        "cap_N2": 0,
        "cap_Tc": -5.522857E+00,
        "cap_Tc2": 2.857143E-03,
        "cap_Te": 2.270000E+01,
        "cap_Te2": 1.750000E-01,
        "cap_NTc": 0,
        "cap_NTe": 0,
        "cap_TeTc": -1.095714E-01,
    },
    "FMSA9C": {
        "power_base": -9.5426E+01,
        "power_N": 3.2079E-02,
        "power_N2": 2.8292E-07,
        "power_Tc": 3.1175E+00,
        "power_Tc2": -2.1964E-02,
        "power_Te": -1.7891E+00,
        "power_Te2": -7.5397E-04,
        "power_NTc": 2.4549E-05,
        "power_NTe": 6.2683E-04,
        "power_TeTc": 3.7054E-02,
        "cap_base": 1.2375E+02,
        "cap_N": 1.2073E-01,
        "cap_N2": -2.3825E-06,
        "cap_Tc": -1.3877E+00,
        "cap_Tc2": -5.7143E-03,
        "cap_Te": 1.0180E+01,
        "cap_Te2": 1.2782E-01,
        "cap_NTc": -5.5796E-04,
        "cap_NTe": 1.8157E-03,
        "cap_TeTc": -8.4911E-02,
    },
}

SYSTEM_CONFIGS = {
    "house_refrigerator": {
        "setpoint_1": -18,
        "hysteresis_1": 2,
        "setpoint_2": 4,
        "hysteresis_2": 2,
        "Kp": 2000,
        "Ki": 15,
        "stab_time": 240,
        "compressor": "EMX70CLC",
        "mass": {
            "ambient": 10000,
            "cabinet_1": 0.1,
            "cabinet_2": 0.5,
            "food_1": 0.01,
            "food_2": 0.01
        },
        "default_mass": {
            "food_1": 0.01,
            "food_2": 0.01
        }
    },
    "vertical_freezer": {
        "setpoint_1": -20,
        "hysteresis_1": 2,
        "setpoint_2": 4,
        "hysteresis_2": 2,
        "Kp": 1500,
        "Ki": 1,
        "stab_time": 240,
        "compressor": "EGAS70HLR",
        "mass": {
            "ambient": 10000,
            "cabinet_1": 0.1,
            "food_1": 0.01,
            "cabinet_2": 0.0,
            "food_2": 0.0,
        },
        "default_mass": {
            "food_1": 0.01,
            "food_2": 0.0,
        }
    },
    "bottle_cooler": {
        "setpoint_1": 4,
        "hysteresis_1": 2,
        "setpoint_2": 4,
        "hysteresis_2": 2,
        "Kp": 1400,
        "Ki": 5,
        "stab_time": 60,
        "heat_capacity_rate_base":{
            "cabinet_1_to_ambient" : 13,
            "cabinet_2_to_ambient" : 13,
        },
        "compressor": "EM2X3125U",
        "mass": {
            "ambient": 10000,
            "cabinet_1": 500,
            "food_1": 10,
            "cabinet_2": 0,
            "food_2": 0,
        },
        "default_mass": {
            "food_1": 10,
            "food_2": 0,
        }
    }
}


# Then use these constants in the code, e.g.:


parser = argparse.ArgumentParser(description='Refrigeration simulator')

parser.add_argument('--system', choices=['house_refrigerator', 'frozen_island', 'bottle_cooler', 'vertical_freezer', 'medical'], required=True)
parser.add_argument('--control', choices=['ON_OFF', 'VCC'], required=True)

class RefrigerationSystem:
 
    def __init__(self, system_type, control_type):
        #Constants
        self.define_system_type(system_type)
        
        if (control_type == "ON_OFF" or control_type == "VCC"):
            self.control_type = control_type
        else:
            raise Exception("Invalid control type: " + str(control_type))
        
        self.p=0
        self.i=0

        #Initial state
        self.temperature = {}
        self.temperature["ambient"] = 25
        self.temperature["cabinet_1"] = self.sys_config["setpoint_1"] + self.sys_config["hysteresis_1"]
        self.temperature["cabinet_2"] = self.sys_config["setpoint_2"] + self.sys_config["hysteresis_2"]
        self.temperature["food_1"] = self.temperature["cabinet_1"]
        self.temperature["food_2"] = self.temperature["cabinet_2"]
        self.temperature["cond"] = self.temperature["ambient"] + DELTA_AMBIENT_CONDENSER
        self.temperature["evap"] = self.temperature["cabinet_1"] - DELTA_CABINET_EVAP
        
        self.voltage_fault_state = False
        self.voltage_fault_duration_s = 0
        self.voltage_fault_duration_trigger_s = 60

        #Static variables
        self.time_below_setpoint_s = 0
        self.vcc_is_active = 0

        #Control actions
        self.compressor_speed = 0
        self.cabinet_1_door_is_open = False
        self.cabinet_2_door_is_open = False
        self.damper_action = 0

        #Powers
        self.power = {}
        self.capacity = {}
        self.power["compressor"] = 0
        self.capacity["compressor"] = 0

        # Specific heat measured in J/(Kg*K) 
        self.specific_heat = {}
        self.specific_heat["ambient"] = 1500
        self.specific_heat["cabinet_1"] = 1500
        self.specific_heat["cabinet_2"] = 1500
        self.specific_heat["food_1"] = 4184
        self.specific_heat["food_2"] = 4184
        
        # Heat capacity rates (thermal coupling) measured in W/K 
        self.heat_capacity_rate = {}
        self.calculate_heat_capacity_rates()

    def define_system_type(self, system_type):
        if system_type not in SYSTEM_CONFIGS:
            raise ValueError(f"Invalid system type: {system_type}")

        self.system_type = system_type
        config = SYSTEM_CONFIGS[system_type]
        self.sys_config = SYSTEM_CONFIGS[system_type]
        self.comp_param = COMPRESSOR_CONFIGS[config["compressor"]]

        self.max_speed = 4500
        self.min_speed = 1400
        self.on_off_speed = 3600

        if(self.sys_config["Ki"] > 0):
            self.integral_error = (self.max_speed-self.min_speed)/self.sys_config["Ki"]
        else:
            self.integral_error = 0


    def add_food(self, temperature, compartment = 1):
        if(compartment == 1):
            self.sys_config["mass"]["food_1"] = self.sys_config["default_mass"]["food_1"]
            self.temperature["food_1"] = temperature
        elif(compartment == 2):
            self.sys_config["mass"]["food_2"] = self.sys_config["default_mass"]["food_2"]
            self.temperature["food_2"] = temperature
    
    def remove_food(self, compartment = 1):
        if(compartment == 1):
            self.sys_config["mass"]["food_1"] = 0
            self.temperature["food_1"] = 0
        elif(compartment == 2):
            self.sys_config["mass"]["food_2"] = 0
            self.temperature["food_2"] = 0
    
    def on_off_control(self):
        if self.temperature["cabinet_1"] < self.sys_config["setpoint_1"]:
            self.compressor_speed = 0
        elif self.temperature["cabinet_1"] > self.sys_config["setpoint_1"] + self.sys_config["hysteresis_1"]:
            self.compressor_speed = self.on_off_speed

        if self.temperature["cabinet_2"] < self.sys_config["setpoint_2"]:
            self.damper_action = 0
        elif self.temperature["cabinet_2"] > self.sys_config["setpoint_2"] + self.sys_config["hysteresis_2"]:
            self.damper_action = 1

    def vcc_control(self, time_step_s):
        if self.vcc_is_active:
            self.cycle_duration_s += time_step_s

            error = self.temperature["cabinet_1"] - self.sys_config["setpoint_1"]

            self.integral_error += error

            if(self.integral_error*self.sys_config["Ki"] > self.max_speed-self.min_speed):
                self.integral_error = (self.max_speed-self.min_speed)/self.sys_config["Ki"]
            elif self.integral_error < 0:
                self.integral_error = 0

            p_component = self.sys_config["Kp"]*error
            i_component = self.sys_config["Ki"]*self.integral_error

            self.p = p_component
            self.i = i_component

            self.compressor_speed = self.min_speed + p_component + i_component

            if(self.compressor_speed > self.max_speed):
                self.compressor_speed = self.max_speed
            elif(self.compressor_speed < self.min_speed):
                self.compressor_speed = self.min_speed

            if self.temperature["cabinet_1"] < self.sys_config["setpoint_1"] + 0.05:
                self.time_below_setpoint_s += time_step_s
                if self.time_below_setpoint_s > self.sys_config["stab_time"]*60:
                    self.vcc_is_active = 0
        else:
            self.time_below_setpoint_s = 0
            self.compressor_speed = 0
            self.cycle_duration_s = 0
            self.integral_error = 0
            
            if self.temperature["cabinet_1"] > self.sys_config["setpoint_1"] + self.sys_config["hysteresis_1"]:
                self.vcc_is_active = 1
            
        if self.temperature["cabinet_2"] < self.sys_config["setpoint_2"]:
            self.damper_action = 0
        elif self.temperature["cabinet_2"] > self.sys_config["setpoint_2"] + self.sys_config["hysteresis_2"]:
            self.damper_action = 1
    
    def calculate_power_and_capacity(self):
        if(self.compressor_speed > 0):
            self.power["compressor"] = self.comp_param["power_base"] + \
                                       self.comp_param["power_N"] * self.compressor_speed + \
                                       self.comp_param["power_N2"] * self.compressor_speed * self.compressor_speed + \
                                       self.comp_param["power_Tc"] * self.temperature["cond"] + \
                                       self.comp_param["power_Tc2"] * self.temperature["cond"] * self.temperature["cond"] + \
                                       self.comp_param["power_Te"] * self.temperature["evap"] + \
                                       self.comp_param["power_Te2"] * self.temperature["evap"] * self.temperature["evap"] + \
                                       self.comp_param["power_NTc"] * self.compressor_speed * self.temperature["cond"] + \
                                       self.comp_param["power_NTe"] * self.compressor_speed * self.temperature["evap"] + \
                                       self.comp_param["power_TcTe"] * self.temperature["cond"] * self.temperature["evap"]
            if(self.power["compressor"] < 0):
                self.power["compressor"] = 0
            self.capacity["compressor"] = self.comp_param["cap_base"] + \
                                          self.comp_param["cap_N"] * self.compressor_speed + \
                                          self.comp_param["cap_N2"] * self.compressor_speed * self.compressor_speed + \
                                          self.comp_param["cap_Tc"] * self.temperature["cond"] + \
                                          self.comp_param["cap_Tc2"] * self.temperature["cond"] * self.temperature["cond"] + \
                                          self.comp_param["cap_Te"] * self.temperature["evap"] + \
                                          self.comp_param["cap_Te2"] * self.temperature["evap"] * self.temperature["evap"] + \
                                          self.comp_param["cap_NTc"] * self.compressor_speed * self.temperature["cond"] + \
                                          self.comp_param["cap_NTe"] * self.compressor_speed * self.temperature["evap"] + \
                                          self.comp_param["cap_TcTe"] * self.temperature["cond"] * self.temperature["evap"]
            if(self.capacity["compressor"] < 0):
                self.capacity["compressor"] = 0
            if(self.control_type == "VCC"):
                self.power["compressor"] = self.compressor_speed*self.power["compressor"]/self.on_off_speed
                self.capacity["compressor"] = self.compressor_speed*self.capacity["compressor"]/self.on_off_speed
        else:
            self.power["compressor"] = 0
            self.capacity["compressor"] = 0 
    
    def calculate_heat_capacity_rates(self):
        # Heat capacity rates (thermal coupling) measured in W/K
        self.heat_capacity_rate[self.coupling_key("cabinet_1", "cabinet_2")] = self.damper_action * 0.025
        self.heat_capacity_rate[self.coupling_key("cabinet_1", "ambient")] = self.sys_config["heat_capacity_rate_base"]["cabinet_1_to_ambient"] + (self.cabinet_1_door_is_open * 0.005)
        self.heat_capacity_rate[self.coupling_key("cabinet_2", "ambient")] = self.sys_config["heat_capacity_rate_base"]["cabinet_2_to_ambient"] + (self.cabinet_2_door_is_open * 0.05)
        self.heat_capacity_rate[self.coupling_key("cabinet_1", "food_1")] = 1
        self.heat_capacity_rate[self.coupling_key("cabinet_2", "food_2")] = 1

    def simulate(self, time_step_s):

        if(self.control_type == "ON_OFF"):
            self.on_off_control()
            if(self.voltage_fault_state):
                self.voltage_fault_duration_s += time_step_s
            else:
                self.voltage_fault_duration_s = 0
            if(self.voltage_fault_duration_s > self.voltage_fault_duration_trigger_s):
                self.compressor_speed = 0

        elif(self.control_type == "VCC"):
            self.vcc_control(time_step_s)
        else:
            self.compressor_speed = 0
            self.damper_action = 0

        self.calculate_power_and_capacity()
        self.calculate_heat_capacity_rates()

        #Energy variation
        delta_energy = {}
        delta_energy["ambient"] = 0
        delta_energy["cabinet_1"] = time_step_s * \
                                      (self.heat_transfer_rate_get("ambient", "cabinet_1")  + \
                                       ((self.sys_config["mass"]["food_1"] > 0) * self.heat_transfer_rate_get("food_1", "cabinet_1"))   - \
                                       (self.capacity["compressor"]))
        delta_energy["cabinet_2"] = time_step_s * \
                                      (self.heat_transfer_rate_get("ambient", "cabinet_2")  + \
                                       self.heat_transfer_rate_get("cabinet_1", "cabinet_2") + \
                                       ((self.sys_config["mass"]["food_2"] > 0) * self.heat_transfer_rate_get("food_2", "cabinet_2")))
        delta_energy["food_1"] = time_step_s * self.heat_transfer_rate_get("cabinet_1", "food_1")
        delta_energy["food_2"] = time_step_s * self.heat_transfer_rate_get("cabinet_2", "food_2")

        #Apply timestep
        for key in self.temperature:
            if(key == "cond"):
                self.temperature[key] = self.temperature["ambient"] + DELTA_AMBIENT_CONDENSER
            elif(key == "evap"):
                self.temperature[key] = self.temperature["cabinet_1"] - DELTA_CABINET_EVAP
            elif(self.sys_config["mass"][key] != 0):
                self.temperature[key] += delta_energy[key]/(self.sys_config["mass"][key] * self.specific_heat[key])

    def heat_transfer_rate_get(self, body1, body2):
        delta_temperature = self.temperature[body1] - self.temperature[body2]
        return delta_temperature*self.heat_capacity_rate[self.coupling_key(body1, body2)]


    
    def coupling_key(self, str1, str2):
        return tuple(sorted((str1, str2)))



# Example usage:
if __name__ == "__main__":

    args = vars(parser.parse_args())

    system = args['system']
    control = args['control']

    simulator = RefrigerationSystem(system, control)

    time_step = SECONDS_PER_MINUTE  # Time step for simulation (in seconds)
    total_time = SECONDS_PER_MINUTE * MINUTES_PER_HOUR * HOURS_PER_DAY * 5
    num_steps = int(total_time / time_step)

    # Initialize the data arrays
    t_ambient = np.zeros(num_steps)
    t_cabinet_1 = np.zeros(num_steps)
    t_food_1 = np.zeros(num_steps)
    if(system == "house_refrigerator"):
        t_cabinet_2 = np.zeros(num_steps)
        t_food_2 = np.zeros(num_steps)
    t_speed = np.zeros(num_steps)
    t_reference = np.zeros(num_steps)
    t_p = np.zeros(num_steps)
    t_i = np.zeros(num_steps)
    t_power = np.zeros(num_steps)
    t_capacity = np.zeros(num_steps)

    simulator.remove_food()
    simulator.remove_food(2)

    simulator.add_food(simulator.sys_config["setpoint_1"])

    # Simulate heat transfer for 100 time steps
    for i in range(num_steps):
        simulator.simulate(time_step)
        t_ambient[i] = simulator.temperature["ambient"]
        t_cabinet_1[i] = simulator.temperature["cabinet_1"]
        t_food_1[i] = simulator.temperature["food_1"]
        if(system == "house_refrigerator"):
            t_cabinet_2[i] = simulator.temperature["cabinet_2"]
            t_food_2[i] = simulator.temperature["food_2"]

        t_speed[i] = simulator.compressor_speed/100
        t_power[i] = simulator.power["compressor"]/100
        t_capacity[i] = simulator.capacity["compressor"]/100

#VCC and ON_OFF wil be handled as two instances of RefrigerationSystem
#Outputs:
#TODO: Add method for RPM retrieval
#TODO: Add method for KWh/day retrieval (EC_daily)
#TODO: Add method for Main cabinet temperature retrieval
#TODO: Add method for Main cabinet food temperature retrieval
#TODO: Add method for Secondary cabinet temperature retrieval
#TODO: Add method for Secondary cabinet food temperature retrieval
#Inputs
#TODO: Add method to set voltage fault state ON/OFF
#TODO: Add method to set ambient temperature
#TODO: Add method to add food to Main cabinet
#TODO: Add method to add food to Secondary cabinet
#TODO: Add method to remove food to Main cabinet
#TODO: Add method to remove food to Secondary cabinet
#Yearly energy consumption: (EC_daily_ON_OFF - EC_daily_VCC)*365

        t_reference[i] = simulator.sys_config["setpoint_1"]

        if(control == "VCC"):
            t_p[i] = simulator.p/100
            t_i[i] = simulator.i/100

        if False:

            if(i == 60*12):
                simulator.add_food(25)

            if(i == 60*24):
                simulator.voltage_fault_state = True
            if(i == 60*26):
                simulator.voltage_fault_state = False

            if(i == 60*36):
                simulator.add_food(25,2)

            if(i == 60*49):
                simulator.cabinet_1_door_is_open = True
            if(i == 60*50):
                simulator.cabinet_1_door_is_open = False

            if(i == 60*59):
                simulator.cabinet_2_door_is_open = True
            if(i == 60*60):
                simulator.cabinet_2_door_is_open = False



    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(t_ambient, label='Ambient')
    plt.plot(t_cabinet_1, label='Cabinet 1')
    plt.plot(t_food_1, label='Food 1')
    if(system == "house_refrigerator"):
        plt.plot(t_cabinet_2, label='Cabinet 2')
        plt.plot(t_food_2, label='Food 2')
    plt.plot(t_speed, label='Speed/100')
    plt.plot(t_power, label='Power/100')
    plt.plot(t_capacity, label='Capacity/100')
    plt.plot(t_reference, label='Reference')
    if(control == "VCC"):
        plt.plot(t_p, label='p_component/100')
        plt.plot(t_i, label='i_component/100')
    plt.title('Simulation of Refrigeration System')
    plt.xlabel('Minutes')
    plt.ylabel('Value')
    plt.legend()
    plt.show()