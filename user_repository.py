"""Data layer for the console system.

Stores users in a local JSON file.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class User:
    username: str
    email: str
    password_hash: str


class UserRepository:
    def __init__(self, path: str) -> None:
        self.path = path
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load(self) -> List[Dict[str, str]]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, users: List[Dict[str, str]]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        # Basic validation
        if not username or not email or not password:
            return False, "Error: All fields are required."
        if len(password) < 6:
            return False, "Error: Password must be at least 6 characters."

        users = self._load()

        if any(u["username"].lower() == username.lower() for u in users):
            return False, "Error: Username already exists."

        users.append(
            {
                "username": username,
                "email": email,
                "password_hash": self._hash_password(password),
            }
        )
        self._save(users)
        return True, "Registration successful."

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        if not username or not password:
            return False, "Error: Username and password are required."

        users = self._load()
        hashed = self._hash_password(password)

        for u in users:
            if u["username"].lower() == username.lower() and u["password_hash"] == hashed:
                return True, "Login successful."

        return False, "Invalid username or password."
