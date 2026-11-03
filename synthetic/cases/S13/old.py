import quillery


def caption_lines(caption):
    """Return the caption broken into lines of at most 24 characters."""
    return quillery.wrap(caption, width=24)
