import os, datetime, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.uix.scrollview import ScrollView
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
try:
    from jnius import autoclass, cast
    from android import activity
    ANDROID = True
except ImportError:
    ANDROID = False




# ------------------------
# Product dictionary
# ------------------------

PRODUCTS = {
    "Invertor": {
        "ADC000005": "Inverter, maximum 3.3KVA AC output",
        "ADC000006": "Inverter, maximum 4.4KVA AC output",
    },
    "Baterie": {
        "ADC000083": "Power Module",
        "ADC000084": "Battery Module",
    },
    "Contor": {
        "ADC000135": "DDSU666-H single-phase",
        "ADC000136": "DTSU666-H three-phase 250A",
    }
}


# ------------------------
# Table Row
# ------------------------
class FormRow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 40

        # Category as editable spinner
        self.category = Spinner(
            text="Alege categorie",
            values=list(PRODUCTS.keys())+["Manual"],
            size_hint_x=0.2
        )
        self.category.bind(text=self.update_category)
        self.add_widget(self.category)

        #Manual category input (hidden initially)
        self.category_manual =TextInput(size_hint_x=0.2, opacity=0, disabled=True)
        self.add_widget(self.category_manual)

        # Cod produs (spinner/manual)
        self.cod_produs = Spinner(text="", size_hint_x=0.2)
        self.cod_produs.bind(text=self.update_product)
        self.add_widget(self.cod_produs)

        self.cod_manual = TextInput(size_hint_x=0.2, opacity=0, disabled=True)
        self.cod_manual.bind(text=self.update_manual_product)
        self.add_widget(self.cod_manual)

        # PN/produs (free text)
        self.product = TextInput(size_hint_x=0.3)
        self.add_widget(self.product)

        # Cantitate luata (free)
        self.qty_taken = TextInput(input_filter="int", size_hint_x=0.15)
        self.add_widget(self.qty_taken)

        # Cantitate utilizata (free)
        self.qty_used = TextInput(input_filter="int", size_hint_x=0.15)
        self.add_widget(self.qty_used)

    def update_category(self, spinner, text):
        if text == "Manual":
        # Show manual category input
            self.category_manual.opacity, self.category_manual.disabled = 1, False
            self.cod_produs.opacity, self.cod_produs.disabled = 0, True
            self.cod_manual.opacity, self.cod_manual.disabled = 1, False
            self.product.text = ""
        else:
        # Hide manual category
            self.category_manual.opacity, self.category_manual.disabled = 0, True
            self.cod_produs.opacity, self.cod_produs.disabled = 1, False
            self.cod_manual.opacity, self.cod_manual.disabled = 0, True
            self.product.readonly = False
            if text in PRODUCTS:
                self.update_codes(spinner, text)


    
    def get_category_value(self):
        return self.category_manual.text if not self.category_manual.disabled else self.category.text


    def update_codes(self, spinner, category):
        codes = list(PRODUCTS.get(category, {}).keys())
        codes.append("Manual")
        self.cod_produs.values = codes
        if codes:
            self.cod_produs.text = codes[0]
            self.update_product(self.cod_produs, codes[0])

    def update_product(self, spinner, text):
        if text == "Manual":
            self.cod_produs.opacity, self.cod_produs.disabled = 0, True
            self.cod_manual.opacity, self.cod_manual.disabled = 1, False
            self.product.text = ""
        else:
            self.cod_produs.opacity, self.cod_produs.disabled = 1, False
            self.cod_manual.opacity, self.cod_manual.disabled = 0, True
            category = self.category.text
            if category in PRODUCTS and text in PRODUCTS[category]:
                self.product.text = PRODUCTS[category][text]
            else:
                self.product.text = ""

    def update_manual_product(self, instance, value):
        self.product.text = f"Cod personalizat: {value}" if value else ""



    def send_email_with_attachment(pdf_path):
        if not ANDROID:
            print("⚠️ Email sending works only on Android device.")
            return
    
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')

        intent = Intent(Intent.ACTION_SEND)
        intent.setType("application/pdf")
        intent.putExtra(Intent.EXTRA_SUBJECT, "Formular Montaj")
        intent.putExtra(Intent.EXTRA_TEXT,
            "Bună ziua,\n\nAtașat găsiți formularul de montaj completat.\n\nCu respect,\nEchipa")

        file = File(pdf_path)
        uri = Uri.fromFile(file)
        intent.putExtra(Intent.EXTRA_STREAM, cast('android.os.Parcelable', uri))

        intent.putExtra(Intent.EXTRA_EMAIL, ["client@example.com"])

        currentActivity = cast('android.app.Activity', activity._activity)
        currentActivity.startActivity(intent)



# ------------------------
# Main App
# ------------------------
class FormApp(App):
    def build(self):
        self.rows = []

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Header
        header = GridLayout(cols=2, size_hint_y=None, height=120)
        header.add_widget(Label(text="Client/locatie"))
        self.client = TextInput()
        header.add_widget(self.client)

        header.add_widget(Label(text="Persoana care a completat"))
        self.completed_by = TextInput()
        header.add_widget(self.completed_by)

        header.add_widget(Label(text="Data completării"))
        self.date_input = TextInput(text=datetime.date.today().isoformat())
        header.add_widget(self.date_input)

        root.add_widget(header)

        # Table header
        table_header = GridLayout(cols=5, size_hint_y=None, height=30)
        for h in ["Categorie", "Cod produs", "PN/produs", "Cant. luata", "Cant. utilizata"]:
            table_header.add_widget(Label(text=h, bold=True))
        root.add_widget(table_header)

        # Scrollable table
        scroll = ScrollView(size_hint=(1, 1))

        self.table = BoxLayout(orientation="vertical", size_hint_y=None)
        self.table.bind(minimum_height=self.table.setter("height"))  # grow as rows are added

        scroll.add_widget(self.table)
        root.add_widget(scroll)


# Buttons
        buttons = BoxLayout(size_hint_y=None, height=50)

        add_btn = Button(text="➕ Adauga rand")
        add_btn.bind(on_release=self.add_row)
        buttons.add_widget(add_btn)

        pdf_btn = Button(text="📄 Genereaza PDF")
        pdf_btn.bind(on_release=self.generate_pdf)
        buttons.add_widget(pdf_btn)

        email_btn = Button(text="✉️ Trimite Email")
        email_btn.bind(on_release=self.send_email)
        buttons.add_widget(email_btn)

        root.add_widget(buttons)

        return root
    def add_row(self, *args):
        row = FormRow()
        self.rows.append(row)
        self.table.add_widget(row)
    
    def add_logo(canvas, doc):
        """Draw logo and header on each page."""
        logo_path = os.path.join(os.getcwd(), "logo.png")
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 40, A4[1] - 100, width=120, height=60,
                            preserveAspectRatio=True, mask='auto')
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(A4[0] / 2, A4[1] - 50, "FORMULAR MONTAJ")
        canvas.setFont("Helvetica", 10)
        canvas.drawRightString(A4[0] - 40, 30, f"Page {doc.page}")
    
    def generate_pdf(self, *args):
        filename = f"formular_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        self.last_pdf = filepath

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        row_height = 20
        bottom_margin = 50
        col_widths = [100, 100, 200, 80, 80]
        table_width = sum(col_widths)
        x_start = (width - table_width) / 2
        headers = ["Categorie", "Cod produs", "PN/produs", "Cant. luata", "Cant. utilizata"]

        # Track page number
        page_num = 1

        def draw_page_header():
            """Draw logo, title, and client info on every page."""
            if os.path.exists("logo.png"):
                c.drawImage("logo.png", 50, height - 100,
                            width=120, height=50, preserveAspectRatio=True, mask="auto")
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 50, "FORMULAR MONTAJ")

            # Header info
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 120, f"Client/Locatie: {self.client.text}")
            c.drawString(50, height - 135, f"Completat de: {self.completed_by.text}")
            c.drawString(50, height - 150, f"Data completarii: {self.date_input.text}")

            # Table header
            y_head = height - 180
            c.setFont("Helvetica-Bold", 9)
            x = x_start
            for i, h in enumerate(headers):
                c.rect(x, y_head, col_widths[i], row_height)
                c.drawCentredString(x + col_widths[i] / 2, y_head + 5, h)
                x += col_widths[i]
            return y_head - row_height

        def draw_page_footer(page_num):
            """Draw footer with page number."""
            c.setFont("Helvetica", 9)
            c.drawCentredString(width/2, 30, f"Pagina {page_num}")

        # --- First page header ---
        y = draw_page_header()

    # --- Draw rows with auto page break ---
        c.setFont("Helvetica", 8)
        for row in self.rows:
            if y <= bottom_margin:  # new page
                draw_page_footer(page_num)
                c.showPage()
                page_num += 1
                y = draw_page_header()
                c.setFont("Helvetica", 8)

            values = [
                row.get_category_value(),
                row.cod_manual.text if not row.cod_manual.disabled else row.cod_produs.text,
                row.product.text,
                row.qty_taken.text,
                row.qty_used.text,
            ]
            x = x_start
            for i, v in enumerate(values):
                c.rect(x, y, col_widths[i], row_height)
                c.drawCentredString(x + col_widths[i] / 2, y + 5, v)
                x += col_widths[i]
            y -= row_height

    # --- Final footer ---
        draw_page_footer(page_num)

    # Save file
        c.save()
        self.last_pdf = filepath
        print(f"✅ PDF saved: {filepath}")


    def send_email(self, *args):
        if not hasattr(self, "last_pdf"):
            print("⚠️ Please generate PDF first!")
            return

        sender = "alexandru.baican@adc.ro"
        password = "lex@ndru308$bcn2004"
        recipients = ["baicanalex568@gmail.com"]

        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = "Formular Montaj Completat"
        msg.attach(MIMEText("Bună ziua,\n\nAtașez formularul de montaj completat.\n\nCu respect,"))

        with open(self.last_pdf, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(self.last_pdf))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(self.last_pdf)}"'
            msg.attach(part)

        try:
        # Outlook SMTP
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                server.ehlo()
                server.starttls()  # important for Outlook
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())
            print("✅ Email sent via Outlook!")
        except Exception as e:
            print("❌ Email failed:", e)



if __name__ == "__main__":
    FormApp().run()
