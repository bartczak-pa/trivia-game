class AppInterface:
    def __init__(self) -> None: ...
    def mainloop(self) -> None: ...
    def title(self, title: str) -> None: ...
    def geometry(self, geometry: str) -> None: ...
    def pack(self, fill: str, expand: bool) -> None: ...
    def show_frame(self, frame_class: type[ctk.CTkFrame]) -> None: ...
    container: CTkFrame
    frames: dict
    app: AppInterface
    ctk: module
    super: module
    self: AppInterface
    title: module
    geometry: module
    pack: module
    CTkFrame: module
    dict: module
    module: module
    bool: module
    str: module
    AppInterface: module
