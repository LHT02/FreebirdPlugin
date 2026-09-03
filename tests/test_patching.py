import unittest

from freebird_curve_editor.patching import PatchRegistry


class FakeOwner:
    value = "original"


class FakeEventTarget:
    def __init__(self):
        self.event_listeners = {}

    def add_event_listener(self, event_name, callback, options=None):
        self.event_listeners.setdefault(event_name, []).append((callback, options or {}))

    def remove_event_listener(self, event_name, callback=None, options=None):
        listeners = self.event_listeners.get(event_name, [])
        if callback is None:
            self.event_listeners.pop(event_name, None)
            return
        self.event_listeners[event_name] = [(fn, opts) for fn, opts in listeners if fn is not callback]


class PatchRegistryTests(unittest.TestCase):
    def test_restores_attribute(self):
        owner = FakeOwner()
        registry = PatchRegistry()
        replacement = object()
        registry.replace_attribute(owner, "value", replacement)
        self.assertIs(owner.value, replacement)
        registry.restore()
        self.assertEqual(owner.value, "original")

    def test_restores_replaced_listener_and_removes_added_listener(self):
        target = FakeEventTarget()

        def original(*_):
            pass

        def replacement(*_):
            pass

        def added(*_):
            pass

        target.add_event_listener("event", original, {"tag": "original"})
        registry = PatchRegistry()
        self.assertEqual(registry.replace_listener(target, "event", original, replacement), 1)
        registry.add_listener(target, "event", added)
        registry.restore()

        listeners = target.event_listeners["event"]
        self.assertEqual(len(listeners), 1)
        self.assertIs(listeners[0][0], original)
        self.assertEqual(listeners[0][1], {"tag": "original"})


if __name__ == "__main__":
    unittest.main()
