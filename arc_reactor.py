"""
Arc Reactor UI - JARVIS-style visual indicator
Transparent floating window with pulsing blue glow
"""

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen
import sys
import math


class ArcReactorUI(QWidget):
    """
    JARVIS-style Arc Reactor visual indicator.
    Shows different states: idle, listening, processing, speaking, error
    """
    
    def __init__(self, size=300):
        super().__init__()
        self.size = size
        self.state = 'idle'
        self.pulse_value = 0
        self.rotation = 0
        self.drag_position = None
        self.init_ui()
        
        # Animation timer (60 fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60fps
    
    def init_ui(self):
        """Initialize the UI window"""
        # Frameless, transparent, always on top
        # Removed Tool flag to prevent hiding when clicking other windows
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Set size
        self.setFixedSize(self.size, self.size)
        
        # Position at bottom-right corner
        self.position_bottom_right()
        
        self.setWindowTitle("Jheevis Arc Reactor")
    
    def position_bottom_right(self):
        """Position window at bottom-right corner with margin"""
        screen = QApplication.primaryScreen().geometry()
        margin = 50
        x = screen.width() - self.size - margin
        y = screen.height() - self.size - margin
        self.move(x, y)
    
    def paintEvent(self, event):
        """Draw the Arc Reactor"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw based on current state
        if self.state == 'idle':
            self.draw_idle(painter)
        elif self.state == 'listening':
            self.draw_listening(painter)
        elif self.state == 'processing':
            self.draw_processing(painter)
        elif self.state == 'speaking':
            self.draw_speaking(painter)
        elif self.state == 'error':
            self.draw_error(painter)
    
    def draw_idle(self, painter):
        """Slow pulsing blue glow (resting state)"""
        center = self.rect().center()
        pulse = abs(self.pulse_value)
        
        # Outer glow
        self.draw_glow(painter, center, 120, pulse * 0.6, (100, 200, 255))
        
        # Middle ring
        self.draw_glow(painter, center, 80, pulse * 0.8, (120, 220, 255))
        
        # Core
        self.draw_glow(painter, center, 40, pulse, (150, 230, 255))
        
        # Center dot
        painter.setBrush(QColor(200, 240, 255, int(255 * pulse)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 15, 15)
    
    def draw_listening(self, painter):
        """Active ripples (listening for input)"""
        center = self.rect().center()
        
        # Multiple expanding ripples
        for i in range(3):
            offset = (self.rotation + i * 40) % 120
            radius = 40 + offset
            alpha = 1.0 - (offset / 120)
            
            self.draw_glow(painter, center, radius, alpha * 0.7, (100, 220, 255))
        
        # Bright core
        self.draw_glow(painter, center, 30, 0.9, (150, 240, 255))
        painter.setBrush(QColor(200, 250, 255, 230))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 12, 12)
    
    def draw_processing(self, painter):
        """Rotating rings (processing/thinking)"""
        center = self.rect().center()
        
        # Draw rotating arc segments
        for i in range(6):
            angle = (self.rotation + i * 60) % 360
            self.draw_arc_segment(painter, center, 90, angle, 40, (100, 210, 255))
        
        # Inner core pulse
        pulse = abs(self.pulse_value)
        self.draw_glow(painter, center, 50, pulse * 0.8, (120, 230, 255))
        
        # Center
        painter.setBrush(QColor(180, 240, 255, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 18, 18)
    
    def draw_speaking(self, painter):
        """Pulsing with speech (talking) - JARVIS-style with expanding rings and rotation"""
        center = self.rect().center()
        pulse = abs(self.pulse_value)
        
        # Fast pulse
        large_pulse = 0.7 + (pulse * 0.3)
        
        # Expanding sound wave rings (like ripples from speaking)
        for i in range(4):
            offset = (self.rotation * 1.5 + i * 30) % 120
            radius = 50 + offset
            alpha = 1.0 - (offset / 120)
            
            self.draw_glow(painter, center, radius, alpha * 0.6, (110, 230, 255))
        
        # Rotating energy arcs (shows active processing/speaking)
        for i in range(8):
            angle = (self.rotation * 2 + i * 45) % 360
            self.draw_arc_segment(painter, center, 80, angle, 30, (120, 240, 255))
        
        # Pulsing middle layer
        self.draw_glow(painter, center, 60, large_pulse * 0.9, (130, 235, 255))
        
        # Core - bright and active with strong pulse
        core_pulse = 0.8 + (pulse * 0.2)
        self.draw_glow(painter, center, 35, core_pulse, (160, 245, 255))
        
        # Bright center dot
        painter.setBrush(QColor(230, 250, 255, int(255 * large_pulse)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(22 * core_pulse), int(22 * core_pulse))
    
    def draw_error(self, painter):
        """Red pulse (error state)"""
        center = self.rect().center()
        pulse = abs(self.pulse_value)
        
        # Red glow
        self.draw_glow(painter, center, 100, pulse * 0.6, (255, 100, 100))
        self.draw_glow(painter, center, 60, pulse * 0.8, (255, 120, 120))
        
        painter.setBrush(QColor(255, 150, 150, int(220 * pulse)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 25, 25)
    
    def draw_glow(self, painter, center, radius, intensity, color):
        """Draw a radial glow effect"""
        gradient = QRadialGradient(QPointF(center), radius)
        r, g, b = color
        
        gradient.setColorAt(0, QColor(r, g, b, int(200 * intensity)))
        gradient.setColorAt(0.5, QColor(r, g, b, int(120 * intensity)))
        gradient.setColorAt(1, QColor(r, g, b, 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, int(radius), int(radius))
    
    def draw_arc_segment(self, painter, center, radius, start_angle, span_angle, color):
        """Draw a rotating arc segment"""
        r, g, b = color
        pen = QPen(QColor(r, g, b, 180))
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw arc
        rect_size = radius * 2
        x = center.x() - radius
        y = center.y() - radius
        painter.drawArc(int(x), int(y), rect_size, rect_size, start_angle * 16, span_angle * 16)
    
    def update_animation(self):
        """Update animation values each frame"""
        if self.state == 'idle':
            # Slow sine wave pulse (2 second cycle)
            self.pulse_value = (math.sin(self.rotation * 0.03) + 1) / 2
            self.rotation += 1
        
        elif self.state == 'listening':
            # Medium speed pulse
            self.pulse_value = (math.sin(self.rotation * 0.08) + 1) / 2
            self.rotation += 2
        
        elif self.state == 'processing':
            # Fast rotation
            self.pulse_value = (math.sin(self.rotation * 0.05) + 1) / 2
            self.rotation += 5
        
        elif self.state == 'speaking':
            # Fast pulse and rotation for energetic speaking animation
            self.pulse_value = (math.sin(self.rotation * 0.2) + 1) / 2
            self.rotation += 4
        
        elif self.state == 'error':
            # Urgent pulse
            self.pulse_value = (math.sin(self.rotation * 0.2) + 1) / 2
            self.rotation += 4
        
        # Keep rotation manageable
        if self.rotation > 3600:
            self.rotation = 0
        
        self.update()  # Trigger repaint
    
    def set_state(self, state: str):
        """
        Change Arc Reactor state
        
        Args:
            state: 'idle', 'listening', 'processing', 'speaking', 'error'
        """
        valid_states = ['idle', 'listening', 'processing', 'speaking', 'error']
        if state in valid_states:
            self.state = state
        else:
            print(f"Warning: Invalid state '{state}'. Use: {valid_states}")
    
    def mousePressEvent(self, event):
        """Make window draggable"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.pos()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to cycle through states (for testing)"""
        states = ['idle', 'listening', 'processing', 'speaking', 'error']
        current_idx = states.index(self.state)
        next_state = states[(current_idx + 1) % len(states)]
        self.set_state(next_state)
        print(f"Arc Reactor: {next_state}")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    reactor = ArcReactorUI(size=300)
    reactor.show()
    
    print("=" * 60)
    print("Arc Reactor UI Test")
    print("=" * 60)
    print("Controls:")
    print("  - Double-click to cycle through states")
    print("  - Drag to move window")
    print("  - Close window to exit")
    print()
    print("States: idle → listening → processing → speaking → error")
    print("=" * 60)
    
    sys.exit(app.exec())
