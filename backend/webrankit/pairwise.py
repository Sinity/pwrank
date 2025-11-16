from __future__ import annotations

import math
import random
from operator import itemgetter
from typing import Any, List, Optional, Tuple

import rpy2
from rpy2.rlike.container import OrdDict
from rpy2.robjects import DataFrame, packages, r
from rpy2.robjects.vectors import (
    FactorVector,
    FloatSexpVector,
    FloatVector,
    IntSexpVector,
    StrVector,
)

_r_bt2 = packages.importr('BradleyTerry2')
_r_base = packages.importr('base')

class PairwiseModel:
    def __init__(self) -> None:
        self.model: Optional[Any] = None
        self.coefficients: Optional[List[Tuple[float, float, str]]] = None  # (ability, stderr, item), sorted by ability
        self.items: List[str] = []
        self.comparison_items: List[List[str]] = [[], []]
        self.comparison_wins: List[List[int]] = [[], []]

    def update_model(self) -> None:
        r_BTm = r('function(df) { BTm(cbind(win1, win2), Label.1, Label.2, data=df) }')
        self.model = r_BTm(self._comparisons_dataframe())

        coeff = _r_bt2.BTabilities(self.model)
        abilities = coeff.rx(True, 1)
        stderrs = coeff.rx(True, 2)
        self.coefficients = sorted(zip(abilities, stderrs, coeff.rownames))

    def coeff_by_id(self, item_id: str) -> Optional[Tuple[float, float, str]]:
        if self.coefficients is None:
            return None
        for coeff in self.coefficients:
            if coeff[2] == item_id:
                return coeff
        return None

    def next_comparison(self) -> Tuple[str, str]:
        if random.random() > 0.33:
            return self.optimal_comparison()
        else:
            return self.random_comparison()

    def win(self, winner: str, loser: str, count: int = 1) -> None:
        idx = self._get_comparison_idx(winner, loser)
        self.comparison_wins[0][idx] += (min(winner, loser) == winner) * count
        self.comparison_wins[1][idx] += (min(winner, loser) == loser) * count

    def draw(self, item1: str, item2: str, count: int = 1) -> None:
        idx = self._get_comparison_idx(item1, item2)
        self.comparison_wins[0][idx] += int(0.5 * count)
        self.comparison_wins[1][idx] += int(0.5 * count)

    def optimal_comparison(self) -> Tuple[str, str]:
        if self.coefficients is None:
            raise ValueError("Model not trained yet")
        highest_stderr_item = max(self.coefficients, key=itemgetter(1))
        item1_idx = self.coefficients.index(highest_stderr_item)
        return (self.coefficients[item1_idx][2], self.coefficients[self._less_certain_neighbour(item1_idx)][2])

    def random_comparison(self) -> Tuple[str, str]:
        if self.coefficients is None:
            raise ValueError("Model not trained yet")
        rand_item = random.choice(self.coefficients)
        item1_idx = self.coefficients.index(rand_item)
        return (self.coefficients[item1_idx][2], self.coefficients[self._less_certain_neighbour(item1_idx)][2])

    def _less_certain_neighbour(self, item1_idx: int) -> int:
        if self.coefficients is None:
            raise ValueError("Model not trained yet")
        if item1_idx == 0:
            return 1
        elif item1_idx == len(self.coefficients) - 1:
            return item1_idx - 1
        elif self.coefficients[item1_idx - 1][1] > self.coefficients[item1_idx + 1][1]:
            return item1_idx - 1
        else:
            return item1_idx + 1

    def _get_comparison_idx(self, item1: str, item2: str) -> int:
        first, second = min(item1, item2), max(item1, item2)
        comparisons = enumerate(zip(*self.comparison_items))
        idx = next((i for i, pair in comparisons if pair == (first, second)), None)
        if idx is None:
            idx = len(self.comparison_items[0])
            self.comparison_items[0].append(first)
            self.comparison_items[1].append(second)
            self.comparison_wins[0].append(0)
            self.comparison_wins[1].append(0)
            if first not in self.items:
                self.items.append(first)
            if second not in self.items:
                self.items.append(second)
        return idx

    def _comparisons_dataframe(self) -> DataFrame:
        column_comp1 = ('Label.1', FactorVector(self.comparison_items[0], levels=StrVector(self.items)))
        column_comp2 = ('Label.2', FactorVector(self.comparison_items[1], levels=StrVector(self.items)))
        column_win1 = ('win1', FloatVector(self.comparison_wins[0]))
        column_win2 = ('win2', FloatVector(self.comparison_wins[1]))
        return DataFrame(OrdDict([column_comp1, column_comp2, column_win1, column_win2]))

