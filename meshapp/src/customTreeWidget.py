
from PySide6.QtWidgets import ( QTreeWidget)
from PySide6.QtCore import Qt

class MyTreeWidget(QTreeWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
            self.setCurrentItem(None)  # Removes the dotted focus rect
            event.accept()             # Mark event as handled
        else:
            # Pass all other keys (arrows, etc.) to the base class
            super().keyPressEvent(event)
