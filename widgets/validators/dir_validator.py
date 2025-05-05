from PySide6.QtCore import Signal, QDir
from PySide6.QtGui import QValidator


class DirValidator(QValidator):
    validationChanged = Signal(QValidator.State)

    def validate(self, _input, _pos):
        _dir = QDir(_input)

        if _dir.exists():
            state = QValidator.State.Acceptable
        else:
            state = QValidator.State.Intermediate
        self.validationChanged.emit(state)

        return state, _input, _pos
