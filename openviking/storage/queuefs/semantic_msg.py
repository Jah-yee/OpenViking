# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""SemanticMsg: Semantic extraction queue message dataclass."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


@dataclass
class SemanticMsg:
    """Semantic extraction queue message.

    Attributes:
        id: Unique identifier (UUID)
        uri: Directory URI to process
        context_type: Type of context (resource, memory, skill)
        status: Processing status (pending/processing/completed)
        timestamp: Creation timestamp
        recursive: Whether to recursively process subdirectories.
                   When True, the processor will collect all subdirectory info and
                   enqueue them for processing (bottom-up order).
                   When False, only the specified directory will be processed.
        lock_resource_uri: Resource URI for lock release on completion
        lock_id: Lock ID for release on completion
    """

    id: str  # UUID
    uri: str  # Directory URI
    context_type: str  # resource, memory, skill
    status: str = "pending"  # pending/processing/completed
    timestamp: int = int(datetime.now().timestamp())
    recursive: bool = True  # Whether to recursively process subdirectories
    account_id: str = "default"
    user_id: str = "default"
    agent_id: str = "default"
    role: str = "root"
    # Additional flags
    skip_vectorization: bool = False
    is_incremental_update: bool = False
    target_uri_root: str = ""
    # Lock release info
    lock_resource_uri: str = ""
    lock_id: str = ""

    def __init__(
        self,
        uri: str,
        context_type: str,
        recursive: bool = True,
        account_id: str = "default",
        user_id: str = "default",
        agent_id: str = "default",
        role: str = "root",
        skip_vectorization: bool = False,
        is_incremental_update: bool = False,
        target_uri_root: str = "",
        lock_resource_uri: str = "",
        lock_id: str = "",
    ):
        self.id = str(uuid4())
        self.uri = uri
        self.context_type = context_type
        self.recursive = recursive
        self.account_id = account_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.role = role
        self.skip_vectorization = skip_vectorization
        self.is_incremental_update = is_incremental_update
        self.target_uri_root = target_uri_root
        self.lock_resource_uri = lock_resource_uri
        self.lock_id = lock_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert object to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticMsg":
        """Safely create object from dictionary, filtering extra fields and handling missing fields."""
        if not data:
            raise ValueError("Data dictionary is empty")

        uri = data.get("uri")
        context_type = data.get("context_type")

        if not uri or not context_type:
            missing = []
            if not uri:
                missing.append("uri")
            if not context_type:
                missing.append("context_type")
            raise ValueError(f"Missing required fields: {missing}")

        obj = cls(
            uri=uri,
            context_type=context_type,
            recursive=data.get("recursive", True),
            account_id=data.get("account_id", "default"),
            user_id=data.get("user_id", "default"),
            agent_id=data.get("agent_id", "default"),
            role=data.get("role", "root"),
            skip_vectorization=data.get("skip_vectorization", False),
            is_incremental_update=data.get("is_incremental_update", False),
            target_uri_root=data.get("target_uri_root", ""),
            lock_resource_uri=data.get("lock_resource_uri", ""),
            lock_id=data.get("lock_id", ""),
        )
        if "id" in data and data["id"]:
            obj.id = data["id"]
        if "status" in data:
            obj.status = data["status"]
        if "timestamp" in data:
            obj.timestamp = data["timestamp"]
        return obj

    @classmethod
    def from_json(cls, json_str: str) -> "SemanticMsg":
        """Create object from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
