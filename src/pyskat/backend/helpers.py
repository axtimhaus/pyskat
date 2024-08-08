def filter_none_values(a_dict: dict):
    """Removes all entries from dict whose value is None."""
    return {k: v for k, v in a_dict if v is not None}


def update_if_not_none(base: dict, **kwargs):
    """Updates the 'base' dict with the values from 'kwargs',
    but only if the respective value in 'kwargs' is not None."""
    return base | filter_none_values(kwargs)
