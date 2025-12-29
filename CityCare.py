import sys
import random
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QTextEdit, QListWidget, QListWidgetItem, QTabWidget, QInputDialog, QLineEdit
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

# ====== Demo Data ======
history = []  # List of reports

# ====== Splash / Intro Screen ======
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CityCare")
        self.setStyleSheet("background-color: #e38da5;")
        self.showMaximized()  # <-- Open splash screen maximized

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title = QLabel("CityCare")
        self.title.setFont(QFont('Arial', 40, QFont.Weight.Bold))
        self.title.setStyleSheet("color:white;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        # Animated text
        self.animated_text = QLabel("")
        self.animated_text.setFont(QFont('Arial', 16))
        self.animated_text.setStyleSheet("color: white;")
        self.animated_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.animated_text)

        # Developer text (hidden initially)
        self.dev_text = QLabel("Developed by Riv")
        self.dev_text.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        self.dev_text.setStyleSheet("color:white;")
        self.dev_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dev_text.hide()
        layout.addWidget(self.dev_text)

        self.setLayout(layout)

        # Start simple timed animation
        self.start_animation()

    def start_animation(self):
        QTimer.singleShot(1000, lambda: self.animated_text.setText("A smart civic platform for reporting and managing city issues."))
        QTimer.singleShot(2500, self.show_dev_text)
        QTimer.singleShot(6000, self.launch_main_app)

    def show_dev_text(self):
        self.dev_text.show()

    def launch_main_app(self):
        self.main_window = CityCareApp()
        self.main_window.show()
        self.close()

# ====== CityCare Main App ======
class CityCareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CityCare - Smart Issue Reporter (Demo)")
        self.setStyleSheet("background-color: #f0f2f5;")
        self.image_path = None

        # Open main app maximized
        self.showMaximized()  # <-- Main window opens maximized

        # ----- Title & Quote -----
        title = QLabel("CityCare")
        title.setFont(QFont('Arial', 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        quote = QLabel("“We care for your city, just like you do!”")
        quote.setFont(QFont('Arial', 14))
        quote.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quote.setStyleSheet("color: #555555;")

        # ----- Tabs: Report / History / Help -----
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 30px; width: 140px; font-weight: bold; }")
        self.report_tab = QWidget()
        self.history_tab = QWidget()
        self.help_tab = QWidget()
        self.tabs.addTab(self.report_tab, "📝 Report")
        self.tabs.addTab(self.history_tab, "📜 History")
        self.tabs.addTab(self.help_tab, "❓ Help")

        # ----- Setup Tabs -----
        self.setup_report_tab()
        self.setup_history_tab()
        self.setup_help_tab()

        # ----- Overall Layout -----
        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(quote)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    # ====== Report Tab ======
    def setup_report_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Image Preview
        self.image_label = QLabel("No image selected")
        self.image_label.setFixedSize(500, 250)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border:2px solid #888; border-radius:10px; background-color:white;")
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Buttons: Upload / Take Photo
        button_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📷 Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)
        self.camera_btn = QPushButton("📸 Take Photo")
        self.camera_btn.clicked.connect(self.take_photo_mock)
        for btn in [self.upload_btn, self.camera_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size:16px;
                    padding:10px;
                    border-radius:8px;
                }
            """)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.camera_btn)
        layout.addLayout(button_layout)

        # Location Input
        loc_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter location manually")
        self.location_input.setFixedHeight(30)
        self.auto_btn = QPushButton("Auto Detect")
        self.auto_btn.clicked.connect(self.auto_detect_location)
        self.auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size:14px;
                padding:6px;
                border-radius:6px;
            }
        """)
        loc_layout.addWidget(self.location_input)
        loc_layout.addWidget(self.auto_btn)
        layout.addLayout(loc_layout)

        # Optional Text / Complaint
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Optional: Add a description or complaint...")
        self.text_edit.setFixedHeight(80)
        layout.addWidget(self.text_edit)

        # Send Button
        self.send_btn = QPushButton("🚀 Send Report")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color:white;
                font-size:16px;
                padding:12px;
                border-radius:8px;
            }
        """)
        self.send_btn.clicked.connect(self.send_report)
        layout.addWidget(self.send_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.report_tab.setLayout(layout)

    # ====== History Tab ======
    def setup_history_tab(self):
        layout = QVBoxLayout()
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        self.history_tab.setLayout(layout)
        self.refresh_history()

    # ====== Help Tab ======
    def setup_help_tab(self):
        layout = QVBoxLayout()
        help_label = QLabel(
            "How to use CityCare Demo:\n\n"
            "1. Upload or take a photo of the issue.\n"
            "2. Enter location manually or click 'Auto Detect'.\n"
            "3. Optionally write a description/complaint.\n"
            "4. Click 'Send Report' to register it.\n"
            "5. Switch to 'History' tab to see your reports, status, and resolution date.\n"
            "6. Once resolved, you can give feedback.\n"
            "7. Status updates are simulated for demo purposes."
        )
        help_label.setWordWrap(True)
        help_label.setFont(QFont('Arial', 12))
        layout.addWidget(help_label)
        self.help_tab.setLayout(layout)

    # ====== Upload / Camera Mock ======
    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name).scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

    def take_photo_mock(self):
        self.image_path = None
        self.image_label.setText("📸 Mock Camera Photo Taken")

    # ====== Auto Detect Location (Demo) ======
    def auto_detect_location(self):
        self.location_input.setText("Auto location detected (Demo)")

    # ====== Send Report ======
    def send_report(self):
        if not self.image_path and not self.text_edit.toPlainText():
            QMessageBox.warning(self, "Error", "Please upload/take a photo or enter a complaint.")
            return
        location = self.location_input.text() if self.location_input.text().strip() else "Location not provided"

        # Mock issue detection
        issue_types = ["Pothole", "Garbage", "Water Leak", "Broken Streetlight"]
        issue = random.choice(issue_types)
        text = self.text_edit.toPlainText()
        now = datetime.now()
        report_date = now.strftime("%Y-%m-%d %H:%M")

        # Add to history
        report = {
            "issue": issue,
            "text": text,
            "status": "Sent",
            "report_date": report_date,
            "resolved_date": None,
            "feedback": "",
            "location": location
        }
        history.append(report)
        self.refresh_history()

        # Show “Email Sent” message
        QMessageBox.information(self, "Demo", f"📧 Report Sent!\nIssue: {issue}\nReported on: {report_date}\nLocation: {location}")

        # Clear inputs
        self.text_edit.clear()
        self.image_label.setText("No image selected")
        self.image_path = None
        self.location_input.clear()

        # Simulate status updates
        QTimer.singleShot(7000, lambda: self.update_status(report, "Opened"))
        QTimer.singleShot(15000, lambda: self.update_status(report, "Resolved"))

    # ====== History Management ======
    def refresh_history(self):
        self.history_list.clear()
        for rep in history:
            status_text = rep["status"]
            report_date = rep["report_date"]
            resolved_date = rep["resolved_date"]
            feedback = rep["feedback"]
            location = rep["location"]

            if status_text == "Resolved":
                display = (f"✅ {rep['issue']}: {rep['text']}\n"
                           f"Reported: {report_date}\nResolved: {resolved_date}\n"
                           f"Location: {location}")
                if feedback:
                    display += f"\nFeedback: {feedback}"
            else:
                display = (f"{status_text} - {rep['issue']}: {rep['text']}\n"
                           f"Reported: {report_date}\nLocation: {location}")

            item = QListWidgetItem(display)
            self.history_list.addItem(item)

    def update_status(self, report, new_status):
        report["status"] = new_status
        if new_status == "Resolved":
            now = datetime.now()
            report["resolved_date"] = now.strftime("%Y-%m-%d %H:%M")
            # Ask for feedback
            text, ok = QInputDialog.getText(self, "Feedback", f"Issue '{report['issue']}' resolved! Provide feedback (optional):")
            if ok and text.strip():
                report["feedback"] = text.strip()
        self.refresh_history()

# ====== Run App ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())
