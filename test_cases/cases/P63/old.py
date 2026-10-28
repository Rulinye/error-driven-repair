def any_flag_per_site(flags):
    """For each site (the index level "site"), tell whether any row has each flag set."""
    return flags.any(level="site")
