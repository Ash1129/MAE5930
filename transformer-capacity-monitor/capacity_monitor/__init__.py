"""Fixed-rules pipeline: log transformer loads and monitor capacity against limits (Tompkins County).

No AI model takes part in any statistic or decision; every pipeline step is deterministic. ai_explain.py is the
one exception: an optional, off-by-default Claude CLI rewrite of alert and summary text, for display only.
"""

__version__ = "0.1.0"
