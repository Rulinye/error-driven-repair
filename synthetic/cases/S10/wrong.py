import gridwell


def wallpaper(motif, down, across):
    """Return the motif repeated down times vertically and across times horizontally."""
    return gridwell.tile(motif, (across, down))
