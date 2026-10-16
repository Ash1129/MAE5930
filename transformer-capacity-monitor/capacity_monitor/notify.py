"""Failure alerts. Always recorded in the store (visible in the app); e-mailed when SMTP is configured.

Configure by environment variables, never in code:
  CAPMON_ALERT_TO, CAPMON_SMTP_HOST, CAPMON_SMTP_PORT (default 587), CAPMON_SMTP_USER, CAPMON_SMTP_PASSWORD, CAPMON_SMTP_FROM
"""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from .guards import redact_pii
from .store import Store


def send_alert(store: Store, level: str, message: str, run_id=None, period_id=None, step=None) -> int:
    message = redact_pii(message)
    delivered = "app only (no CAPMON_ALERT_TO configured)"
    to = os.environ.get("CAPMON_ALERT_TO")
    host = os.environ.get("CAPMON_SMTP_HOST")
    if to and host:
        try:
            msg = EmailMessage()
            msg["Subject"] = f"[Capacity Monitor] {level.upper()} run {run_id or '-'} period {period_id or '-'} step {step or '-'}"
            msg["From"] = os.environ.get("CAPMON_SMTP_FROM", os.environ.get("CAPMON_SMTP_USER", "capacity-monitor@localhost"))
            msg["To"] = to
            msg.set_content(f"Run: {run_id}\nPeriod: {period_id}\nStep: {step}\n\n{message}\n")
            port = int(os.environ.get("CAPMON_SMTP_PORT", "587"))
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.starttls()
                user, pw = os.environ.get("CAPMON_SMTP_USER"), os.environ.get("CAPMON_SMTP_PASSWORD")
                if user and pw:
                    s.login(user, pw)
                s.send_message(msg)
            delivered = f"email to {to}"
        except Exception as exc:  # alert delivery failure must not hide the run failure
            delivered = f"email failed: {exc!r}; recorded in app"
    return store.add_alert(level, message, run_id=run_id, period_id=period_id, step=step, delivered=delivered)
