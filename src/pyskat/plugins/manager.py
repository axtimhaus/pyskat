from pluggy import PluginManager, HookspecMarker, HookimplMarker

NAME = "pyskat"

plugin_manager = PluginManager(NAME)
"""The pluggy plugin manager used for pyskat."""

hookspec = HookspecMarker(NAME)
"""Decorator to declare a hook specification."""

hookimpl = HookimplMarker(NAME)
"""Decorator to declare a hook implementation."""
