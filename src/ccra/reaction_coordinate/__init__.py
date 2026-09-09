"""Project-scoped reaction-coordinate data model and editor package.

GUI modules are intentionally not imported at package import time so that model,
storage and layout utilities remain usable in headless environments.
"""
from .models import Diagram, DiagramEdge, DiagramNode

__all__ = ["Diagram", "DiagramEdge", "DiagramNode"]
