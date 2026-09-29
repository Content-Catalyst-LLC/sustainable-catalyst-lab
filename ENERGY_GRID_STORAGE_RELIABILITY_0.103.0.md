# Lab 0.103.0 — Grid, Storage & Reliability Uncertainty

Adds seeded Monte Carlo / Latin-hypercube adequacy scenario planning around Workbench 6.3.0 `adequacy-timeseries` execution. The Lab perturbs only caller-declared demand, renewable-output, storage-availability, and firm forced-outage parameters. It produces explicit Workbench requests and analyzes returned ENS / loss-of-load distributions. It never calls Workbench automatically, predicts outages, or declares a real grid reliable.
