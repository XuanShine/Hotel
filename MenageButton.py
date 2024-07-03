from nicegui import ui

class MenageButton(ui.button_group):

    def __init__(self, *args, state=False, **kwargs) -> None:
        self._state = state
        super().__init__(*args, **kwargs)
        
        self.on('click', self.toggle)

    def toggle(self) -> None:
        """Toggle the button state."""
        self._state = not self._state
        self.update()

    def update(self) -> None:
        self.props(f'color={"blue" if self._state else "grey"}')
        super().update()