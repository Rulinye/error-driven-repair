import numpy as np


def impedances(resistance, reactance):
    """Return the complex impedances R + jX in double precision."""
    z = np.asarray(resistance, dtype=np.cfloat)
    z += 1j * np.asarray(reactance)
    return z
