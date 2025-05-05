from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator, QValidator


class IntValidator(QIntValidator):
    validationChanged = Signal(QValidator.State)

    def validate(self, _input, _pos):
        state, _input, _pos = super().validate(_input, _pos)
        self.validationChanged.emit(state)

        return state, _input, _pos
