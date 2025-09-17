import os, datetime, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import requests
import base64
import msal 
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
from kivy.uix.popup import Popup
from kivy.uix.label import Label

client_id = "c65a86ef-c2c1-4fa7-8d23-f7bd26eacf79"
tenant_id = "1b4f6890-7d22-4701-b4c7-dbee8d2a3594"
authority = f"https://login.microsoftonline.com/{tenant_id}"

# Create MSAL app globally
app = msal.PublicClientApplication(client_id=client_id, authority=authority)

# Acquire token once and keep it (but don't send email yet!)
result = app.acquire_token_interactive(scopes=["Mail.Send"])

if "access_token" in result:
    access_token = result["access_token"]
else:
    print("❌ Could not acquire token:", result.get("error_description"))
    access_token = None


# ------------------------
# Product dictionary
# ------------------------

PRODUCTS = {
    "Invertor(single-phase)": {
        "ADC000005": "Inverter, maximum 3.3KVA AC output,SUN2000-3KTL-L1",
        "ADC000006": "Inverter, maximum 4.4KVA AC output,SUN2000-4KTL-L1",
        "ADC000007": "SUN2000-5KTL-L1,Inverter, maximum 5.5KVA AC output",
        "ADC000008": "SUN2000-6KTL-L1 Inverter, maximum 6.6KVA AC output",
        "ADC000009": "SUN2000-8KTL-LC0 Inverter, maximum 8.8KVA AC output",
        "ADC000010": "SUN2000-10KTL-LC0, Inverter, maximum 11KVA AC output"
    },
        "Invertor(three-phase)": {
        "ADC000011": "SUN2000-3KTL-M1HC , Inverter, maximum 3.3KVA AC output",
        "ADC000012": "SUN2000-4KTL-M1HC , Inverter, maximum 4.4KVA AC output",
        "ADC000013": "SUN2000-5KTL-M1HC  Inverter, maximum 5.5KVA AC output",
        "ADC000011": "SUN2000-6KTL-M1HC  Inverter, maximum 6.6KVA AC output",
        "ADC000015": "SUN2000-8KTL-M1HC  Inverter, maximum 8.8KVA AC output",
        "ADC000016": "SUN2000-10KTL-M1HC Inverter, maximum 11KVA AC output",
        "ADC000017": "SUN2000-12KTL-M5 HC Inverter, maximum 13.2KVA AC output",
        "ADC000018": "SUN2000-15KTL-M5 HC Inverter, maximum 16.5KVA AC output",
        "ADC000019": "SUN2000-17KTL-M5 HC Inverter, maximum 18.7KVA AC output",
        "ADC000022": "SUN2000-30KTL-M3 Inverter, maximum 33.0KVA AC output",
        "ADC000023": "SUN2000-36KTL-M3 Inverter, maximum 40.0KVA AC output",
        "ADC000024": "SUN2000-40KTL-M3 Inverter, maximum 44.0KVA AC output",
        "ADC000025": "SUN2000-50KTL-M3 Inverter, maximum 55.0KVA AC output",
        "ADC000026": "SUN2000-100KTL-M2-AFCI Inverter, maximum 110.0KVA AC output",
        "ADC000027": "SUN2000-115KTL-M2 (115 kW) Inverter, maximum 125.0KVA AC output",
        "ADC000028": "SUN2000-150KTL-MG0 (150 kW) Inverter, maximum 165.0KVA AC output",
        "ADC000029": "SUN2000-185KTL-H1 (185 kW) Huawei three-phase inverter SUN2000-185KTL-H1",
        "ADC000030": "SUN2000-215KTL-H0 (215 kW) Huawei three-phase inverter SUN2000-215KTL-H0",
        "ADC000031": "SUN2000-215KTL-H1 (215 kW) Huawei three-phase inverter SUN2000-215KTL-H1",
        "ADC000032": "SUN2000-330KTL-H1 Huawei three-phase inverter SUN2000-330KTL-H1",
        "ADC000033": "SUN2000-12K-MB0 Inverter, Hybrid , maximum 13.2KVA AC output",
        "ADC000034": "SUN2000-15K-MB0 Inverter, Hybrid , maximum 16.5KVA AC output",
        "ADC000035": "SUN2000-17K-MB0 Inverter, Hybrid, maximum 18.7KVA AC output",
        "ADC000036": "SUN2000-20K-MB0 Inverter, Hybrid, maximum 22.0KVA AC output",
        "ADC000037": "SUN2000-25K-MB0 Inverter, Hybrid, maximum 27.0KVA AC output",
        "ADC000038": "SUN2000-5K-MAP0 Inverter on-grid hybrid, Asymetric Huawei SUN2000-5K-MAP0",
        "ADC000039": "SUN2000-6K-MAP0 Inverter on-grid hybrid, Asymetric Huawei SUN2000-6K-MAP0",
        "ADC000040": "SUN2000-8K-MAP0 Inverter on-grid hybrid, Asymetric Huawei SUN2000-8K-MAP0",
        "ADC000041": "SUN2000-10K-MAP0 Inverter on-grid hybrid, Asymetric Huawei SUN2000-10K-MAP0",
        "ADC000042": "SUN2000-12K-MAP0 (13,2 kW) Inverter on-grid hybrid, Asymetric Huawei SUN2000-12K-MAP0",
        "ADC000043": "SUN5000-8K-MAP0 Inverter hybrid Asymetric Huawei SUN5000-8K-MAP0",
        "ADC000044": "SUN5000-12K-MAP0 Inverter hybrid Asymetric Huawei SUN5000-12K-MAP0" 
    },
    
    "Smart Power Sensor": {
        "ADC000135": "DDSU666-H Power meter, DDSU666-H, single-phase smart meter",
        "ADC000136": "DTSU666-H 250A Power meter, DTSU666-H, three-phase smart meter 250A",
        "ADC000137": "DTSU666-H 100A Power meter, DTSU666-H, three-phase smart meter 100A",
        "ADC000138": "DTSU666-HW Power meter, DTSU666-H, three-phase smart meter",
        "ADC000139": "DTSU666-FE Smart power Sensor"
    },
    "Accessories":{
        "ADC000140": "EMMA-A02, EMMA-A02",
        "ADC000141": "SmartGuard-63A-S0, SmartGuard-63A-S0",
        "ADC000335": "SmartGuard-63A-T0, SmartGuard-63A-T0"
    },
    "Storage":{
        "ADC000083": "LUNA2000-5-C0, Power Module",
        "ADC000084": "LUNA2000-5-E0, Battery Module,",
        "ADC000085": "Luna2000-5-S0, Storage KIT Luna 5 Kw",
        "ADC000086": "Luna2000-10-S0, Storage KIT Luna 10 Kw",
        "ADC000087": "Luna2000-15-S0, Storage KIT Luna 15 Kw",
        "ADC000088": "Battery module LUNA2000-7-E1, Battery Module",
        "ADC000089": "Power module LUNA2000-10KW-C1, Power Module",
        "ADC000090": "Huawei LUNA2000-7-S1 ,Storage KIT Luna 7 Kw",
        "ADC000091": "Huawei LUNA2000-14-S1 ,Storage KIT Luna 14 Kw",
        "ADC000092": "Huawei LUNA2000-21-S1 ,Storage KIT Luna 21 Kw"
    },
    "Wall Mount":{
        "ADC000142" "Luna2000 Wall Bracket, Battery Wall mounting bracket S0",
        "ADC000143" "LUNA2000-S1 Wall Mounting Bracket, Battery Wall mounting bracket S1"
    },
    "Backup system(single-phase)":{
        "ADC000144": "Back-up box-B0, Backup system"
    },
    "Backup system(three-phase)":{
        "ADC000145": "Back-up box-B1, Backup system"
    },
    "Optimizer":{
        "ADC000146": "SUN2000-450W-P2 Optimizer, 450W, compatible with L1 and M1/M2 inverters",
        "ADC000147": "SUN2000-600W-P, HUAWEI Smart PV Optimizer SUN2000-600W-P",
        "ADC000148": "1100W-P Short Cable Optimizer, Optimizator Huawei 1100W-P Smart Module Controller cablu scurt",
        "ADC000149": "1100W-P Long Cable Optimizer, Optimizator Huawei 1100W-P Smart Module Controller cablu lung",
        "ADC000150": "1300W-P Short Cable Optimizer, Optimizator Huawei 1300W-P Smart Module Controller cablu scurt",
        "ADC000151": "1300W-P Long Cable Optimizer, Optimizator Huawei 1300W-P Smart Module Controller cablu lung"
    },
    "Smart Logger":{
        "ADC000152": "SmartLogger3000A03EU (with MBUS), Smart logger communication for 80 devices at most with MBUS",
        "ADC000153": "SmartLogger3000A01EU, Smart logger communication for 80 devices at most",
        "ADC000154": "SmartLogger3000B, Smart logger communication for 150 devices at most"
    },

    "WiFi Dongle":{
        "ADC000155": "SmartDongle WLAN-FE , WLAN-FE Dongle, communication for 10 devices at most"
    },
    "4G Dongle":{
        "ADC000157": "SmartDongle 4G, External 4G antenna, communication for 10 devices at most"
    },
    "Analizor de putere":{
        "ADC000158": "Power Analyser JANITZA UMG 103", 
        "ADC000159": "Power Analyser JANITZA UMG 104"
    },
    "Silicon irradiance sensor":{
        "ADC000311": "SM1-485PRO-SUNMETER PRO"
    },
    "PT100Temp":{
        "ADC000280":" TM3-Temmer PT100 temperature*, PT100 temperature probe for PV modules withadhesive surface for adhesion to tedlar of PV modules.",        
    },
    "Anemometer":{
        "ADC000281":"ANE-ANEMOMETER-Wind*, Windmeter - Digital Anemometer"
    },
    "Charging station":{
        "ADC000185":"AC charger 1 Phase 7kW/32A, Charging station 1 Phase 7kW/32A", 
        "ADC000186":"AC charger 3 Phase 22kW/32A, Charging station 3 Phase 22kW/32A" 
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
        
        reset_btn = Button(text="🔄 Resetare form")
        reset_btn.bind(on_release=self.reset_form)
        buttons.add_widget(reset_btn)

        add_btn = Button(text="➕ Adauga rand")
        add_btn.bind(on_release=self.add_row)
        buttons.add_widget(add_btn)

        pdf_btn = Button(text="📄 Genereaza PDF")
        pdf_btn.bind(on_release=self.generate_pdf)
        buttons.add_widget(pdf_btn)

        email_btn = Button(text="✉️ Trimite Email")
        email_btn.bind(on_press=self.send_email)
        buttons.add_widget(email_btn)

        root.add_widget(buttons)

        return root
    def reset_form(self, *args):
        #Reset header inputs
        self.client.text = ""
        self.completed_by.text = ""
        self.date_input.text = datetime.date.today().isoformat()
        #Clear table rows
        for row in self.rows:
            self.table.remove_widget(row)
        self.rows = []
        print("🔄 Formular resetat!")

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
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
            logo_width = 100
            logo_height = 35
            if os.path.exists(logo_path):
                try:
                    c.drawImage(
                        logo_path,
                        width - logo_width -40,
                        height - logo_height -20,
                        width=logo_width,
                        height=logo_height,
                        mask='auto'
                    )
                except Exception as e:
                    print(f"⚠️ Could not draw logo: {e}")
            else:
                print(f"⚠️ Logo not found at {logo_path}")

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
            popup = Popup(
                title="⚠️ Atenție",
                content=Label(text="Trebuie să generezi PDF-ul înainte de a trimite emailul."),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            return

    # Authenticate only when user presses Send Email
        result = app.acquire_token_interactive(scopes=["Mail.Send"])
        if "access_token" not in result:
            popup = Popup(
                title="❌ Eroare autentificare",
                content=Label(text="Nu am putut obține token-ul.\nVerifică login-ul Microsoft."),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            return

        access_token = result["access_token"]

    # Read PDF content
        with open(self.last_pdf, "rb") as f:
            file_content = base64.b64encode(f.read()).decode("utf-8")

        endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        email_msg = {
            "message": {
                "subject": "Formular Montaj Completat",
                "body": {
                    "contentType": "Text",
                    "content": "Bună ziua,\n\nAtașez formularul de montaj completat.\n\nCu respect,"
                },
                "from": {
                    "emailAddress": {"address": "formular@adc.ro"}
                },
                "toRecipients": [
                    {"emailAddress": {"address": "baicanalex568@gmail.com"}}
                ],
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": os.path.basename(self.last_pdf),
                        "contentBytes": file_content
                    }
                ]
            },
            "saveToSentItems": "true"
        }

        r = requests.post(endpoint, headers=headers, json=email_msg)

        if r.status_code == 202:
            popup = Popup(
                title="✅ Succes",
                content=Label(text="Email trimis cu succes!\nPDF-ul a fost atașat."),
                size_hint=(0.6, 0.3)
            )
        else:
            popup = Popup(
                title="❌ Eroare",
                content=Label(text=f"Eroare la trimiterea emailului:\n{r.status_code}\n{r.text}"),
                size_hint=(0.7, 0.4)
            )
        popup.open()
         

if __name__ == "__main__":
    FormApp().run()
