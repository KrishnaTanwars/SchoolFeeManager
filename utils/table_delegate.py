"""
Custom PySide6 Table Item Delegate and Header View for Responsive Word-Wrapping and Dynamic Row Height Calculation.
Prevents text truncation, clipping, or cut-off labels across all ERP QTableWidgets.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QHeaderView
from PySide6.QtCore import Qt, QSize, QModelIndex
from PySide6.QtGui import QPainter, QTextDocument


class WordWrapItemDelegate(QStyledItemDelegate):
    """
    Custom PySide6 item delegate that automatically wraps text inside QTableWidget cells
    and dynamically calculates the exact row height needed to show full content without '...' or clipping.
    """
    def __init__(self, parent=None, padding_x: int = 10, padding_y: int = 8):
        super().__init__(parent)
        self.padding_x = padding_x
        self.padding_y = padding_y

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        # Draw selection/background highlight
        style = options.widget.style() if options.widget else None
        if style:
            style.drawPrimitive(style.PE_PanelItemViewItem, options, painter, options.widget)

        text = options.text
        if not text:
            return

        painter.save()

        # Check alignment
        alignment = index.data(Qt.TextAlignmentRole)
        if alignment is None:
            alignment = int(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            alignment = int(alignment)

        # Determine font color
        if options.state & options.State_Selected:
            painter.setPen(options.palette.highlightedText().color())
        else:
            painter.setPen(options.palette.text().color())

        painter.setFont(options.font)

        # Calculate bounding rect with padding
        rect = options.rect.adjusted(self.padding_x // 2, self.padding_y // 2, -self.padding_x // 2, -self.padding_y // 2)

        # Draw multi-line text with word wrapping
        flags = alignment | Qt.TextWordWrap
        painter.drawText(rect, flags, text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        text = options.text
        if not text:
            return super().sizeHint(option, index)

        # Determine available width from view column
        col_width = 150
        if options.widget and hasattr(options.widget, "columnWidth"):
            col_width = options.widget.columnWidth(index.column())

        usable_width = max(50, col_width - self.padding_x)

        doc = QTextDocument()
        doc.setDefaultFont(options.font)
        doc.setTextWidth(usable_width)
        doc.setPlainText(text)

        required_height = int(doc.size().height()) + self.padding_y
        min_height = max(36, required_height)

        return QSize(usable_width, min_height)


class WordWrapHeaderView(QHeaderView):
    """
    Custom QHeaderView that automatically wraps long table header text into multi-line headers.
    """
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)

    def sectionSizeFromContents(self, logicalIndex: int) -> QSize:
        model = self.model()
        if not model:
            return super().sectionSizeFromContents(logicalIndex)

        header_text = str(model.headerData(logicalIndex, self.orientation(), Qt.DisplayRole) or "")
        font = self.font()

        doc = QTextDocument()
        doc.setDefaultFont(font)

        col_width = self.sectionSize(logicalIndex)
        doc.setTextWidth(max(40, col_width - 8))
        doc.setPlainText(header_text)

        h = int(doc.size().height()) + 12
        w = int(doc.idealWidth()) + 16

        return QSize(max(50, w), max(38, h))


def apply_responsive_table_formatting(table, padding_x: int = 10, padding_y: int = 8):
    """
    Applies responsive word-wrapping and automatic row height expansion
    to a QTableWidget to prevent text clipping and truncation across all resolutions.
    """
    if not table:
        return

    table.setWordWrap(True)
    table.setTextElideMode(Qt.ElideNone)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap)

