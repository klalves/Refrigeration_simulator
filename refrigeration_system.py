import numpy as np
import matplotlib.pyplot as plt
import argparse

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

        #Initial state
        self.temperature = {}
        self.temperature["ambient"] = 25
        self.temperature["cabinet_1"] = self.setpoint_1 + self.hysteresis_1
        self.temperature["cabinet_2"] = self.setpoint_2 + self.hysteresis_2
        self.temperature["food_1"] = self.temperature["cabinet_1"]
        self.temperature["food_2"] = self.temperature["cabinet_2"]
        
        self.voltage_fault_state = False
        self.voltage_fault_duration_s = 0
        self.voltage_fault_duration_trigger_s = 60

        #Static variables
        self.time_below_setpoint_s = 0
        self.vcc_is_active = 0

        #Control actions
        self.compressor_speed = 0
        self.cabinet_1_door_state = 0
        self.cabinet_2_door_state = 0
        self.damper_action = 0

        #Powers
        self.power = {}
        self.power["compressor"] = 0

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
        if(system_type == "house_refrigerator"):
            self.setpoint_1 = -18
            self.hysteresis_1 = 2
            self.setpoint_2 = 4
            self.hysteresis_2 = 2
            self.Kp = 1000
            self.Ki = 1
            self.stab_time = 240

            self.compressor_max_power = 250

            self.mass = {}
            self.mass["ambient"] = 10000
            self.mass["cabinet_1"] = 0.1
            self.mass["cabinet_2"] = 0.5
            self.mass["food_1"] = 5.0
            self.mass["food_2"] = 5.0
        elif(system_type == "vertical_freezer"):
            self.setpoint_1 = -20
            self.hysteresis_1 = 2
            self.setpoint_2 = 4
            self.hysteresis_2 = 2
            self.Kp = 800
            self.Ki = 1
            self.stab_time = 120

            self.compressor_max_power = 350

            self.mass = {}
            self.mass["ambient"] = 10000
            self.mass["cabinet_1"] = 0.5
            self.mass["cabinet_2"] = 0
            self.mass["food_1"] = 20.0
            self.mass["food_2"] = 0
        else:
            raise Exception("Invalid system type: " + str(system_type))
        
        self.max_speed = 4500
        self.min_speed = 1200
        if(self.Ki > 0):
            self.integral_error = (self.max_speed-self.min_speed)/self.Ki
        else:
            self.integral_error = 0
        
    def on_off_control(self):
        if self.temperature["cabinet_1"] < self.setpoint_1:
            self.compressor_speed = 0
        elif self.temperature["cabinet_1"] > self.setpoint_1 + self.hysteresis_1:
            self.compressor_speed = self.max_speed

        if self.temperature["cabinet_2"] < self.setpoint_2:
            self.damper_action = 0
        elif self.temperature["cabinet_2"] > self.setpoint_2 + self.hysteresis_2:
            self.damper_action = 1

    def vcc_control(self, time_step_s):
        if self.vcc_is_active:
            self.cycle_duration_s += time_step_s

            error = self.temperature["cabinet_1"] - self.setpoint_1

            if(error > 0):
                self.integral_error += error
            else:
                self.integral_error += 20*error

            if(self.integral_error*self.Ki > self.max_speed-self.min_speed):
                self.integral_error = (self.max_speed-self.min_speed)/self.Ki
            elif self.integral_error < 0:
                self.integral_error = 0

            p_component = self.Kp*error
            i_component = self.Ki*self.integral_error

            self.compressor_speed = self.min_speed + p_component + i_component

            if(self.compressor_speed > self.max_speed):
                self.compressor_speed = self.max_speed
            elif(self.compressor_speed < self.min_speed):
                self.compressor_speed = self.min_speed

            if self.temperature["cabinet_1"] < self.setpoint_1 + 0.05:
                self.time_below_setpoint_s += time_step_s
                if self.time_below_setpoint_s > self.stab_time*60:
                    self.vcc_is_active = 0
        else:
            self.time_below_setpoint_s = 0
            self.compressor_speed = 0
            self.cycle_duration_s = 0
            
            if self.temperature["cabinet_1"] > self.setpoint_1 + self.hysteresis_1:
                self.vcc_is_active = 1
            
        if self.temperature["cabinet_2"] < self.setpoint_2:
            self.damper_action = 0
        elif self.temperature["cabinet_2"] > self.setpoint_2 + self.hysteresis_2:
            self.damper_action = 1
    
    def variable_reference(self):
        if(self.cycle_duration_s > self.tto*60):
            dynamic_reference = self.setpoint_1
        else:
            dynamic_reference = self.setpoint_1 + self.hysteresis_1*(1 - (self.cycle_duration_s/(self.tto*60)))
        return dynamic_reference
    
    def calculate_power(self):
        self.power["compressor"] = self.compressor_max_power * ((self.compressor_speed / self.max_speed)**0.5)

    def calculate_heat_capacity_rates(self):
        # Heat capacity rates (thermal coupling) measured in W/K
        self.heat_capacity_rate[self.coupling_key("cabinet_1", "cabinet_2")] = self.damper_action * 0.025
        self.heat_capacity_rate[self.coupling_key("cabinet_1", "ambient")] = 0.005 + (self.cabinet_1_door_state * 0.05)
        self.heat_capacity_rate[self.coupling_key("cabinet_2", "ambient")] = 0.01 + (self.cabinet_2_door_state * 0.05)
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
        
        self.calculate_power()
        self.calculate_heat_capacity_rates()

        #Energy variation
        delta_energy = {}
        delta_energy["ambient"] = 0
        delta_energy["cabinet_1"] = time_step * \
                                      (self.heat_transfer_rate_get("ambient", "cabinet_1")  - \
                                       (self.power["compressor"] * 0.001))
        delta_energy["cabinet_2"] = time_step * \
                                      (self.heat_transfer_rate_get("ambient", "cabinet_2")  + \
                                       self.heat_transfer_rate_get("cabinet_1", "cabinet_2"))
        delta_energy["food_1"] = time_step * self.heat_transfer_rate_get("cabinet_1", "food_1")
        delta_energy["food_2"] = time_step * self.heat_transfer_rate_get("cabinet_2", "food_2")


        #Apply timestep
        for key in self.temperature:
            if(self.mass[key] != 0):
                self.temperature[key] += delta_energy[key]/(self.mass[key] * self.specific_heat[key])

    #Get the heat transfer rate from body1 to body2
    #  heat transfer rate -> W
    #  heat capacity rate -> W/Celsius
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
    time_step = 60  # Time step for simulation (in seconds)

    num_steps = 60*24 # 1 day of simulation

    # Initialize the data arrays
    t_ambient = np.zeros(num_steps)
    t_cabinet_1 = np.zeros(num_steps)
    t_food_1 = np.zeros(num_steps)
    if(system == "house_refrigerator"):
        t_cabinet_2 = np.zeros(num_steps)
        t_food_2 = np.zeros(num_steps)
    t_speed = np.zeros(num_steps)
    t_reference = np.zeros(num_steps)

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

        t_reference[i] = simulator.setpoint_1

    
    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(t_ambient, label='Ambient')
    plt.plot(t_cabinet_1, label='Cabinet 1')
    plt.plot(t_food_1, label='Food 1')
    if(system == "house_refrigerator"):
        plt.plot(t_cabinet_2, label='Cabinet 2')
        plt.plot(t_food_2, label='Food 2')
    plt.plot(t_speed, label='Speed/100')
    plt.plot(t_reference, label='Reference')
    plt.title('Simulation of Refrigeration System')
    plt.xlabel('Minutes')
    plt.ylabel('Value')
    plt.legend()
    plt.show()