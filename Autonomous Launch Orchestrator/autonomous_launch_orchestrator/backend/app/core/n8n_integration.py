import os
import requests
from typing import Dict, Any

class N8NIntegration:
    def __init__(self, n8n_base_url: str = "http://localhost:5678"):
        self.base_url = n8n_base_url.rstrip("/")

    def _resolve_webhook_url(self, name_or_url: str) -> str:
        # Full URL passed
        if name_or_url.startswith("http://") or name_or_url.startswith("https://"):
            return name_or_url
        # Env override (e.g., N8N_WEBHOOK_MARKETING_GENERAL)
        env_key = f"N8N_WEBHOOK_{name_or_url.upper()}"
        env_val = os.getenv(env_key)
        if env_val:
            return env_val
        # Fallback to base_url + /webhook/{slug}
        return f"{self.base_url}/webhook/{name_or_url}"

    def trigger_workflow(self, workflow_name_or_url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an n8n workflow via webhook"""
        webhook_url = self._resolve_webhook_url(workflow_name_or_url)
        try:
            resp = requests.post(webhook_url, json=data, timeout=30)
            ok = 200 <= resp.status_code < 300
            return {
                "status": "success" if ok else "error",
                "status_code": resp.status_code,
                "response": (resp.json() if resp.content else None),
                "url": webhook_url,
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None),
                "url": webhook_url,
            }

    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        return {"status": "completed", "execution_id": execution_id}

    def map_task_to_workflow(self, role: str, task_type: str) -> str:
        key = (role or "general").strip().lower()
        mapping = {
            "marketing": {"default": "marketing_general"},
            "developer": {"default": "developer_general"},
            "sales": {"default": "sales_general"},
            "legal": {"default": "legal_general"},
        }
        role_map = mapping.get(key, {"default": "general_workflow"})
        return role_map.get(task_type, role_map["default"])

