# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

from typing import Dict
from typing import List
from typing import Tuple


def uniform_result(items) -> List[float]:
    # List[Item, Selector]
    # likelihood = Selector / Item
    max_features = sum([feature for _, feature in items])
    if max_features == 0:
        # no potential toc in document
        return [0.0 for _ in items]
    result = [feature / max_features for (_, feature) in items]
    # round to 2 digits
    result = [round(item, 2) for item in result]
    return result


def uniform_result_with_items(items: Dict[str, int],
                             ) -> List[Tuple[str, float]]:
    common = sum(items.values())
    result = [(
        size,
        round(occurence / common, 2),
    ) for size, occurence in items.items()]
    return result
