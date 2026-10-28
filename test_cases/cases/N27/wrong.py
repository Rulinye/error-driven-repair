import numpy as np


def impedances(resistance, reactance):
    """Return the complex impedances R + jX in double precision."""
    z = np.asarray(resistance, dtype=np.complex64)
    z += 1j * np.asarray(reactance)
    return z
