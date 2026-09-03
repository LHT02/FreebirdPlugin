from dataclasses import dataclass, field


@dataclass
class RuntimeState:
    draw_into_active_curve: bool = False
    draw_target: object = None
    draw_radius: float = 1.0
    falloff_entries: dict = field(default_factory=dict)
    falloff_session: tuple = None
    twist_axes: dict = field(default_factory=dict)
    joystick_timestamps: dict = field(default_factory=dict)
    add_point_start_position: object = None
    add_point_last_position: object = None
    add_point_count: int = 0

    def reset_transform(self):
        self.falloff_entries.clear()
        self.falloff_session = None
        self.twist_axes.clear()
        self.joystick_timestamps.clear()

    def reset_add_point(self):
        self.add_point_start_position = None
        self.add_point_last_position = None
        self.add_point_count = 0

    def reset(self):
        self.draw_into_active_curve = False
        self.draw_target = None
        self.draw_radius = 1.0
        self.reset_transform()
        self.reset_add_point()


runtime = RuntimeState()
