import sys
import random
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

DATA_FILE = "citycare_data.json"
history = []
CURRENT_ROLE = "Citizen"

STYLE = """
QWidget {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #0b1220,
        stop:0.5 #0f172a,
        stop:1 #0b1220
    );
    color: #e5e7eb;
    font-family: Segoe UI, Inter;
}

/* SCROLLBAR */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 20px 0 20px 0;
}

QScrollBar::handle:vertical {
    background: rgba(124,58,237,0.6);
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(124,58,237,0.9);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* HERO */
QLabel#HeroTitle {
    font-size: 64px;
    font-weight: 800;
}

QLabel#HeroSubtitle {
    font-size: 18px;
    color: #94a3b8;
}

/* CARD */
QFrame#Card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px;
    padding: 50px;
}

/* SECTION LABEL */
QLabel#SectionLabel {
    font-size: 13px;
    color: #94a3b8;
    font-weight: 600;
}

/* PRIMARY BUTTON */
QPushButton#Primary {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed,
        stop:1 #9333ea
    );
    border-radius: 16px;
    padding: 14px 32px;
    font-weight: 600;
}

QPushButton#Secondary {
    background: rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 12px 22px;
    border: 1px solid rgba(255,255,255,0.08);
}

QLineEdit, QTextEdit, QComboBox {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 14px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #7c3aed;
}

QTabWidget::pane { border: none; }

QTabBar::tab {
    background: transparent;
    padding: 14px 26px;
    font-weight: 600;
    color: #94a3b8;
}

QTabBar::tab:selected {
    color: white;
    border-bottom: 3px solid #7c3aed;
}
"""

class AnimatedButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("Primary")

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setColor(QColor("#7c3aed"))
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)

        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(250)

    def enterEvent(self, event):
        self.anim.setStartValue(0)
        self.anim.setEndValue(30)
        self.anim.start()

    def leaveEvent(self, event):
        self.anim.setStartValue(30)
        self.anim.setEndValue(0)
        self.anim.start()


class UploadArea(QLabel):
    def __init__(self):
        super().__init__("Drop image here\nor click Upload")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(200)
        self.setStyleSheet("""
            border: 2px dashed rgba(255,255,255,0.15);
            border-radius: 20px;
            background: rgba(255,255,255,0.03);
        """)


class RoleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.selected_role = None
        self.setWindowTitle("CityCare Access")
        self.setFixedSize(420, 300)
        self.setModal(True)

        self.setStyleSheet("""
        QDialog {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #0b1220,
                stop:1 #0f172a
            );
            color: #e5e7eb;
            font-family: Segoe UI, Inter;
        }

        QLabel#Title {
            font-size: 26px;
            font-weight: 800;
        }

        QLabel#Subtitle {
            font-size: 14px;
            color: #94a3b8;
        }

        QPushButton {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 16px;
            font-size: 16px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: rgba(124,58,237,0.2);
            border: 1px solid #7c3aed;
        }

        QPushButton:pressed {
            background: rgba(124,58,237,0.35);
        }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Welcome to CityCare")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Select how you want to continue")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        citizen_btn = QPushButton("Continue as Citizen")
        authority_btn = QPushButton("Login as Authority")

        citizen_btn.clicked.connect(lambda: self.select_role("Citizen"))
        authority_btn.clicked.connect(lambda: self.select_role("Authority"))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(citizen_btn)
        layout.addWidget(authority_btn)

    def select_role(self, role):
        self.selected_role = role
        self.accept()

    def get_role(self):
        return self.selected_role


class CityCare(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CityCare")
        self.resize(1200, 900)
        self.setStyleSheet(STYLE)

        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(50)
        layout.setContentsMargins(0, 50, 0, 50)

        wrapper = QWidget()
        wrapper.setMaximumWidth(1100)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setSpacing(40)

        hero = QVBoxLayout()
        title = QLabel("Report first.\nFix faster.")
        title.setObjectName("HeroTitle")

        subtitle = QLabel("CityCare helps you report civic issues instantly and transparently.")
        subtitle.setObjectName("HeroSubtitle")

        cta = AnimatedButton("Start Reporting")
        hero.addWidget(title)
        hero.addWidget(subtitle)
        hero.addWidget(cta)

        wrapper_layout.addLayout(hero)

        self.tabs = QTabWidget()
        self.report_tab = QWidget()
        self.history_tab = QWidget()
        self.help_tab = QWidget()

        self.tabs.addTab(self.report_tab, "Report")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.help_tab, "Help")

        wrapper_layout.addWidget(self.tabs)
        layout.addWidget(wrapper)

        self.setup_report()
        self.setup_history()
        self.setup_help()

        self.load_data()
        self.refresh_history()

    def load_data(self):
        global history
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    history = json.load(f)
            except:
                history = []
        else:
            history = []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(history, f, indent=4)

    def setup_report(self):
        layout = QVBoxLayout(self.report_tab)
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        self.image_label = UploadArea()
        upload = QPushButton("Upload Image")
        upload.setObjectName("Secondary")
        upload.clicked.connect(self.upload_image)

        self.issue = QComboBox()
        self.issue.addItems(["Pothole", "Garbage", "Leakage", "Road Damage", "Streetlight"])

        self.location = QLineEdit()
        self.location.setPlaceholderText("Enter Location")

        auto = QPushButton("Auto Detect")
        auto.setObjectName("Secondary")
        auto.clicked.connect(self.auto_location)

        loc_layout = QHBoxLayout()
        loc_layout.addWidget(self.location)
        loc_layout.addWidget(auto)

        self.desc = QTextEdit()
        self.desc.setFixedHeight(100)

        submit = AnimatedButton("Submit Report")
        submit.clicked.connect(self.submit_report)

        card_layout.addWidget(self.image_label)
        card_layout.addWidget(upload)
        card_layout.addWidget(self.issue)
        card_layout.addLayout(loc_layout)
        card_layout.addWidget(self.desc)
        card_layout.addWidget(submit)

        layout.addWidget(card)

    def setup_history(self):
        layout = QVBoxLayout(self.history_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Your Submitted Reports")
        title.setStyleSheet("font-size:24px; font-weight:700;")
        layout.addWidget(title)

        subtitle = QLabel("Track progress and status of your civic complaints.")
        subtitle.setStyleSheet("color:#94a3b8;")
        layout.addWidget(subtitle)

        legend = QLabel("🟡 Sent   |   🔵 In Progress   |   🟢 Resolved")
        legend.setStyleSheet("color:#94a3b8; font-size:13px;")
        layout.addWidget(legend)

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

    def setup_help(self):
        layout = QVBoxLayout(self.help_tab)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("How CityCare Works")
        title.setStyleSheet("font-size:24px; font-weight:700;")
        layout.addWidget(title)

        info = QLabel("Use the Report tab to submit issues.\nAuthorities manage them from History.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#94a3b8;")
        layout.addWidget(info)

    def upload_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg)")
        if file:
            pix = QPixmap(file).scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(pix)

    def auto_location(self):
        self.location.setText(random.choice(["Indore", "Delhi", "Mumbai", "Bhopal"]))

    def submit_report(self):
        if CURRENT_ROLE != "Citizen":
            return

        report = {
            "id": len(history) + 1,
            "issue": self.issue.currentText(),
            "location": self.location.text() or "Not provided",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Sent"
        }

        history.append(report)
        self.save_data()
        self.refresh_history()
        self.desc.clear()
        self.location.clear()

    def refresh_history(self):
        self.history_list.clear()

        for index, r in enumerate(history):

            if r["status"] == "Resolved":
                icon = "🟢"
            elif r["status"] == "In Progress":
                icon = "🔵"
            else:
                icon = "🟡"

            item = QListWidgetItem(
                f"{icon} #{r.get('id', index+1)} • {r['issue']} • {r['location']} • {r['date']}"
            )
            self.history_list.addItem(item)

            if CURRENT_ROLE == "Authority":
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(0, 0, 0, 0)

                btn1 = QPushButton("In Progress")
                btn2 = QPushButton("Resolve")

                btn1.clicked.connect(lambda _, i=index: self.update_status(i, "In Progress"))
                btn2.clicked.connect(lambda _, i=index: self.update_status(i, "Resolved"))

                layout.addWidget(btn1)
                layout.addWidget(btn2)

                item.setSizeHint(widget.sizeHint())
                self.history_list.setItemWidget(item, widget)

    def update_status(self, index, status):
        if CURRENT_ROLE != "Authority":
            return

        history[index]["status"] = status
        self.save_data()
        self.refresh_history()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    role_dialog = RoleDialog()
    if role_dialog.exec():
        CURRENT_ROLE = role_dialog.get_role()
        window = CityCare()
        window.show()
        sys.exit(app.exec())
