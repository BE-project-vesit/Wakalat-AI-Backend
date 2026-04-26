import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'MUTUAL NON-DISCLOSURE AGREEMENT', 0, 1, 'C')
        self.ln(10)

pdf = PDF()
pdf.add_page()
pdf.set_font('helvetica', '', 12)

text = """This Mutual Non-Disclosure Agreement (the "Agreement") is entered into as of April 20, 2026, by and between:

Party A: Tech Nova Solutions Pvt. Ltd., having its registered office at Andheri East, Mumbai, Maharashtra 400069.
Party B: Zenith Innovations, having its registered office at Koramangala, Bengaluru, Karnataka 560034.

1. Purpose
The parties intend to explore a potential business collaboration regarding artificial intelligence software integration (the "Purpose"). During these discussions, it may be necessary for either party to share confidential information.

2. Confidential Information
"Confidential Information" shall mean any and all technical and non-technical information provided by either party to the other, including but not limited to trade secrets, proprietary algorithms, source code, business plans, and financial reports.

3. Obligations
The receiving party agrees to hold the Confidential Information in strict confidence and will not disclose it to any third party without prior written consent from the disclosing party. 

4. Term
This Agreement shall remain in effect for a period of three (3) years from the Effective Date. The obligations of confidentiality shall survive the termination of this Agreement for five (5) additional years.

5. Jurisdiction
This Agreement shall be governed by and construed in accordance with the laws of India. Any disputes arising out of this Agreement shall be subject to the exclusive jurisdiction of the courts located in Mumbai, Maharashtra.

IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first written above.

For Party A:                                           For Party B:
Signature: _______________________                     Signature: _______________________
Name: Rajesh Sharma                                    Name: Priya Desai
Title: Chief Executive Officer                         Title: Managing Director
"""

pdf.multi_cell(0, 8, text)

# Output
output_path = r"C:\girgit-logs\VESIT\Final Year BE Project\Sample_Testing_NDA.pdf"
pdf.output(output_path)
print("Saved to", output_path)
