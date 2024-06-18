class RefrigerationSystem:
    def __init__(self):
        #Constants
        # Specific heat measured in J/(Kg*K) 
        self.specific_heat = {}
        self.specific_heat["compartment"] = 1500
        self.specific_heat["evaporator_air"] = 716
        self.specific_heat["condenser_air"] = 716

        # Heat capacity rates (thermal coupling) measured in W/K 
        self.heat_capacity_rate = {}
        self.heat_capacity_rate[self.coupling_key("compartment", "evaporator_air")] = 0.419
        self.heat_capacity_rate[self.coupling_key("compartment", "ambient")] = 0.1
        self.heat_capacity_rate[self.coupling_key("evaporator_air", "evaporator_refrigerant")] = 0.32
        self.heat_capacity_rate[self.coupling_key("condenser_air", "condenser_refrigerant")] = 0.64
        self.heat_capacity_rate[self.coupling_key("condenser_air", "ambient")] = 0.419

        self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")] = 1.00
        self.heat_capacity_rate[self.coupling_key("expansion_valve", "refrigerant")] = 1.00

        #Initial state
        self.temperature_c = {}
        self.temperature_c["ambient"] = 25.0
        self.temperature_c["compartment"] = 10.0
        self.temperature_c["evaporator_air"] = 25.0
        self.temperature_c["evaporator_refrigerant"] = 25.0
        self.temperature_c["condenser_air"] = 25.0
        self.temperature_c["condenser_refrigerant"] = 25.0
        self.temperature_c["condenser_out"] = self.temperature_c["condenser_refrigerant"]

        self.refrigerant_mass_total = 2.0
        self.mass = {}
        self.mass["compartment"] = 10.0
        self.mass["evaporator_air"] = 0.2
        self.mass["condenser_air"] = 0.2
        self.mass["evaporator_refrigerant"] = 0.5*self.refrigerant_mass_total
        self.mass["condenser_refrigerant"] = self.refrigerant_mass_total - self.mass["evaporator_refrigerant"]

        self.enthalpy = {}
        self.enthalpy["evaporator_refrigerant"] = 0
        self.enthalpy["condenser_refrigerant"] = 0

    def simulate(self, time_step_s):
        #Input values
        power = {}
        power["compressor"] = 1.0

        #Calculate auxiliary variables

        #Energy variation
        delta_energy = {}
        delta_energy["compartment"] = time_step * \
                                      (self.heat_transfer_rate_get("evaporator_air", "compartment") + \
                                       self.heat_transfer_rate_get("ambient", "compartment"))
        delta_energy["evaporator_air"] = time_step * \
                                         (self.heat_transfer_rate_get("compartment", "evaporator_air") + \
                                          self.heat_transfer_rate_get("evaporator_refrigerant", "evaporator_air"))
        delta_energy["condenser_air"] = time_step * \
                                        (self.heat_transfer_rate_get("ambient", "condenser_air") + \
                                         self.heat_transfer_rate_get("condenser_refrigerant", "condenser_air") + \
                                         power["compressor"])
        delta_energy["compressor"] = time_step * power["compressor"]
        delta_energy["subcooling"] = time_step * \
                                     (self.heat_transfer_rate_get("evaporator_air", "evaporator_refrigerant") + \
                                      power["compressor"] -\
                                      self.heat_transfer_rate_get("condenser_refrigerant", "condenser_air"))

        #Enthalpy
        self.enthalpy["condenser_out"] = self.a5 + self.a4 * self.temperature_c["condenser_out"]
        self.enthalpy["evaporator_in"] = self.enthalpy["condenser_out"]
        self.enthalpy["evaporator_refrigerant_vapour"] = self.a3 + \
                                                    self.a2 * self.temperature_c["evaporator_refrigerant"] + \
                                                    self.a1 * self.temperature_c["evaporator_refrigerant"] * self.temperature_c["evaporator_refrigerant"]
        self.enthalpy["evaporator_refrigerant_liquid"] = self.a5 + \
                                                    self.a4 * self.temperature_c["evaporator_refrigerant"]

        self.enthalpy["evaporator_out"] = 2*self.enthalpy["evaporator_refrigerant"] - self.enthalpy["evaporator_in"]
        self.enthalpy["condenser_in"] = self.enthalpy["evaporator_out"] + power["compressor"]*self.cpr/self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")]

        #Refrigerant quality
        refrigerant_quality = {}
        refrigerant_quality["evaporator_in"] = (self.enthalpy["evaporator_in"] - self.enthalpy["evaporator_refrigerant_liquid"]) / \
                                               (self.enthalpy["evaporator_refrigerant_vapour"] - self.enthalpy["evaporator_refrigerant_liquid"])
        refrigerant_quality["evaporator_refrigerant"] = (refrigerant_quality["evaporator_in"] + 1)/2
        refrigerant_quality["condenser_refrigerant"] = 0.5

        #Mass variation
        delta_mass = {}
        delta_mass["evaporator_refrigerant"] = (self.heat_capacity_rate[self.coupling_key("expansion_valve", "refrigerant")] - \
                                                self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")])/self.cpr
        delta_mass["condenser_refrigerant"] = -delta_mass["evaporator_refrigerant"]

        #Enthalpy variation
        delta_enthalpy = {}
        tmp_a = (self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")]*self.enthalpy["evaporator_in"] - \
                 self.heat_capacity_rate[self.coupling_key("expansion_valve", "refrigerant")]*self.enthalpy["evaporator_out"]) / self.cpr
        tmp_b = self.heat_transfer_rate_get("evaporator_air","evaporator_refrigerant")
        tmp_c = -self.enthalpy["evaporator_refrigerant"]*delta_mass["evaporator_refrigerant"]
        delta_enthalpy["evaporator_refrigerant"] = time_step*(tmp_a + tmp_b + tmp_c)/self.mass["evaporator_refrigerant"]

        tmp_a = (self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")]*self.enthalpy["condenser_in"] - \
                 self.heat_capacity_rate[self.coupling_key("expansion_valve", "refrigerant")]*self.enthalpy["condenser_out"]) / self.cpr
        tmp_b = self.heat_transfer_rate_get("condenser_refrigerant","condenser_air") + power["compressor"]
        tmp_c = -self.enthalpy["condenser_refrigerant"]*delta_mass["condenser_refrigerant"]
        delta_enthalpy["condenser_refrigerant"] = time_step*(tmp_a + tmp_b + tmp_c)/self.mass["condenser_refrigerant"]

        c4 = self.a4*(1-refrigerant_quality["evaporator_refrigerant"]) + \
             self.a1*2*refrigerant_quality["evaporator_refrigerant"]*self.temperature_c["evaporator_refrigerant"] + \
             self.a2*refrigerant_quality["evaporator_refrigerant"]
        
        c7 = self.a4*(1-refrigerant_quality["condenser_refrigerant"]) + \
             self.a1*2*refrigerant_quality["condenser_refrigerant"]*self.temperature_c["condenser_refrigerant"] + \
             self.a2*refrigerant_quality["condenser_refrigerant"]


        #Calculate temperature deltas
        delta_temperature = {}
        delta_temperature["compartment"] = delta_energy["compartment"]/(self.mass["compartment"] * self.specific_heat["compartment"])
        delta_temperature["evaporator_air"] = delta_energy["evaporator_air"]/(self.mass["evaporator_air"] * self.specific_heat["evaporator_air"])
        delta_temperature["condenser_air"] = delta_energy["condenser_air"]/(self.mass["condenser_air"] * self.specific_heat["condenser_air"])
        delta_temperature["evaporator_refrigerant"] = delta_enthalpy["evaporator_refrigerant"]/c4
        delta_temperature["subcooling"] = delta_energy["subcooling"]/self.heat_capacity_rate[self.coupling_key("compressor", "refrigerant")]
        delta_temperature["condenser_refrigerant"] = delta_enthalpy["condenser_refrigerant"]/c7
        
        #Apply timestep
        self.temperature_c["compartment"] += delta_temperature["compartment"]
        self.temperature_c["evaporator_air"] += delta_temperature["evaporator_air"]
        self.temperature_c["condenser_air"] += delta_temperature["condenser_air"]
        self.temperature_c["evaporator_refrigerant"] += delta_temperature["evaporator_refrigerant"]
        self.temperature_c["condenser_refrigerant"] += delta_temperature["condenser_refrigerant"]
        self.temperature_c["condenser_out"] = self.temperature_c["condenser_refrigerant"] - delta_temperature["subcooling"]

        self.mass["evaporator_refrigerant"] += delta_mass["evaporator_refrigerant"]
        self.mass["condenser_refrigerant"] += delta_mass["condenser_refrigerant"]

        self.enthalpy["evaporator_refrigerant"] += delta_enthalpy["evaporator_refrigerant"]
        self.enthalpy["condenser_refrigerant"] += delta_enthalpy["condenser_refrigerant"]



    #Get the heat transfer rate from body1 to body2
    #  heat transfer rate -> W
    #  heat capacity rate -> W/Celsius
    def heat_transfer_rate_get(self, body1, body2):
        delta_temperature = self.temperature_c[body1] - self.temperature_c[body2]
        return delta_temperature*self.heat_capacity_rate[self.coupling_key(body1, body2)]
    
    def coupling_key(self, str1, str2):
        return tuple(sorted((str1, str2)))
    
    def refrigerant_selection(self, selection):
        if selection == "R12":
            self.a1 = -0.00079898
            self.a2 =  0.42074
            self.a3 =  187.58
            self.a4 =  0.94094
            self.a5 =  36.772

            self.b1 = 1.7979e-6
            self.b2 = 0.00072218

            self.c1 = 0.00013694
            self.c2 = 0.011086
            self.c3 = 0.30459

            self.R_hv = 0.99996
            self.R_hl = 0.99975
            self.R_vl = 0.99442

            self.R_psat = 0.99949
            self.Pcrit = 4115
            self.Tcrit = 385.15
            self.M = 120.93

            self.cpr = 0.612

        elif selection == "R134a":
            self.a1 = -0.0019937
            self.a2 =  0.56359
            self.a3 =  247.85
            self.a4 =  1.5408
            self.a5 =  54.332

            self.b1 = 2.3877e-6
            self.b2 = 0.00078627

            self.c1 = 0.00025045
            self.c2 = 0.011438
            self.c3 = 0.20888

            self.R_hv = 0.99919
            self.R_hl = 0.99451
            self.R_vl = 0.98632

            self.R_psat = 0.99801
            self.Pcrit = 4060.3
            self.Tcrit = 374.23
            self.M = 102.03

            self.cpr = 0.9

        else:
            self.a1 = -0.0019937
            self.a2 =  0.56359
            self.a3 =  247.85
            self.a4 =  1.5408
            self.a5 =  54.332

            self.b1 = 2.3877e-6
            self.b2 = 0.00078627

            self.c1 = 0.00025045
            self.c2 = 0.011438
            self.c3 = 0.20888

            self.R_hv = 0.99919
            self.R_hl = 0.99451
            self.R_vl = 0.98632

            self.R_psat = 0.99801
            self.Pcrit = 4060.3
            self.Tcrit = 374.23
            self.M = 102.03

            self.cpr = 0.9

# Example usage:
if __name__ == "__main__":
    simulator = RefrigerationSystem()
    simulator.refrigerant_selection("R134a")
    time_step = 1  # Time step for simulation (in seconds)

    # Simulate heat transfer for 100 time steps
    for i in range(100):
        simulator.simulate(time_step)
        print("Compartment temperature: T1 =", simulator.temperature_c["compartment"])