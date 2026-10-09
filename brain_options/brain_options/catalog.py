"""
Options field catalog loader and grouping utilities.
Provides access to all 138 live BRAIN option fields grouped by economic sub-family.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class OptionField:
    id: str
    description: str
    dataset: str
    category: str
    subcategory: str
    field_type: str
    alpha_count: int
    user_count: int


class OptionsCatalog:
    def __init__(self, catalog_path: Optional[str] = None):
        if catalog_path is None:
            data_file = os.path.join(os.path.dirname(__file__), "data", "catalog.json")
            if os.path.exists(data_file):
                catalog_path = data_file
            else:
                catalog_path = os.path.join(os.path.dirname(__file__), "catalog.json")

        self.catalog_path = catalog_path
        self.fields: list[OptionField] = []
        self._fields_by_id: dict[str, OptionField] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.catalog_path):
            return
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            field = OptionField(
                id=item.get("id", ""),
                description=item.get("description", ""),
                dataset=item.get("dataset", ""),
                category=item.get("category", ""),
                subcategory=item.get("subcategory", ""),
                field_type=item.get("type", "MATRIX"),
                alpha_count=int(item.get("alphaCount", 0)),
                user_count=int(item.get("userCount", 0)),
            )
            self.fields.append(field)
            self._fields_by_id[field.id] = field

    def get_field(self, field_id: str) -> Optional[OptionField]:
        return self._fields_by_id.get(field_id)

    @property
    def all_field_ids(self) -> list[str]:
        return [f.id for f in self.fields]

    @property
    def pcr_vol_fields(self) -> list[str]:
        """Put-Call Ratio by Volume across tenors."""
        return [f.id for f in self.fields if f.id.startswith("pcr_vol_")]

    @property
    def pcr_oi_fields(self) -> list[str]:
        """Put-Call Ratio by Open Interest across tenors."""
        return [f.id for f in self.fields if f.id.startswith("pcr_oi_")]

    @property
    def skew_fields(self) -> list[str]:
        """Implied Volatility Skew steepness fields."""
        return [f.id for f in self.fields if "skew" in f.id]

    @property
    def atm_iv_fields(self) -> list[str]:
        """At-the-money implied volatility fields."""
        return [f.id for f in self.fields if f.id.startswith("implied_volatility_mean_") and "skew" not in f.id]

    @property
    def forward_price_fields(self) -> list[str]:
        """Synthetic forward prices derived from options parity."""
        return [f.id for f in self.fields if f.id.startswith("forward_price_")]

    @property
    def call_breakeven_fields(self) -> list[str]:
        """Call breakeven prices weighted by OI."""
        return [f.id for f in self.fields if f.id.startswith("call_breakeven_")]

    def subfamilies(self) -> dict[str, list[str]]:
        """Group fields by sub-family."""
        return {
            "forward_price": self.forward_price_fields,
            "call_breakeven": self.call_breakeven_fields,
            "pcr_vol": self.pcr_vol_fields,
            "pcr_oi": self.pcr_oi_fields,
            "skew": self.skew_fields,
            "atm_iv": self.atm_iv_fields,
        }

    def summarize_for_prompt(self, max_fields_per_group: int = 8) -> str:
        """Generates a compact, highly descriptive summary for LLM prompt context."""
        return (
            f"1. FORWARD PRICES (Synthetic Forward Expectations): {', '.join(self.forward_price_fields[:max_fields_per_group])}\n"
            f"2. CALL BREAKEVEN PRICES (OI-Weighted Hurdle Rates): {', '.join(self.call_breakeven_fields[:max_fields_per_group])}\n"
            f"3. PUT-CALL VOLUME RATIOS (Smart-Money Flow & Hedging): {', '.join(self.pcr_vol_fields[:max_fields_per_group])}\n"
            f"4. PUT-CALL OI RATIOS (Open Interest Positioning): {', '.join(self.pcr_oi_fields[:max_fields_per_group])}\n"
            f"5. IMPLIED VOLATILITY SKEW (Downside Tail Risk Steepness): {', '.join(self.skew_fields[:max_fields_per_group])}\n"
            f"6. ATM IMPLIED VOLATILITY (Market Expected Variance): {', '.join(self.atm_iv_fields[:max_fields_per_group])}"
        )
