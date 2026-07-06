"""
knowledge/kb_docs.py

The help-center knowledge base. In production this comes from your real
help docs / resolved-ticket archive; here it's a small hand-written set
matching the topics used in ingestion/case_generator.py so retrieval
accuracy can be validated against known ground truth.
"""

KB_DOCS = {
    "double_charge_refund": (
        "If you were charged twice for the same billing period, this is usually caused by a "
        "retried payment after a temporarily declined card. Refunds for duplicate charges are "
        "processed automatically within 3-5 business days. If you don't see it, contact billing support."
    ),
    "update_payment_method": (
        "To update your credit card on file, go to Account Settings > Billing > Payment Methods, "
        "then select 'Add New Card' and remove the old one. Changes apply to your next billing cycle."
    ),
    "export_crash": (
        "Export crashes are most commonly caused by a corrupted temp cache file. Clear the app cache "
        "from Settings > Storage > Clear Cache, restart the app, and try exporting again."
    ),
    "data_loss": (
        "If data appears to have disappeared after an update, it is very likely a sync delay rather "
        "than actual data loss. Data is recoverable from the last automatic backup within 30 days. "
        "This is treated as a critical issue and escalated to the data recovery team."
    ),
    "reset_password": (
        "To reset your password, click 'Forgot Password' on the login screen and follow the emailed "
        "reset link. Reset links expire after 30 minutes."
    ),
    "change_email": (
        "To change your account email, go to Account Settings > Profile > Email, enter the new address, "
        "and confirm via the verification email sent to the new address."
    ),
    "cannot_login": (
        "Invalid credentials errors are usually caused by an expired session or a recent password change "
        "on another device. Try resetting your password. If the issue persists after reset, your account "
        "may be temporarily locked after multiple failed attempts."
    ),
    "account_compromised": (
        "If you believe your account is compromised, this is treated as a critical security issue. "
        "Immediately reset your password from a trusted device and contact security support to review "
        "recent login activity and revoke active sessions."
    ),
}
