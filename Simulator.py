import numpy as np
import time
import timeit
import torch
from scipy.stats import norm


class Simulator:
    @staticmethod
    def simulate_posudo(spot, r, q, sigma, dt, num_paths, time_steps):
        np.random.seed(int(time.time()))
        half_path = int(num_paths / 2) + 1
        sqrt_var = sigma * np.sqrt(dt)
        st = spot * np.ones((num_paths, time_steps + 1))
        # start = timeit.default_timer()
        simu = np.random.normal(0, 1, (half_path, time_steps))
        anti_simu = -simu
        simulation = np.concatenate((simu, anti_simu))[:num_paths, :]
        growth = (r - q - 0.5 * sigma * sigma) * dt + sqrt_var * simulation
        factor = np.exp(growth)
        for i in range(1, time_steps + 1):
            st[:, i] = st[:, i - 1] * factor[:, i - 1]

        return st

    @staticmethod
    def simulate_sobol(spot, r, q, sigma, dt, num_paths, time_steps):
        sqrt_var = sigma * np.sqrt(dt)
        st = spot * np.ones((num_paths, time_steps + 1))
        soboleng = torch.quasirandom.SobolEngine(dimension=time_steps, scramble=True, seed=int(time.time()))
        Sobol_Rn = np.array(soboleng.draw(num_paths, dtype=torch.float64))
        simulation = norm.ppf(Sobol_Rn)
        growth = (r - q - 0.5 * sigma * sigma) * dt + sqrt_var * simulation
        factor = np.exp(growth)
        for i in range(1, time_steps + 1):
            st[:, i] = st[:, i - 1] * factor[:, i - 1]
        return st

## Testing
# N = 100000
# start = timeit.default_timer()
# sim_prices = Simulator.simulate_posudo(100, 0.025, 0.01, 0.25, 1.0/365.0, N, 365)
# stop = timeit.default_timer()
# sim_prices_2 = Simulator.simulate_sobol(101, 0.025, 0.01, 0.25, 1.0/365.0, N, 365)
# factor = sim_prices_2 / sim_prices
# print('Time: ', stop - start)
