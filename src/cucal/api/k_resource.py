from typing import Sequence, Mapping


def unit_costs(resource_ids: Sequence[str]) -> Mapping[str, float]:
    """
    Temporary stub that returns a fake price for each resource.

    Replace this implementation with the real network call once the
    k-resource service is available.

    Args:
        resource_ids: iterable of resource IDs, e.g. ["r1", "r2"]

    Returns:
        dict: mapping {resource_id: cost_per_unit_in_dollars}
    """
    # Example: $1.50, $2.50, $3.50 ...
    return {rid: 1.5 + idx for idx, rid in enumerate(resource_ids)}
