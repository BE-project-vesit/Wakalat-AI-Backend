import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

class PDF(FPDF):
    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('helvetica', '', 12)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

    def image_with_maintain_aspect(self, image_path):
        with Image.open(image_path) as img:
            w, h = img.size
        usable_width = self.w - self.l_margin - self.r_margin
        
        # Available height on current page (reserve 20 units for bottom text)
        available_height = self.h - self.get_y() - self.b_margin - 20
        
        aspect_ratio = h / w
        img_w = usable_width
        img_h = usable_width * aspect_ratio

        if img_h > available_height:
            img_h = available_height
            img_w = available_height / aspect_ratio

        # Center horizontally
        x_pos = (self.w - img_w) / 2
        self.image(image_path, x=x_pos, w=img_w, h=img_h)
        # Manually move cursor below image
        self.set_y(self.get_y() + img_h)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Center align title on first page (vertical and horizontal)
page_height = pdf.h
pdf.set_y(page_height / 2 - 20)
pdf.set_font('helvetica', 'B', 24)
pdf.cell(0, 15, 'Wakalat-AI: Sample Outputs & Capabilities', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.set_font('helvetica', 'I', 14)
pdf.cell(0, 10, 'A comprehensive comparison and demonstration of case forms and outputs', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

base_dir = r"C:\girgit-logs\VESIT\Final Year BE Project\Sample Output Format and Demo Video"

def add_section(title, desc, image_names):
    for idx, img in enumerate(image_names):
        pdf.add_page()
        title_str = title if idx == 0 else title + " (Continued)"
        pdf.chapter_title(title_str)
        if idx == 0 and desc:
            pdf.chapter_body(desc)
        
        img_path = os.path.join(base_dir, img)
        if os.path.exists(img_path):
            pdf.image_with_maintain_aspect(img_path)
            pdf.ln(5)
            pdf.set_font('helvetica', 'I', 10)
            pdf.cell(0, 10, f"Source File: {img}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        else:
            pdf.chapter_body(f"Error: Image {img} not found.")

sections = [
    {
        "title": "1. The Wakalat-AI Advantage: ChatGPT vs. Wakalat-AI",
        "desc": "Comparison of a generic AI (ChatGPT) requiring specific prompt engineering vs. Wakalat-AI providing fine-tuned analysis with 1 prompt via automated tools.",
        "images": ["criminal robbery chatgpt response.png", "criminal robbery.png", "criminal 2.png"]
    },
    {
        "title": "2. Guided Form: Criminal Case",
        "desc": "Dynamic guided form fields specifically tailored for Criminal cases.",
        "images": ["guided form  criminal case.png"]
    },
    {
        "title": "3. Civil Case Capabilities",
        "desc": "Input forms and fine-tuned AI analysis outputs for varying Civil cases.",
        "images": ["civil case form.png", "civil case output.png", "civil - partnership dispute.png"]
    },
    {
        "title": "4. Cybercrime Case Capabilities",
        "desc": "Input forms and analysis outputs for Cybercrime incidents.",
        "images": ["cybercrime form.png", "cybercrime output.png"]
    },
    {
        "title": "5. Family Case Capabilities",
        "desc": "Input forms and analysis outputs for Family dispute resolutions.",
        "images": ["family case form.png", "family case output.png"]
    },
    {
        "title": "6. Feature Highlight: Limitation Period Check",
        "desc": "Automated limitation period checks referencing specific Indian statutory acts.",
        "images": ["limitation period.png", "limitation period sources.png"]
    }
]

for sec in sections:
    add_section(sec["title"], sec["desc"], sec["images"])

output_path = os.path.join(base_dir, "Wakalat_AI_Sample_Outputs_v3.pdf")
pdf.output(output_path)
print(f"PDF successfully generated at: {output_path}")
