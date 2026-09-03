fb_info = {"name": "Freebird Curve Editor"}


def register():
    from .lifecycle import register_plugin

    register_plugin()


def unregister():
    from .lifecycle import unregister_plugin

    unregister_plugin()
