"""
Sentiment field catalog loader and grouping utilities.
Provides access to BRAIN sentiment fields grouped by economic sub-family.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class SentimentField:
    id: str
    description: str
    dataset: str
    category: str
    subcategory: str
    field_type: str
    alpha_count: int
    user_count: int


class SentimentCatalog:
    def __init__(self, catalog_path: Optional[str] = None):
        if catalog_path is None:
            data_file = os.path.join(os.path.dirname(__file__), "data", "catalog.json")
            if os.path.exists(data_file):
                catalog_path = data_file
            else:
                catalog_path = os.path.join(os.path.dirname(__file__), "catalog.json")

        self.catalog_path = catalog_path
        self.fields: list[SentimentField] = []
        self._fields_by_id: dict[str, SentimentField] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.catalog_path):
            return
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for item in raw_data:
            dataset_info = item.get("dataset", {})
            dataset_name = dataset_info.get("name", "") if isinstance(dataset_info, dict) else str(dataset_info)
            category_info = item.get("category", {})
            category_name = category_info.get("name", "") if isinstance(category_info, dict) else str(category_info)
            subcat_info = item.get("subcategory", {})
            subcat_name = subcat_info.get("name", "") if isinstance(subcat_info, dict) else str(subcat_info)

            field = SentimentField(
                id=item.get("id", ""),
                description=item.get("description", ""),
                dataset=dataset_name,
                category=category_name,
                subcategory=subcat_name,
                field_type=item.get("type", "MATRIX"),
                alpha_count=int(item.get("alphaCount", 0)),
                user_count=int(item.get("userCount", 0)),
            )
            self.fields.append(field)
            self._fields_by_id[field.id] = field

    def get_field(self, field_id: str) -> Optional[SentimentField]:
        return self._fields_by_id.get(field_id)

    @property
    def all_field_ids(self) -> list[str]:
        return [f.id for f in self.fields]
