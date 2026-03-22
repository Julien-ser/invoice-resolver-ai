"""
A/B Testing package for experiment management and analysis.
"""

from .experiment import (
    ExperimentManager,
    assign_variant_to_campaign,
    track_email_open,
    analyze_experiment,
)

__all__ = [
    "ExperimentManager",
    "assign_variant_to_campaign",
    "track_email_open",
    "analyze_experiment",
]
