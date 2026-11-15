import os
import json
import uuid
import time
from typing import Dict, Any, Optional, List
from werkzeug.security import generate_password_hash, check_password_hash

class UserManager:
    """
    Manages user registration, authentication, sessions, and user-specific reports.
    """
    def __init__(self, data_path: str = "data/users.json"):
        self.data_path = data_path
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, str] = {}  # token -> user_id
        self._load_users()
        self._seed_default_users()

    def _load_users(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}
        else:
            self.users = {}

    def _save_users(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=2)

    def _seed_default_users(self):
        """Seed default enterprise analyst accounts if empty."""
        default_analysts = [
            {
                "email": "analyst@finintellect.com",
                "name": "Sarah Jenkins, CFA",
                "password": "Analyst@2025",
                "company": "Apex Global Asset Management",
                "role": "Senior Financial Analyst",
                "avatar_initials": "SJ",
                "avatar_color": "from-blue-600 to-indigo-600"
            },
            {
                "email": "cfo@techcorp.com",
                "name": "Michael Vance",
                "password": "CFO@TechCorp25",
                "company": "TechCorp Solutions Ltd.",
                "role": "Chief Financial Officer",
                "avatar_initials": "MV",
                "avatar_color": "from-emerald-600 to-teal-600"
            }
        ]

        modified = False
        for da in default_analysts:
            # Check if email already exists
            existing = self.get_user_by_email(da["email"])
            if not existing:
                uid = str(uuid.uuid4())[:8]
                self.users[uid] = {
                    "id": uid,
                    "name": da["name"],
                    "email": da["email"].lower(),
                    "password_hash": generate_password_hash(da["password"]),
                    "company": da["company"],
                    "role": da["role"],
                    "avatar_initials": da["avatar_initials"],
                    "avatar_color": da["avatar_color"],
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "reports": [
                        "techcorp_solutions_ltd._fy2025",
                        "apex_global_holdings_fy2024"
                    ],
                    "preferences": {
                        "default_length": "Standard",
                        "default_tone": "Professional"
                    }
                }
                modified = True

        if modified:
            self._save_users()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        target = email.strip().lower()
        for u in self.users.values():
            if u["email"].lower() == target:
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.users.get(user_id)

    def register(self, name: str, email: str, password: str, company: str = "", role: str = "Financial Analyst") -> Dict[str, Any]:
        """Register a new user account."""
        email = email.strip().lower()
        if not name or not email or not password:
            return {"success": False, "error": "Name, email, and password are required."}
        
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters long."}

        if self.get_user_by_email(email):
            return {"success": False, "error": "An account with this email already exists. Please log in."}

        # Generate avatar initials
        parts = name.strip().split()
        initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
        colors = [
            "from-blue-600 to-indigo-600",
            "from-purple-600 to-pink-600",
            "from-emerald-600 to-teal-600",
            "from-amber-500 to-orange-600",
            "from-cyan-600 to-blue-600"
        ]
        color = colors[len(self.users) % len(colors)]

        uid = str(uuid.uuid4())[:8]
        new_user = {
            "id": uid,
            "name": name.strip(),
            "email": email,
            "password_hash": generate_password_hash(password),
            "company": company.strip() or "Independent Analyst",
            "role": role.strip() or "Financial Analyst",
            "avatar_initials": initials,
            "avatar_color": color,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "reports": ["techcorp_solutions_ltd._fy2025"],
            "preferences": {
                "default_length": "Standard",
                "default_tone": "Professional"
            }
        }

        self.users[uid] = new_user
        self._save_users()

        # Create session token
        token = str(uuid.uuid4())
        self.sessions[token] = uid

        safe_user = self._get_safe_user(new_user)
        return {
            "success": True,
            "user": safe_user,
            "token": token,
            "message": f"Welcome aboard, {name}!"
        }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password."""
        email = email.strip().lower()
        user = self.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "No account found with this email. Please register."}

        if not check_password_hash(user["password_hash"], password):
            return {"success": False, "error": "Invalid password. Please check your credentials."}

        token = str(uuid.uuid4())
        self.sessions[token] = user["id"]

        safe_user = self._get_safe_user(user)
        return {
            "success": True,
            "user": safe_user,
            "token": token,
            "message": f"Welcome back, {user['name']}!"
        }

    def logout(self, token: str) -> bool:
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

    def get_user_from_token(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        uid = self.sessions.get(token)
        if not uid:
            return None
        user = self.get_user_by_id(uid)
        return self._get_safe_user(user) if user else None

    def add_user_report(self, user_id: str, report_id: str):
        """Add a generated report ID to the user's private report archive."""
        user = self.get_user_by_id(user_id)
        if user:
            if "reports" not in user:
                user["reports"] = []
            if report_id not in user["reports"]:
                user["reports"].append(report_id)
                self._save_users()

    def get_user_reports_count(self, user_id: str) -> int:
        user = self.get_user_by_id(user_id)
        if user:
            return len(user.get("reports", []))
        return 0

    def _get_safe_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Return user object sanitized of password hash."""
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "company": user.get("company", "Enterprise"),
            "role": user.get("role", "Financial Analyst"),
            "avatar_initials": user.get("avatar_initials", "FA"),
            "avatar_color": user.get("avatar_color", "from-blue-600 to-indigo-600"),
            "created_at": user.get("created_at"),
            "reports_count": len(user.get("reports", [])),
            "reports": user.get("reports", []),
            "preferences": user.get("preferences", {
                "default_length": "Standard",
                "default_tone": "Professional"
            })
        }
