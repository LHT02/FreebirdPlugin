from dataclasses import dataclass, field


@dataclass
class RuntimeState:
    draw_into_active_curve: bool = False
    draw_target: object = None
    draw_radius: float = 1.0
    falloff_entries: dict = field(default_factory=dict)
    falloff_session: tuple = None
    joystick_timestamps: dict = field(default_factory=dict)

    def reset_transform(self):
        self.falloff_entries.clear()
        self.falloff_session = None
        self.joystick_timestamps.clear()

    def reset(self):
        self.draw_into_active_curve = False
        self.draw_target = None
        self.draw_radius = 1.0
        self.reset_transform()


runtime = RuntimeState()
