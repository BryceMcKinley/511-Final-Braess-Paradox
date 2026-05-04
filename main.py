import matplotlib.pyplot as plt
import simulate as sim_mod

# --- Execute ---

simulate_params = sim_mod.SimulationParams()
simulate_params.RNDM_SWITCH = True


sim = sim_mod.Simulation(params=simulate_params)
history, cars_sat, cars_sbt, cars_sabt = [], [], [], []


plt.ion()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8), dpi=90)
plt.subplots_adjust(left=0.05, right=0.95, wspace=0.3)

for i in range(simulate_params.ITERATIONS):
    avg_time = sim.step()
    history.append(avg_time)
    cars_sat.append(sim.roads[2].cars)
    cars_sbt.append(sim.roads[1].cars)
    cars_sabt.append(sim.roads[0].cars - sim.roads[2].cars if len(sim.roads) > 4 else 0)
    
    sim.draw_network(i, avg_time)
    
    # Right top: Equilibrium Graph
    plt.subplot(2, 2, 2)
    plt.cla()
    plt.plot(history, color='red', linewidth=2)
    plt.title(f"Equilibrium Graph: Avg Time = {avg_time:.2f} min")
    plt.xlabel("Iteration")
    plt.ylabel("Avg Travel Time (min)")
    plt.ylim(60, 90)
    plt.grid(True, alpha=0.3)
    
    # Right bottom: Number of Cars per Path Graph
    plt.subplot(2, 2, 4)
    plt.cla()
    plt.plot(cars_sat, color='red', label='S-A-T')
    plt.plot(cars_sbt, color='green', label='S-B-T')
    plt.plot(cars_sabt, color='blue', label='S-A-B-T')
    plt.title("Number of Cars Per Path")
    plt.xlabel("Iteration")
    plt.ylim(0, sim.params.NUM_CARS)
    plt.ylabel("Number of Cars")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.pause(0.01)

plt.ioff()
plt.show()