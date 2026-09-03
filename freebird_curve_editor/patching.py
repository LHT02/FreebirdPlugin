class PatchRegistry:
    def __init__(self):
        self._attribute_patches = []
        self._listener_patches = []
        self._added_listeners = []

    def replace_attribute(self, owner, name, replacement):
        original = getattr(owner, name)
        self._attribute_patches.append((owner, name, original, replacement))
        setattr(owner, name, replacement)
        return original

    def replace_listener(self, target, event_name, original, replacement):
        listeners = getattr(target, "event_listeners", {}).get(event_name, [])
        count = 0
        for index, (callback, options) in enumerate(listeners):
            if callback is original:
                listeners[index] = (replacement, options)
                count += 1
        if count:
            self._listener_patches.append((target, event_name, original, replacement))
        return count

    def add_listener(self, target, event_name, callback, options=None):
        options = options or {}
        target.add_event_listener(event_name, callback, options)
        self._added_listeners.append((target, event_name, callback))

    def restore(self):
        for target, event_name, callback in reversed(self._added_listeners):
            target.remove_event_listener(event_name, callback)
        self._added_listeners.clear()

        for target, event_name, original, replacement in reversed(self._listener_patches):
            listeners = getattr(target, "event_listeners", {}).get(event_name, [])
            for index, (callback, options) in enumerate(listeners):
                if callback is replacement:
                    listeners[index] = (original, options)
        self._listener_patches.clear()

        for owner, name, original, replacement in reversed(self._attribute_patches):
            if getattr(owner, name, None) is replacement:
                setattr(owner, name, original)
        self._attribute_patches.clear()
