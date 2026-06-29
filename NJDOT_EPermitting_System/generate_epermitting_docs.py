import os
import sys
from fpdf import FPDF

class EPermittingPDF(FPDF):
    def header(self):
        # Draw top decorative header band in NJDOT Green/Blue style
        self.set_fill_color(33, 115, 70) # Greenish Teal for E-Permitting
        self.rect(0, 0, 210, 20, "F")
        
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.set_xy(10, 5)
        self.cell(0, 10, "NJDOT E-Permitting System - Comprehensive Reference Guide", 0, 0, "L")
        
        # Line break
        self.ln(20)

    def footer(self):
        # Go to 15 mm from bottom
        self.set_y(-15)
        self.set_fill_color(240, 240, 240)
        self.rect(0, 282, 210, 15, "F")
        
        self.set_text_color(100, 100, 100)
        self.set_font("Helvetica", "I", 8)
        self.set_x(10)
        self.cell(0, 10, "Confidential - New Jersey Department of Transportation (NJDOT) Internal Use", 0, 0, "L")
        
        self.set_x(-25)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")

    def chapter_title(self, num, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(33, 115, 70) # E-Permitting Green
        self.cell(0, 10, f"{num}. {title}", 0, 1, "L")
        self.ln(4)

    def chapter_subtitle(self, text):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(100, 110, 120) # Slate Grey
        self.cell(0, 8, text, 0, 1, "L")
        self.ln(2)

    def heading_3(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.cell(0, 6, text, 0, 1, "L")
        self.ln(1)

    def paragraph_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30) # Charcoal
        self.multi_cell(0, 5, text)
        self.ln(3)

    def bullet_item(self, text, indent=5):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.set_x(self.get_x() + indent)
        self.multi_cell(0, 5, f"- {text}")
        self.set_x(self.get_x() - indent)
        self.ln(1.5)

    def add_table(self, headers, data, col_widths):
        # Header
        self.set_fill_color(33, 115, 70)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 7, header, 1, 0, "C", True)
        self.ln()
        
        # Data rows
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 9)
        
        fill = False
        for row in data:
            self.set_fill_color(245, 250, 245) if fill else self.set_fill_color(255, 255, 255)
            
            # Calculate max lines needed for this row
            max_lines = 1
            for i, text in enumerate(row):
                chars_per_line = col_widths[i] // 2.2
                lines = max(1, -(-len(str(text)) // int(chars_per_line)))
                max_lines = max(max_lines, lines)
            
            row_height = max_lines * 4.5 + 2.5
            
            # Draw cells
            for i, text in enumerate(row):
                x = self.get_x()
                y = self.get_y()
                self.rect(x, y, col_widths[i], row_height, "DF" if fill else "D")
                self.multi_cell(col_widths[i], 4, str(text), 0, "L", False)
                self.set_xy(x + col_widths[i], y)
            
            self.ln(row_height)
            fill = not fill
        self.ln(3)

def generate_pdf():
    pdf = EPermittingPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(True, margin=20)
    
    # ---------------------------------------------------------
    # COVER PAGE
    # ---------------------------------------------------------
    pdf.add_page()
    pdf.set_fill_color(250, 255, 250)
    pdf.rect(0, 0, 210, 297, "F")
    
    pdf.set_fill_color(33, 115, 70)
    pdf.rect(0, 0, 210, 80, "F")
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_xy(15, 25)
    pdf.cell(0, 12, "NEW JERSEY", 0, 1, "L")
    pdf.cell(0, 12, "DEPARTMENT OF TRANSPORTATION", 0, 1, "L")
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(220, 245, 220)
    pdf.ln(5)
    pdf.cell(0, 8, "E-Permitting System Customer Portal Reference Guide", 0, 1, "L")
    
    pdf.set_text_color(33, 115, 70)
    pdf.set_xy(15, 110)
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 8, "COMPLETE BUSINESS, FUNCTIONAL,\nWORKFLOW, & AUTOMATION KNOWLEDGE BASE")
    
    pdf.set_fill_color(100, 110, 120)
    pdf.rect(15, 130, 80, 2, "F")
    
    pdf.set_xy(15, 140)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, "A professional, reverse-engineered solution guide detailing the NJDOT E-Permitting Customer Portal, covering highway occupancy, utility openings, drainage connections, subdivision planning, and automated testing architectures.\n\nPrepared for Developers, Business Analysts, Product Owners, UI/UX Teams, QA Engineers, and Automation Teams.")
    
    pdf.set_xy(15, 210)
    headers_meta = ["Document Metadata", "Detail"]
    meta_data = [
        ["System Name", "NJDOT Highway E-Permitting Customer Portal"],
        ["Version", "3.0 (Production Release Reference)"],
        ["Artifact Type", "Complete Solution & Operations Manual"],
        ["Publication Date", "June 2026"],
        ["Status", "Approved / SharePoint Ready"],
        ["Author", "Senior Solution & QA Architect (Advanced Agentic Systems)"]
    ]
    pdf.add_table(headers_meta, meta_data, [60, 120])
    
    # ---------------------------------------------------------
    # MAIN CHAPTERS
    # ---------------------------------------------------------
    
    # Section 1: Executive Summary
    pdf.add_page()
    pdf.chapter_title("1", "Executive Summary")
    pdf.paragraph_text(
        "The New Jersey Department of Transportation (NJDOT) manages all physical encroachments, access links, utility lines, and structural connections along State highways. The NJDOT E-Permitting System acts as the customer-facing web application where companies, utility providers, developers, and independent applicants file digital requests."
    )
    pdf.paragraph_text(
        "By digitizing these workflows, NJDOT enforces statewide safety specifications, tracks physical access points, automates the collection of statutory fees, and coordinates field engineering reviews. This reference document acts as a complete functional and technical knowledge base to support product owners, developers, and QA teams."
    )
    
    # Section 2: Module Overview
    pdf.chapter_title("2", "Module Overview")
    pdf.paragraph_text(
        "The E-Permitting Customer Portal includes several integrated functional modules:"
    )
    pdf.bullet_item("Profile Registry: Captures organization details, tax identifiers, and Point of Contact (POC) records.")
    pdf.bullet_item("Dashboard: Main portal containing the 'Submit Application' launcher card.")
    pdf.bullet_item("Submit Application drawer: Portal dispatch system supporting 12 active permit categories.")
    pdf.bullet_item("Action Items Grid: Tracks pending revisions or supplementary files requested by NJDOT engineers.")
    pdf.bullet_item("Permit History Grid: Archives historical submissions and their status logs.")
    pdf.bullet_item("Payment Activity Ledger: Financial ledger showing paid fees, transactions, and Excel download exports.")
    pdf.bullet_item("Common Checkout Gateway: Renders the credit/debit card billing gateway.")
    
    # Section 3: Business Purpose
    pdf.chapter_title("3", "Business Purpose")
    pdf.paragraph_text(
        "The e-permitting portal serves several critical state operational requirements:"
    )
    pdf.bullet_item("Statutory Enforcement: Integrates state regulations for highway utility openings and driveway access (NJSA 27:7-44.1 and NJAC 16:41).")
    pdf.bullet_item("Safety Assurance: Reviews structural load capabilities (bridge attachments), utility depths, and line-of-sight clearances (poles and structures).")
    pdf.bullet_item("Administrative Efficiency: Standardizes review metrics, replaces physical files with structured data, and coordinates multi-agency approvals.")

    # Section 4: User Roles & Permissions
    pdf.add_page()
    pdf.chapter_title("4", "User Roles & Permissions")
    pdf.paragraph_text(
        "The application divides authorization into the following roles:"
    )
    pdf.bullet_item("Utility Provider / Contractor: Submits utility openings, pole erections, or bridge attachments, and handles billing.")
    pdf.bullet_item("Land Developer: Prepares lot consolidation, major planning, and driveway access requests.")
    pdf.bullet_item("Appointed Engineering Agent: Represents land developers or utility companies during the planning review.")
    pdf.bullet_item("NJDOT Engineer / inspector (Staff Portal): Backend staff who review designs, execute coordinate inspections, issue permits, and audit financial files.")

    # Section 5: Functional Overview
    pdf.chapter_title("5", "Functional Overview")
    pdf.paragraph_text(
        "The system coordinates data and document collections across 12 distinct permit types:"
    )
    pdf.bullet_item("Utility Opening: Applies to excavation, pipeline installation, or road surface cuts.")
    pdf.bullet_item("Drainage Connection: Standardizes runoff volume estimations and drainage pipe layouts.")
    pdf.bullet_item("Erection of Pole: Manages safety and placement spacing for utility poles.")
    pdf.bullet_item("Highway Occupancy: Governs staging of construction materials or temporary highway detours.")
    pdf.bullet_item("Bridge Attachment: Collects structural plans for mounting conduits or utility cables on state bridges.")
    pdf.bullet_item("Letter of Interest: Initiates preliminary inquiries regarding highway access permits.")
    pdf.bullet_item("Lot Consolidation/Subdivision: Manages parcel mapping and municipal approvals.")
    pdf.bullet_item("Major Planning & Driveway Permits: Governs large-scale residential and commercial development access.")
    pdf.bullet_item("Pre-Application Meeting: Requests face-to-face planning discussions with NJDOT staff.")
    pdf.bullet_item("Street Intersection: Regulates physical intersections connecting local roads to state highways.")

    # Section 6: End-to-End Workflows
    pdf.add_page()
    pdf.chapter_title("6", "End-to-End Workflows")
    
    pdf.chapter_subtitle("Workflow 1: Utility Road Opening Permit")
    pdf.bullet_item("Step 1: User clicks 'Submit Application' on dashboard and selects 'Utility Opening'.")
    pdf.bullet_item("Step 2: User inputs Lot Owner details (Company, POC name, phone, email, and address).")
    pdf.bullet_item("Step 3: User uploads the required Authorization Certificate.")
    pdf.bullet_item("Step 4: User selects Route, Suffix, Direction, and enters Milepost, Block, and Lot details.")
    pdf.bullet_item("Step 5: User clicks 'Add New' to enter road cut dimensions (Length, Width, Depth).")
    pdf.bullet_item("Step 6: System automatically calculates area (Length x Width) and validates that the result is greater than zero.")
    pdf.bullet_item("Step 7: User uploads Overall Site Plans and checks the statutory acknowledgment box.")
    pdf.bullet_item("Step 8: User clicks 'Continue to Payment', completes checkout, and returns home.")
    
    pdf.chapter_subtitle("Workflow 2: Drainage Connection Permit")
    pdf.bullet_item("Step 1: User launches Drainage form.")
    pdf.bullet_item("Step 2: Inputs owner details and adds highway route location details.")
    pdf.bullet_item("Step 3: Enters drainage pipe size, runoff coefficient, and rainfall intensity metrics.")
    pdf.bullet_item("Step 4: Uploads Hydrology and Hydraulic calculations alongside Overall Site Plans.")
    pdf.bullet_item("Step 5: Signee inputs name and title, accepts terms, and processes payment.")
    
    pdf.chapter_subtitle("Workflow 3: Pre-Application Planning Meeting")
    pdf.bullet_item("Step 1: User opens Pre-Application request form.")
    pdf.bullet_item("Step 2: Inputs developer details and proposed development coordinates.")
    pdf.bullet_item("Step 3: Enters meeting agenda topics and lists proposed attendees.")
    pdf.bullet_item("Step 4: Uploads conceptual sketches and site layout plans.")
    pdf.bullet_item("Step 5: Submits the request. No checkout fee applies for scheduling preliminary meetings.")

    # Section 7: Navigation Flow
    pdf.add_page()
    pdf.chapter_title("7", "Navigation Flow")
    pdf.paragraph_text(
        "NJDOT Login Page\n"
        "  |\n"
        "  +-- [Action] Login --> Application Selection Portal\n"
        "                           |\n"
        "                           +--> E-Permitting Customer Dashboard\n"
        "                                  |\n"
        "                                  +--> Submit Application Menu\n"
        "                                  |      |-- Utility Opening Form\n"
        "                                  |      |-- Drainage Form\n"
        "                                  |      |-- Highway Occupancy Form\n"
        "                                  |      |-- Bridge Attachment Form\n"
        "                                  |      |-- Major Planning Form\n"
        "                                  |      +-- Pre-App Meeting Form\n"
        "                                  |\n"
        "                                  +--> Action Items Grid\n"
        "                                  +--> Permit History Grid\n"
        "                                  +--> Payment Activity Grid"
    )

    # Section 8: Business Rules
    pdf.chapter_title("8", "Business Rules")
    pdf.bullet_item("Milepost Validation: Proposed coordinates must fall within the physical limits of the selected Route suffix.")
    pdf.bullet_item("No Fee Scheduling: Pre-application planning meetings do not require checkout payment.")
    pdf.bullet_item("Authorization Certificate: If the applicant company is not the property owner of record, an Authorization Certificate signed by the owner is mandatory.")
    pdf.bullet_item("Calculated Road Surface Fees: Opening dimensions (Length x Width) automatically dictate the fee structure based on physical square footage.")

    # Section 9: Required Fields & Validations
    pdf.add_page()
    pdf.chapter_title("9", "Required Fields & Validations")
    headers_req = ["Form Section", "Field Name", "Type", "Validation Criteria"]
    req_data = [
        ["Owner Info", "Lot Owner Company", "String", "Mandatory; must match business registry."],
        ["Owner Info", "Contact Phone", "Numeric", "Must be formatted as (XXX)-XXX-XXXX."],
        ["Location", "Route", "Dropdown", "Must select from active state highway routes."],
        ["Location", "Block / Lot", "String", "Mandatory; alphanumeric permitted."],
        ["Dimensions", "Length / Width", "Numeric", "Positive values required; dictates fee."],
        ["Attachments", "Site Plans", "Upload", "Mandatory; PDF format recommended."],
        ["Checkout", "Card Number", "Numeric", "16-digit valid credit card string."],
        ["Checkout", "CVV / Expiry", "Numeric", "3-digit CVV, year must be in the future."]
    ]
    pdf.add_table(headers_req, req_data, [35, 45, 25, 75])

    # Section 10: Status Flow & Lifecycle
    pdf.chapter_title("10", "Status Flow & Lifecycle")
    pdf.bullet_item("Draft: Form created but payment has not been successfully processed.")
    pdf.bullet_item("Submitted / Paid: Fee paid; visible to NJDOT staff.")
    pdf.bullet_item("Under Review: Assigned to an engineering analyst for design check.")
    pdf.bullet_item("Action Required: Files missing or revisions needed; returned to applicant's Action Items grid.")
    pdf.bullet_item("Approved / Issued: Final permit generated and released as a PDF.")
    pdf.bullet_item("Rejected: Spacing safety issues or local zoning denials; file closed.")

    # Section 11: Approval Workflow
    pdf.chapter_title("11", "Approval Workflow")
    pdf.paragraph_text(
        "1. Customer submits application and pays fee.\n"
        "2. System conducts automated spatial GIS routing checks.\n"
        "3. NJDOT Engineer reviews design plans and drainage metrics.\n"
        "4. Inspector coordinates a physical roadside field check.\n"
        "5. Final sign-off by Section Manager; permit is issued digitally."
    )

    # Section 12: Data Requirements
    pdf.chapter_title("12", "Data Requirements")
    pdf.bullet_item("Numeric Precision: Opening sizes, pipe runoff coefficients, and mileposts must be decimal values.")
    pdf.bullet_item("Date Stamps: Dates are validated and formatted exclusively as MM/DD/YYYY.")
    pdf.bullet_item("File Upload Limits: Enforces maximum size limits per upload and accepts only safe extensions (PDF, DOC, DOCX, JPG, PNG).")

    # Section 13: UI Components & Controls
    pdf.add_page()
    pdf.chapter_title("13", "UI Components & Controls")
    pdf.bullet_item("Kendo UI Grid: Used for Action Items, Permit History, and Payment Activity grids. Supports sorting, server-side data loading, and pagination.")
    pdf.bullet_item("Kendo DatePicker: Custom date selector. Input fields are updated directly via JavaScript to bypass flaky calendar popup clicks.")
    pdf.bullet_item("Kendo NumericTextBox: Restricts coordinate or dimension fields to numbers.")
    pdf.bullet_item("Kendo PanelBar: Handles expandable navigation menus.")

    # Section 14: Document Upload/Download Workflow
    pdf.chapter_title("14", "Document Upload/Download Workflow")
    pdf.paragraph_text(
        "Upload Flow:\n"
        "- The user drags a file into the Kendo Upload dropzone or clicks to select a local file.\n"
        "- An asynchronous POST request uploads the file to a secure temporary directory.\n"
        "- Upon completion, the system shows a green checkmark icon (`.k-file-success` or `.k-i-check`)."
    )
    pdf.paragraph_text(
        "Download Flow:\n"
        "- Exporting grids (Excel/CSV) triggers a backend query which bundles data into a file stream and initiates a browser download.\n"
        "- Accessing generated permits or invoices opens an inline popup window with authentication cookies carried over automatically."
    )

    # Section 15: Search & Grid Functionality
    pdf.chapter_title("15", "Search & Grid Functionality")
    pdf.bullet_item("Search Criteria: Standard search boxes filter Kendo grids instantly based on record IDs or addresses.")
    pdf.bullet_item("Pagination: Handles large datasets via fast pagination controls.")
    pdf.bullet_item("Export Utility: Extracts the active grid view into a spreadsheet.")

    # Section 16: Integration Points
    pdf.chapter_title("16", "Integration Points")
    pdf.bullet_item("NJ Common Checkout: Redirects user payments to New Jersey's state financial infrastructure.")
    pdf.bullet_item("NJDOT GIS/Map Services: Automatically validates route coordinates and setbacks.")

    # Section 17: Error Handling & Validation Rules
    pdf.add_page()
    pdf.chapter_title("17", "Error Handling & Validation Rules")
    pdf.bullet_item("Mandatory fields: Empty values trigger immediate red borders and a top-level alert summary panel.")
    pdf.bullet_item("Incorrect types: Entering letters into numeric boxes is rejected. Dates must fit the MM/DD/YYYY format.")
    pdf.bullet_item("Invalid credentials: Failed logins display a modal pop-up error: 'You have entered an invalid email address or password.'")

    # Section 18: Automation Coverage Summary
    pdf.chapter_title("18", "Automation Coverage Summary")
    pdf.paragraph_text(
        "The customer portal is automated with a Python-based Playwright framework using Page Object Models (POMs) and Pytest. The suite supports parallel execution using xdist and incorporates cross-process file locks to prevent database conflicts during authentication."
    )

    # Section 19: Test Scenarios Covered
    pdf.chapter_title("19", "Test Scenarios Covered")
    headers_scen = ["Test Scenario", "Verified Flow", "Expected Outcome"]
    scen_data = [
        ["test_login_page_api_validation", "Validates login page inputs.", "Email/password mandatory checks pass."],
        ["test_utility_opening", "Submit road openings and complete payment.", "Dimensions calculated, pays successfully."],
        ["test_drainage", "Submit drainage connection and runoff data.", "Hydrology checks complete, redirects checkout."],
        ["test_erection_pole", "Submit utility pole erection request.", "Spacing details filled, saves successfully."],
        ["test_highway_occupancy", "Request temporary highway closures.", "Staging details submitted, paid successfully."],
        ["test_letter_interest", "Submit access pre-planning inquiry.", "Saves successfully without checkout fee."],
        ["test_lot_consolidation", "Submit lot consolidation mapping.", "Saves maps and routes to payment gateway."],
        ["test_major_planning", "Submit complex subdivision details.", "Spacing grids completed, paid successfully."],
        ["test_pre_application_meeting", "Request pre-application planning session.", "Meeting agenda saved without checkout fee."],
        ["test_street_intersection", "Request connection of street intersections.", "Saves layouts and routes to payment gateway."],
        ["test_payment_activity_filters", "Filter activity by multiple timeframes and export.", "Verifies grid updates dynamically and exports CSV."]
    ]
    pdf.add_table(headers_scen, scen_data, [45, 65, 70])

    # Section 20: Gaps & Missing Coverage
    pdf.add_page()
    pdf.chapter_title("20", "Gaps & Missing Coverage")
    pdf.bullet_item("Attachment Limit boundaries: Uploading extremely large plans or multiple document sets.")
    pdf.bullet_item("Conditional Fields: Verification of validations when changing permit choices mid-entry.")

    # Section 21: Known Limitations
    pdf.chapter_title("21", "Known Limitations")
    pdf.bullet_item("AJAX Latency: Kendo loading masks sometimes cause flaky clicks under server load, resolved by explicit hidden-mask wait conditions.")
    pdf.bullet_item("Zoom Layout Shifts: Elements shift under different browser zoom settings, requiring force-clicks on certain checkbox labels.")

    # Section 22: Team Knowledge Base
    pdf.chapter_title("22", "Team Knowledge Base")
    pdf.bullet_item("Auth Cache: State files are cached inside '.auth/auth_state.json'. Clear this to trigger fresh logins.")
    pdf.bullet_item("Staggered delays: Workers delay starting by 4-second intervals to avoid overloading the test server.")

    # Section 23: AI Learning Notes
    pdf.chapter_title("23", "AI Learning Notes")
    pdf.bullet_item("Kendo DatePicker direct set: The calendar picker UI is highly unstable under automation. Set values directly via window.jQuery/JavaScript evaluation.")

    # Section 24: Future Automation Opportunities
    pdf.chapter_title("24", "Future Automation Opportunities")
    pdf.bullet_item("E2E Integration: Linking customer submission with Staff Portal approval steps to test full regulatory workflows.")

    # Section 25: Future Product Enhancement Opportunities
    pdf.chapter_title("25", "Future Product Enhancement Opportunities")
    pdf.bullet_item("GIS coordinate selector: An interactive pin-drop map interface replacing manual milepost inputs.")
    pdf.bullet_item("Autofill Company Profiles: Automatic registry lookup using corporate tax registration databases.")
    
    # Save the PDF file
    output_path = r"c:\Users\Mohan(QAQC)\PlaywrightProjects\NJDOT_EPermitting_System\NJDOT_EPermitting_System_Documentation.pdf"
    pdf.output(output_path)
    print(f"[INFO] PDF documentation generated successfully at: {output_path}")

if __name__ == "__main__":
    generate_pdf()
