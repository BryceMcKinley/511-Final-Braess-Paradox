import simulate as sim_mod
import pandas as pd

def find_best_parameters():
    # Define the ranges you want to test
    tolls = [0, 5, 15, 25, 45]
    altruism_levels = [0.0, 0.01, 0.05, 0.1]
    learning_rates = [0.1, 0.2, 0.5]
    random_switch_probs = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5]

    results = []

    print("Starting optimization sweep...")
    for toll in tolls:
        for altruism in altruism_levels:
            for lr in learning_rates:
                for rsp in random_switch_probs:
                    # Create a specific parameter set for this run
                    params = sim_mod.SimulationParams(
                        TOLL_VALUE=toll,
                        ALTRUISTIC_PERCENTAGE=altruism,
                        LEARNING_RATE_OVERRIDE=lr,
                        INCLUDE_SHORTCUT=True,
                        RNDM_SWITCH=True,
                        RNDM_SWITCH_PROB=rsp
                    )

                    # Run simulation to equilibrium[cite: 5, 6]
                    sim = sim_mod.Simulation(params=params)
                    final_avg_time = 0
                    for _ in range(params.ITERATIONS):
                        final_avg_time = sim.step()

                    results.append({
                        'Toll': toll,
                        'Altruism': altruism,
                        'LearningRate': lr,
                        'AvgTime': final_avg_time,
                        'RNDM_SWITCH_PROB': rsp
                    })
                    print(f"Tested: Toll={toll}, Altruism={altruism}, LR={lr}, RSP={rsp} -> Result: {final_avg_time:.2f}")

    # Convert to DataFrame for easy sorting
    df = pd.DataFrame(results)
    best_config = df.loc[df['AvgTime'].idxmin()]

    print("\n" + "="*30)
    print("OPTIMIZATION COMPLETE")
    print(f"The Best Avg Time found was: {best_config['AvgTime']:.2f} minutes")
    print(f"Optimal Toll: {best_config['Toll']}")
    print(f"Optimal Altruism: {best_config['Altruism']*100}%")
    print(f"Optimal Learning Rate: {best_config['LearningRate']}")
    print(f"Optimal Random Switch Prob: {best_config['RNDM_SWITCH_PROB']*100}%")
    print("="*30)

    return best_config

if __name__ == "__main__":
    find_best_parameters()