"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Request Models for Steganography Detection API
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class SteganographyRequest:
    """
    Model for single text steganography detection request
    """

    text: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BatchTextItem:
    """
    Model for individual text item in batch request
    """

    text: str
    id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BatchSteganographyRequest:
    """
    Model for batch steganography detection request
    """

    texts: List[BatchTextItem]
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
