import sys, random, time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QTextEdit, QListWidget, QListWidgetItem,
    QTabWidget, QLineEdit, QFrame, QComboBox, QScrollArea, QDialog,
    QFormLayout, QSpinBox, QInputDialog
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

# ================= Demo Storage =================
history = []
profile_data = {"Name": "", "Surname": "", "Age": "", "Location": ""}

# ================= Premium Styles =================
BASE_STYLE = """
QWidget {{
    background-color: {bg};
    font-family: Inter, Arial;
    color: {fg};
}}
QLabel#Title {{
    font-size: 34px;
    font-weight: 700;
}}
QLabel#Subtitle {{
    font-size: 14px;
    color: {sub};
}}
QFrame#Card {{
    background: {card_bg};
    border-radius: 14px;
    padding: 18px;
}}
QPushButton {{
    background-color: {btn_bg};
    color: {btn_fg};
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 14px;
}}
QPushButton:hover {{
    background-color: {btn_hover};
}}
QPushButton#Secondary {{
    background-color: {sec_bg};
    color: {sec_fg};
}}
QLineEdit, QTextEdit, QComboBox {{
    background: {input_bg};
    border: 1px solid {input_border};
    border-radius: 10px;
    padding: 10px;
}}
QTabWidget::pane {{
    border: none;
}}
QTabBar::tab {{
    background: transparent;
    padding: 10px 20px;
    font-weight: 600;
    color: {tab_inactive};
}}
QTabBar::tab:selected {{
    color: {tab_active};
    border-bottom: 3px solid {tab_active};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: {scroll};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

THEMES = {
    "Night Pink": {
        "bg": "#1a0f1a","fg": "#ffe6f0","sub": "#ffb3d9","card_bg": "#2d132d",
        "btn_bg": "#ff66b3","btn_hover": "#e0559c","btn_fg": "white",
        "sec_bg": "#3a1f3a","sec_fg": "#ffe6f0","input_bg": "#2d132d","input_border": "#ff66b3",
        "tab_active": "#ff66b3","tab_inactive": "#ffb3d9","scroll": "#ff66b3"
    },
    "Blue Panther": {
        "bg": "#0d1f2d","fg": "#cce7ff","sub": "#99cfff","card_bg": "#123447",
        "btn_bg": "#3399ff","btn_hover": "#287acc","btn_fg": "white",
        "sec_bg": "#1b3b5c","sec_fg": "#cce7ff","input_bg": "#123447","input_border": "#3399ff",
        "tab_active": "#3399ff","tab_inactive": "#99cfff","scroll": "#3399ff"
    },
    "Cream White": {
        "bg": "#f6f7fb","fg": "#1f2937","sub": "#6b7280","card_bg": "white",
        "btn_bg": "#2563eb","btn_hover": "#1e40af","btn_fg": "white",
        "sec_bg": "#e5e7eb","sec_fg": "#111827","input_bg": "#f9fafb","input_border": "#e5e7eb",
        "tab_active": "#2563eb","tab_inactive": "#6b7280","scroll": "#2563eb"
    }
}

current_theme = "Cream White"

def apply_theme(widget, theme_name):
    global current_theme
    current_theme = theme_name
    theme = THEMES[theme_name]
    widget.setStyleSheet(BASE_STYLE.format(**theme))

# ================= Splash =================
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:#111827; color:white;")
        self.showMaximized()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("CityCare")
        title.setFont(QFont("Inter", 40, QFont.Weight.Bold))
        subtitle = QLabel("A smarter way to care for your city")
        subtitle.setStyleSheet("color:#9ca3af; font-size:16px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        QTimer.singleShot(2500, self.launch)
    def launch(self):
        self.main = CityCareApp()
        apply_theme(self.main, current_theme)
        self.main.show()
        self.close()

# ================= Main App =================
class CityCareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CityCare")
        self.showMaximized()
        self.image_path = None
        # Header
        title = QLabel("CityCare")
        title.setObjectName("Title")
        subtitle = QLabel("Report civic issues quickly & transparently")
        subtitle.setObjectName("Subtitle")
        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)
        # ⚙️ Settings Button
        header_layout = QHBoxLayout()
        header_layout.addLayout(header)
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setStyleSheet("font-size:18px;")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)
        # Tabs
        self.tabs = QTabWidget()
        self.report_tab = QWidget()
        self.history_tab = QWidget()
        self.help_tab = QWidget()
        self.tabs.addTab(self.report_tab, "Report Issue")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.help_tab, "Help")
        self.setup_report_tab()
        self.setup_history_tab()
        self.setup_help_tab()
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 30, 40, 30)
        main.setSpacing(25)
        main.addLayout(header_layout)
        main.addWidget(self.tabs)
        apply_theme(self, current_theme)

    # ================= Settings =================
    def open_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("⚙️ Settings")
        settings_btn = QPushButton("⚙️")
        layout = QVBoxLayout(dlg)
        profile_btn = QPushButton("👤 Profile")
        profile_btn.clicked.connect(self.open_profile)
        layout.addWidget(profile_btn)
        theme_btn = QPushButton("🎨 Theme Change")
        theme_btn.clicked.connect(self.change_theme)
        layout.addWidget(theme_btn)
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.clicked.connect(lambda: QMessageBox.information(self, "Logout", "Logged out!"))
        layout.addWidget(logout_btn)
        dlg.exec()

    # ================= Profile =================
    def open_profile(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Profile")
        layout = QFormLayout(dlg)
        name_input = QLineEdit(profile_data["Name"])
        surname_input = QLineEdit(profile_data["Surname"])
        age_input = QSpinBox()
        age_input.setRange(1,120)
        age_input.setValue(int(profile_data["Age"] or 18))
        location_input = QLineEdit(profile_data["Location"])
        layout.addRow("Name:",name_input)
        layout.addRow("Surname:",surname_input)
        layout.addRow("Age:",age_input)
        layout.addRow("Location:",location_input)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_profile(name_input,surname_input,age_input,location_input,dlg))
        layout.addRow(save_btn)
        dlg.exec()
    def save_profile(self,name,surname,age,location,dialog):
        profile_data["Name"]=name.text()
        profile_data["Surname"]=surname.text()
        profile_data["Age"]=str(age.value())
        profile_data["Location"]=location.text()
        dialog.close()
        QMessageBox.information(self,"Saved","Profile saved in session.")

    # ================= Theme =================
    def change_theme(self):
        theme, ok = QInputDialog.getItem(self,"Select Theme","Theme:",THEMES.keys(),current=0,editable=False)
        if ok and theme:
            apply_theme(self,theme)

    # ================= Report Tab =================
    def setup_report_tab(self):
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        card_container=QWidget()
        scroll.setWidget(card_container)
        layout=QVBoxLayout(card_container)
        layout.setSpacing(16)
        # Image label
        self.image_label=QLabel("Uploaded image will be shown here 🖼️")
        self.image_label.setFixedHeight(240)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border:2px dashed #d1d5db;border-radius:12px;color:#9ca3af;")
        btns=QHBoxLayout()
        upload=QPushButton("Upload Image 🗃️")
        upload.clicked.connect(self.upload_image)
        camera=QPushButton("Take Photo 📸")
        camera.setObjectName("Secondary")
        camera.clicked.connect(self.take_photo_mock)
        btns.addWidget(upload)
        btns.addWidget(camera)
        self.issue_type=QComboBox()
        self.issue_type.addItems(["Pothole","Leakage","Road Damage","Garbage","Streetlight"])
        self.issue_type.setFixedHeight(36)
        self.location=QLineEdit()
        self.location.setPlaceholderText("Location 📍")
        auto=QPushButton("Auto Detect 📡")
        auto.setObjectName("Secondary")
        auto.clicked.connect(self.auto_detect_location)
        loc=QHBoxLayout()
        loc.addWidget(self.location)
        loc.addWidget(auto)
        self.text=QTextEdit()
        self.text.setPlaceholderText("Describe the issue (optional)")
        self.text.setFixedHeight(90)
        send=QPushButton("Submit Report 📤")
        send.clicked.connect(self.send_report)
        layout.addWidget(self.image_label)
        layout.addLayout(btns)
        layout.addWidget(self.issue_type)
        layout.addLayout(loc)
        layout.addWidget(self.text)
        layout.addWidget(send,alignment=Qt.AlignmentFlag.AlignRight)
        report_layout=QVBoxLayout(self.report_tab)
        report_layout.addWidget(scroll)

    # ================= History =================
    def setup_history_tab(self):
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        container=QWidget()
        scroll.setWidget(container)
        self.history_layout=QVBoxLayout(container)
        self.counter_label=QLabel("")
        self.counter_label.setStyleSheet("font-weight:600; font-size:14px;")
        self.history_layout.addWidget(self.counter_label)
        self.history_list=QListWidget()
        self.history_layout.addWidget(self.history_list)
        self.refresh_history()
        tab_layout=QVBoxLayout(self.history_tab)
        tab_layout.addWidget(scroll)

    # ================= Help =================
    def setup_help_tab(self):
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        container=QWidget()
        scroll.setWidget(container)
        layout=QVBoxLayout(container)
        help_text=QLabel(
"Help – CityCare \n"
 "\n"
"📌 What is CityCare?\n"
 "\n"
"CityCare is a civic issue reporting platform that helps citizens report problems like \n"
 "potholes, damaged roads, or other public issues quickly and transparently.\n"
 "\n"      
"📝 How to Report an Issue\n"
 "\n"
"1. Go to Report Issue\n"
"2. Select the issue type (e.g., pothole)\n"
"3. Enter the location\n"
"4. Add a short description (optional)\n"
"5. Upload or take a photo of the issue\n"
"6. Submit the report\n"
        "\n"     
"Your report will be reviewed and tracked until it is resolved.\n"
 "\n"
"📷 Image Guidelines\n"
 "\n"
"1. Upload a clear image of the issue\n"
"2. Make sure the problem is visible\n"
"3. Avoid blurry or unrelated images\n"
   "\n"          
"Images help authorities understand and resolve issues faster.\n"
 "\n"
"🕒 Tracking Your Report\n"
 "\n"
"1. You can view all your submitted reports in the History section\n"
"2. Each report shows its current status:\n"
 "\n"
"Pending\n"
"In Progress\n"
"Resolved\n"
 "\n"
"You’ll be notified once the issue is resolved.\n"
 "\n"
"⭐ Feedback & Ratings\n"
 "\n"
"After an issue is resolved, you’ll be asked to:\n"
 "\n"
"Rate the resolution (1–5)\n"
"Share feedback (optional)\n"
"Your feedback helps improve the service quality.\n"
 "\n"
"🎨 Theme & Personalization\n"
 "\n"
"CityCare supports multiple themes:\n"
 "\n"
"Cream White – Default Theme\n"
 "\n"
"Night Pink – Blush Mode Theme\n"
 "\n"
"Blue Panther – Midnight Theme\n"
 "\n"
"You can change themes anytime from Settings.\n"
 "\n"
"❓ Need More Help?\n"
 "\n"
"If you face any issues or have suggestions, please share feedback through the app.\n"
 "\n"
"Together, we can make cities better.\n"
"\n"
        )
        help_text.setStyleSheet("color:#374151; font-size:14px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        tab_layout=QVBoxLayout(self.help_tab)
        tab_layout.addWidget(scroll)

    # ================= Logic =================
    def upload_image(self):
        file,_=QFileDialog.getOpenFileName(self,"Select Image","","Images (*.png *.jpg)")
        if file:
            self.image_path=file
            pix=QPixmap(file).scaled(self.image_label.width(),self.image_label.height(),Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pix)
    def take_photo_mock(self):
        self.image_label.setText("Mock photo captured")
        self.image_path="mock"
    def auto_detect_location(self):
        self.location.setText("Auto detected location")

    # ================= Send Report =================
    def send_report(self):
        if not self.image_path and not self.text.toPlainText():
            QMessageBox.warning(self,"Error","Add image or description")
            return
        issue=self.issue_type.currentText()
        now=datetime.now().strftime("%Y-%m-%d %H:%M")
        report={"issue":issue,"text":self.text.toPlainText(),"status":"Sent",
                "date":now,"location":self.location.text() or "Not provided","image":self.image_path}
        history.append(report)
        self.refresh_history()
        QMessageBox.information(self,"Submitted","Report submitted successfully")
        self.text.clear()
        self.location.clear()
        self.image_label.setText("No image selected")
        # Demo timeline: resolve after 20 sec
        QTimer.singleShot(20000, lambda r=report:self.auto_resolve(r))

    # ================= Auto Resolve & Feedback =================
    def auto_resolve(self,report):
        report["status"]="Resolved"
        self.refresh_history()
        dlg=QDialog(self)
        dlg.setWindowTitle("Feedback for your report")
        layout=QVBoxLayout(dlg)
        lbl=QLabel(f"Your report '{report['issue']}' has been resolved!\nPlease provide feedback:")
        layout.addWidget(lbl)
        feedback_text=QTextEdit()
        feedback_text.setPlaceholderText("Type your feedback here...")
        layout.addWidget(feedback_text)
        rating_box=QComboBox()
        rating_box.addItems([str(i) for i in range(1,6)])
        layout.addWidget(QLabel("Rating (1-5):"))
        layout.addWidget(rating_box)
        submit_btn=QPushButton("Submit Feedback")
        submit_btn.clicked.connect(lambda: (dlg.close(), QMessageBox.information(self,"Thanks","Feedback submitted!")))
        layout.addWidget(submit_btn)
        dlg.exec()

    # ================= Refresh History =================
    def refresh_history(self):
        self.history_list.clear()
        submitted=len(history)
        resolved=sum(1 for r in history if r["status"]=="Resolved")
        self.counter_label.setText(f"Submitted: {submitted} | Resolved: {resolved}")
        if not history:
            placeholder=QListWidgetItem("No reports yet.\nSubmit a report to see history here.")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.history_list.addItem(placeholder)
        else:
            for idx,r in enumerate(history):
                item=QListWidgetItem(f"{r['issue']} • {r['status']}\n{r['date']} • {r['location']}")
                self.history_list.addItem(item)
                # Add view report on double click
                self.history_list.itemDoubleClicked.connect(self.view_report)

    def view_report(self,item):
        idx=self.history_list.row(item)
        r=history[idx]
        dlg=QDialog(self)
        dlg.setWindowTitle("View Report")
        layout=QVBoxLayout(dlg)
        lbl=QLabel(f"Issue: {r['issue']}\nStatus: {r['status']}\nDate: {r['date']}\nLocation: {r['location']}\nDescription: {r['text']}")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        if r["image"] and r["image"]!="mock":
            pix=QPixmap(r["image"]).scaled(400,300,Qt.AspectRatioMode.KeepAspectRatio)
            img_lbl=QLabel()
            img_lbl.setPixmap(pix)
            layout.addWidget(img_lbl)
        elif r["image"]=="mock":
            img_lbl=QLabel("Mock photo")
            layout.addWidget(img_lbl)
        dlg.exec()

# ================= Run =================
if __name__=="__main__":
    app=QApplication(sys.argv)
    splash=SplashScreen()
    splash.show()
    sys.exit(app.exec())
