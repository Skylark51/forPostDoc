from __future__ import annotations


def detach_reaction_editor(widget) -> None:
    """Disconnect scene callbacks before Qt destroys the underlying C++ objects."""
    scene = getattr(widget, "scene", None)
    view = getattr(widget, "view", None)
    if scene is None:
        return
    try:
        scene.selectionChanged.disconnect(widget._selection_changed)
    except (RuntimeError, TypeError):
        pass
    try:
        scene.model_changed.disconnect(widget._model_changed)
    except (RuntimeError, TypeError):
        pass
    if view is not None:
        try:
            view.setScene(None)
        except RuntimeError:
            pass
