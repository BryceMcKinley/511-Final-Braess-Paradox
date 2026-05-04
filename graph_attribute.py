import simulate as sim_mod
import matplotlib.pyplot as plt

def analyze_parameter_impact(parameter_name, values):
    """
    Sweeps through a list of values for a specific parameter and graphs the result.
    """
    results = []
    print(f"Analyzing impact of {parameter_name}...")
    
    for val in values:
        sim_param = sim_mod.SimulationParams()
        # Override global module variables
        if parameter_name == 'toll': 
            sim_param.TOLL_VALUE = val
        elif parameter_name == 'altruism': 
            sim_param.ALTRUISTIC_PERCENTAGE = val
        elif parameter_name == 'RNDM_SWITCH_PROB': 
            sim_param.RNDM_SWITCH_PROB = val
            sim_param.RNDM_SWITCH = True
        elif parameter_name == 'learning': 
            sim_param.learning_rate = val
        else:
            raise ValueError(f"Unknown parameter: {parameter_name}")

        temp_sim = sim_mod.Simulation(params=sim_param)
        
        current_avg = 0
        for _ in range(sim_mod.SimulationParams.ITERATIONS):
            current_avg = temp_sim.step()
            
        results.append(current_avg)
        print(f"{parameter_name}: {val} | Final Avg Time: {current_avg:.2f}")

    # Plotting results
    plt.figure(figsize=(10, 6))
    plt.plot(values, results, marker='o', linestyle='-', color='teal', linewidth=2)
    plt.title(f"Impact of {parameter_name.capitalize()} on Total System Efficiency")
    plt.xlabel(f"Value of {parameter_name}")
    plt.ylim(60, 90)  # Adjust y-axis limits based on parameter range    
    plt.ylabel("Equilibrium Avg Travel Time (min)")
    plt.grid(True, alpha=0.3)
    plt.show()

# Example usage:
analyze_parameter_impact('toll', [0, 5, 10, 15, 20, 25, 30])
# analyze_parameter_impact('RNDM_SWITCH_PROB', [0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0])
# analyze_parameter_impact('learning', [0.1, 0.2, 0.3, 0.4, 0.5])6)  # Adjust y-axis limits based 
