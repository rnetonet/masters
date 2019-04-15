import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import timesynth as ts

time_sampler = ts.TimeSampler(stop_time=60)
times_to_sample = time_sampler.sample_irregular_time(
    num_points=3600, keep_percentage=50
)

signal_generator = ts.signals.Sinusoidal(frequency=0.05)
noise_generator = ts.noise.GaussianNoise(std=0)
timeserie = ts.TimeSeries(signal_generator, noise_generator=noise_generator)

samples, signals, errors = timeserie.sample(times_to_sample)

fig, ax = plt.subplots()

plt.plot(times_to_sample, samples)

circle = plt.Circle((0, 0), 0.2, color="r", fill=False)
ax.add_artist(circle)

plt.show()
