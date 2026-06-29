import os
import sys
from fpdf import FPDF

class NJDOTPDF(FPDF):
    def header(self):
        # Draw top decorative header band in NJDOT Blue
        self.set_fill_color(28, 54, 115) # Navy Blue
        self.rect(0, 0, 210, 20, "F")
        
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.set_xy(10, 5)
        self.cell(0, 10, "NJDOT Outdoor Advertising Portal - Comprehensive Reference Guide", 0, 0, "L")
        
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
        self.set_text_color(28, 54, 115) # NJDOT Navy
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
        self.set_fill_color(28, 54, 115)
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
            self.set_fill_color(245, 248, 255) if fill else self.set_fill_color(255, 255, 255)
            
            # Calculate max lines needed for this row
            max_lines = 1
            row_heights = []
            for i, text in enumerate(row):
                # Simple approximation of line count
                chars_per_line = col_widths[i] // 2.2
                lines = max(1, -(-len(str(text)) // int(chars_per_line)))
                max_lines = max(max_lines, lines)
            
            row_height = max_lines * 4.5 + 2.5
            
            # Draw cells
            x_start = self.get_x()
            for i, text in enumerate(row):
                # multi_cell can be tricky for matching heights, so we use rect + multi_cell for wrap or simple cell
                x = self.get_x()
                y = self.get_y()
                self.rect(x, y, col_widths[i], row_height, "DF" if fill else "D")
                self.multi_cell(col_widths[i], 4, str(text), 0, "L", False)
                self.set_xy(x + col_widths[i], y)
            
            self.ln(row_height)
            fill = not fill
        self.ln(3)

def generate_pdf():
    pdf = NJDOTPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(True, margin=20)
    
    # ---------------------------------------------------------
    # COVER PAGE
    # ---------------------------------------------------------
    pdf.add_page()
    # Disable header/footer for cover page
    pdf.set_fill_color(250, 252, 255)
    pdf.rect(0, 0, 210, 297, "F")
    
    pdf.set_fill_color(28, 54, 115)
    pdf.rect(0, 0, 210, 80, "F")
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_xy(15, 25)
    pdf.cell(0, 12, "NEW JERSEY", 0, 1, "L")
    pdf.cell(0, 12, "DEPARTMENT OF TRANSPORTATION", 0, 1, "L")
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(220, 230, 255)
    pdf.ln(5)
    pdf.cell(0, 8, "Outdoor Advertising Customer Portal Reference Guide", 0, 1, "L")
    
    pdf.set_text_color(28, 54, 115)
    pdf.set_xy(15, 110)
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 8, "COMPLETE BUSINESS, FUNCTIONAL,\nWORKFLOW, & AUTOMATION KNOWLEDGE BASE")
    
    pdf.set_fill_color(100, 110, 120)
    pdf.rect(15, 130, 80, 2, "F")
    
    pdf.set_xy(15, 140)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, "A professional, reverse-engineered solution guide detailing the NJDOT Outdoor Advertising customer module, business logic, workflows, validations, and automated coverage schemas.\n\nPrepared for Developers, Business Analysts, Product Owners, UI/UX Teams, QA Engineers, and Automation Teams.")
    
    pdf.set_xy(15, 210)
    headers_meta = ["Document Metadata", "Detail"]
    meta_data = [
        ["System Name", "NJDOT Outdoor Advertising (ODA) Customer Portal"],
        ["Version", "2.1 (Production Release Reference)"],
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
        "The New Jersey Department of Transportation (NJDOT) administers the Outdoor Advertising (ODA) program to regulate roadside signs along state highways. This regulation ensures highway safety, public aesthetic protection, and compliance with the federal Highway Beautification Act (HBA)."
    )
    pdf.paragraph_text(
        "The NJDOT Outdoor Advertising Customer Portal acts as the public-facing e-permitting module. It enables companies, independent dealers, and agents to submit digital applications, process administrative fees, execute license/permit transfers, register business entity name changes, and track action items and history. By digitizing these flows, NJDOT ensures transparency, decreases lead time, eliminates paper-based errors, and establishes a robust audit trail."
    )
    pdf.paragraph_text(
        "This document provides a highly detailed functional, technical, and automated overview of the system, enabling rapid onboarding of developers, QA teams, product owners, and business analysts."
    )
    
    # Section 2: Module Overview
    pdf.chapter_title("2", "Module Overview")
    pdf.paragraph_text(
        "The NJDOT Outdoor Advertising customer portal is organized into distinct sub-modules, which collectively support the end-to-end lifecycle of licenses, permits, and financial transactions:"
    )
    pdf.bullet_item("Portal Access & Security: Email-based registration, password authentication, application selection, and session logout controls.")
    pdf.bullet_item("Account Registration: Pre-submission profiling system that dynamically adapts based on DBE/SBE (Disadvantaged/Small Business Enterprise) status.")
    pdf.bullet_item("Submit Application Panel: Centralized dispatch menu for new License applications, new Permit applications, Permit Transfer requests, and Name Change requests.")
    pdf.bullet_item("Action Items Grid: Task management console displaying pending requirements, information requests, and remediation items.")
    pdf.bullet_item("Applications History: Repository for all historical submissions, featuring status tracking, details viewing, and Excel exporting.")
    pdf.bullet_item("Payment Activity: Financial ledger containing transaction details, date filters, and Excel download exports.")
    pdf.bullet_item("Checkout Gateway: Integration with the secure New Jersey Common Checkout portal for card-based fee payments.")

    # Section 3: Business Purpose
    pdf.add_page()
    pdf.chapter_title("3", "Business Purpose")
    pdf.paragraph_text(
        "The primary business driver behind the ODA Customer Portal is to streamline highway billboard regulation and dealer licensing. Specifically, the system resolves key operational objectives:"
    )
    pdf.bullet_item("Legal Compliance: Enforces Title 27 of the New Jersey Statutes Annotated (NJSA) and New Jersey Administrative Code (NJAC) 16:41C.")
    pdf.bullet_item("Revenue Collection: Automates the receipt and processing of non-refundable application and permit fees.")
    pdf.bullet_item("Verification & Inspection: Collects precise site coordinates, dimensions, sketches, and owner consents for physical highway inspections by NJDOT engineers.")
    pdf.bullet_item("Administrative Efficiency: Reduces processing time from months to days by providing real-time validation and self-service dashboards.")

    # Section 4: User Roles & Permissions
    pdf.chapter_title("4", "User Roles & Permissions")
    pdf.paragraph_text(
        "The portal is designed around a multi-tier security model. The active customer roles include:"
    )
    pdf.bullet_item("Independent Dealer / Owner: Full access to register company profiles, apply for licenses, request sign permits, process payments, and request transfers.")
    pdf.bullet_item("Appointed Agent: Authorized representative acting on behalf of property owners or sign dealers to submit designs and inspect permit logs.")
    pdf.bullet_item("Property Owner (Third Party): Consents to the physical installation of signs on private property (documents uploaded via portal by the dealer).")
    pdf.bullet_item("NJDOT Staff / Approver (Staff Portal): Backend user who performs visual inspection, reviews applicant documents, approves/rejects submissions, and tracks payment ledger audits.")

    # Section 5: Functional Overview
    pdf.add_page()
    pdf.chapter_title("5", "Functional Overview")
    pdf.paragraph_text(
        "The core functionality of the customer portal revolves around five core operational areas:"
    )
    pdf.chapter_subtitle("A. Profile Management & Creation")
    pdf.paragraph_text(
        "Allows external businesses to register their organization in the NJDOT system. The system enforces strict validations on DBE/SBE identification and automatically flags profiles for administrative review."
    )
    pdf.chapter_subtitle("B. Permit Submission")
    pdf.paragraph_text(
        "Collects engineering drawings, site sketches, dimensional metrics (sign face width and height), and county/state highway references to register a new roadside structure."
    )
    pdf.chapter_subtitle("C. License Management")
    pdf.paragraph_text(
        "Validates that a business entity holds a valid Outdoor Advertising License. An entity must possess an active license before they can own or lease physical permit structures."
    )
    pdf.chapter_subtitle("D. Permit Transfers & Name Changes")
    pdf.paragraph_text(
        "Maintains the chain of custody for highway advertising locations. Users can transfer permits to other licensed dealers or request name corrections on official documentation."
    )
    pdf.chapter_subtitle("E. Payment Auditing")
    pdf.paragraph_text(
        "Links checkout identifiers with active applications, ensuring no unpaid permit or license enters the review queue."
    )

    # Section 6: End-to-End Workflows
    pdf.add_page()
    pdf.chapter_title("6", "End-to-End Workflows")
    
    pdf.chapter_subtitle("Workflow 1: Account Creation (DBE vs Non-DBE)")
    pdf.bullet_item("Step 1: User clicks 'Create an Account' on the main login screen.")
    pdf.bullet_item("Step 2: System prompts: 'Are you a Federal DBE/SBE?'")
    pdf.bullet_item("Step 3: If YES, System displays DBE Registration form. The Company Name field is bypassed/hidden (as the profile links to certified DBE databases).")
    pdf.bullet_item("Step 4: If NO, System displays standard Registration form. Company Name and Federal DBE/SBE ID numbers are mandatory fields.")
    pdf.bullet_item("Step 5: User inputs address, zip, phone, email, billing coordinates, corporate officers, and Point of Contact (POC) details.")
    pdf.bullet_item("Step 6: User clicks Submit, saving profile in 'Pending Validation' state.")
    
    pdf.chapter_subtitle("Workflow 2: Outdoor Advertising License Application")
    pdf.bullet_item("Step 1: Logged-in user selects the Submit Application menu.")
    pdf.bullet_item("Step 2: User clicks 'License Application' button.")
    pdf.bullet_item("Decision point: System evaluates if account already holds a license. If yes, it launches a blocking popup ('STOP: Account holds license') and exits.")
    pdf.bullet_item("Step 3: If no license exists, user fills text fields, checks statutory certifications, and enters signee name and title.")
    pdf.bullet_item("Step 4: User clicks Complete Payment, triggering the record save.")
    pdf.bullet_item("Step 5: Redirects to NJ Common Checkout to process the license fee.")
    pdf.bullet_item("Step 6: Upon successful transaction, returns to portal success page.")

    pdf.chapter_subtitle("Workflow 3: Permit Structure Application")
    pdf.bullet_item("Step 1: Logged-in user clicks 'Submit Application' and clicks 'Permit Application'.")
    pdf.bullet_item("Step 2: A modal displays to confirm domain environment, user clicks OK.")
    pdf.bullet_item("Step 3: Form requires Face Height and Face Width (numeric feet).")
    pdf.bullet_item("Step 4: Selects Sign Type and Sign Material from dropdowns.")
    pdf.bullet_item("Step 5: Selects County (e.g. Atlantic) and fills in precise location details.")
    pdf.bullet_item("Step 6: Uploads the location sketch document.")
    pdf.bullet_item("Step 7: Enters Property Owner details and uploads the signed Consent document.")
    pdf.bullet_item("Step 8: Clicks Complete Payment. Popup displays the SUB reference number (e.g. SUB-2026-1020).")
    pdf.bullet_item("Step 9: Directs to Checkout, processes payment, and displays success screen.")

    # Section 7: Navigation Flow
    pdf.add_page()
    pdf.chapter_title("7", "Navigation Flow")
    pdf.paragraph_text(
        "The application's structural navigation flow is mapped as follows:"
    )
    pdf.paragraph_text(
        "NJDOT Login Page\n"
        "  |\n"
        "  +-- [Action] Create an Account --> Company Registration Forms\n"
        "  |\n"
        "  +-- [Action] Login --> Application Select Portal\n"
        "                           |\n"
        "                           +--> Outdoor Advertising Dashboard\n"
        "                                  |\n"
        "                                  +--> Submit Application Drawer\n"
        "                                  |      |-- License Application\n"
        "                                  |      |-- Permit Application\n"
        "                                  |      |-- Permit Transfer\n"
        "                                  |      +-- Name Change\n"
        "                                  |\n"
        "                                  +--> Action Items Grid\n"
        "                                  |\n"
        "                                  +--> Applications History Grid\n"
        "                                  |\n"
        "                                  +--> Payment Activity Grid\n"
        "                                  |\n"
        "                                  +--> Logout Link"
    )

    # Section 8: Business Rules
    pdf.chapter_title("8", "Business Rules")
    pdf.bullet_item("License Pre-requisite: A user cannot apply for a permit structure unless their business possesses an active, valid Outdoor Advertising License.")
    pdf.bullet_item("Deduplication: A single tax entity is restricted to a single License Profile. Duplicate submissions will trigger an validation error or block.")
    pdf.bullet_item("Unpaid Submissions: Applications created but abandoned at the payment gateway are flagged as 'Draft/Unpaid' and will not be visible to staff reviewers.")
    pdf.bullet_item("Size Restrictions: Minimum and maximum face dimensions apply. Extreme dimensions flag the permit for advanced administrative variance review.")

    # Section 9: Required Fields & Validations
    pdf.add_page()
    pdf.chapter_title("9", "Required Fields & Validations")
    headers_req = ["Form Section", "Field Name", "Type", "Validation Criteria"]
    req_data = [
        ["Login", "Email", "String", "Must be a valid email format; mandatory."],
        ["Login", "Password", "String", "Mandatory; minimum security check."],
        ["Create Account", "Company Name", "String", "Mandatory only if DBE/SBE is 'No'."],
        ["Create Account", "Zip Code", "Numeric", "Exactly 5 digits required."],
        ["Create Account", "POC Email", "String", "POC Email & Confirm Email must match."],
        ["Permit App", "Face Height", "Numeric", "Mandatory; integer feet (> 0)."],
        ["Permit App", "Face Width", "Numeric", "Mandatory; integer feet (> 0)."],
        ["Permit App", "Sign Location", "String", "Description of highway milepost/intersection."],
        ["Permit App", "County", "Dropdown", "Must select from list (e.g. Atlantic)."],
        ["Permit App", "Consent Doc", "Upload", "PDF/Word file of owner permission."],
        ["Permit App", "Sketch Doc", "Upload", "PDF/Word file showing sign placement."],
        ["Permit Transfer", "Permit No", "Numeric", "Mandatory; must match an active permit."]
    ]
    pdf.add_table(headers_req, req_data, [35, 45, 25, 75])

    # Section 10: Status Flow & Lifecycle
    pdf.chapter_title("10", "Status Flow & Lifecycle")
    pdf.paragraph_text(
        "Every application progresses through a formal state machine during its lifecycle:"
    )
    pdf.bullet_item("Draft: User started filling the form, but has not completed payment.")
    pdf.bullet_item("Submitted / Paid: Fee paid; application enters the NJDOT queue.")
    pdf.bullet_item("Under Review: Assigned to an NJDOT analyst for file checking.")
    pdf.bullet_item("Inspection Scheduled: Highway inspector scheduled to verify highway coordinates and safety clearance.")
    pdf.bullet_item("Approved / Issued: Permit/License active and documents generated.")
    pdf.bullet_item("Returned / Action Required: Documents missing or corrections required. Appears in customer's 'Action Items' grid.")
    pdf.bullet_item("Rejected: Denied due to safety violations, dimensional issues, or local ordinances.")

    # Section 11: Approval Workflow
    pdf.add_page()
    pdf.chapter_title("11", "Approval Workflow")
    pdf.paragraph_text(
        "NJDOT enforces a strict multi-stage validation before permit issuance:"
    )
    pdf.paragraph_text(
        "1. Submission Check: Initial verification of document clarity and fee payment.\n"
        "2. Location Verification: Analyst checks if the proposed structure is within regulated distance of interstate interchanges or scenic corridors.\n"
        "3. Physical Inspection: Staff travels to site or uses GIS map coordinate checking to confirm setbacks, height, and spacing from other signs.\n"
        "4. Legal/Zoning Check: Ensures municipal approval and owner consent are in order.\n"
        "5. Final Sign-off: Section Manager signs and releases the PDF permit."
    )

    # Section 12: Data Requirements
    pdf.chapter_title("12", "Data Requirements")
    pdf.paragraph_text(
        "The portal handles structured data models and requires standard database formats:"
    )
    pdf.bullet_item("Address: Enforces standard postal abbreviations and US State codes.")
    pdf.bullet_item("Corporate Officers: Requires at least a President, Vice President, Secretary, and Treasurer name to complete registration.")
    pdf.bullet_item("Date Stamps: Dates are validated and formatted exclusively as MM/DD/YYYY.")
    pdf.bullet_item("File Upload Limits: Enforces maximum size limits per upload and accepts only safe extensions (PDF, DOC, DOCX, JPG, PNG).")

    # Section 13: UI Components & Controls
    pdf.chapter_title("13", "UI Components & Controls")
    pdf.paragraph_text(
        "The portal is built using high-performance, responsive UI elements:"
    )
    pdf.bullet_item("Kendo UI Grid: Used for Action Items, Applications History, and Payment Activity. Supports sorting, Ajax-based lazy loading, and paginating.")
    pdf.bullet_item("Kendo DropDownList: Dropdowns with integrated search boxes (e.g. County, State, Sign Type).")
    pdf.bullet_item("Kendo Upload: Asynchronous chunk-based file upload dropzones with progress bars and validation status checks.")
    pdf.bullet_item("Kendo NumericTextBox: Restricts input fields to numerical values with up/down arrows.")

    # Section 14: Document Upload/Download Workflow
    pdf.add_page()
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
    pdf.paragraph_text(
        "The dashboard search bar utilizes live client-side Kendo grid filtering. Key capabilities:"
    )
    pdf.bullet_item("Auto-suggest: Searches filter matches across application IDs, dealer names, and addresses.")
    pdf.bullet_item("Fast Pagination: Page-size controls allow viewing 10, 20, or 50 items. Direct page inputs let users skip pages quickly.")
    pdf.bullet_item("Export Utility: Extracts the filtered view into a fully-formatted spreadsheet.")

    # Section 16: Integration Points
    pdf.chapter_title("16", "Integration Points")
    pdf.bullet_item("NJ Common Checkout: Redirection API that offloads secure payment information collection and processing to New Jersey's state financial infrastructure.")
    pdf.bullet_item("DBE/SBE database: Verifies corporate profile details for certified Disadvantaged Business Enterprises.")
    pdf.bullet_item("NJDOT GIS/Map Services: Connects sign coordinates to verify local zoning lines and mileage calculations.")

    # Section 17: Error Handling & Validation Rules
    pdf.chapter_title("17", "Error Handling & Validation Rules")
    pdf.bullet_item("Mandatory fields: Empty values trigger immediate red borders and a top-level alert summary panel.")
    pdf.bullet_item("Incorrect types: Entering letters into numeric boxes is rejected. Dates must fit the MM/DD/YYYY format.")
    pdf.bullet_item("Invalid credentials: Failed logins display a modal pop-up error: 'You have entered an invalid email address or password.'")

    # Section 18: Automation Coverage Summary
    pdf.add_page()
    pdf.chapter_title("18", "Automation Coverage Summary")
    pdf.paragraph_text(
        "The NJDOT Outdoor Advertising customer portal is fully automated with a state-of-the-art Playwright test automation suite written in Python, utilizing Page Object Models (POMs) and Pytest. The suite is configured for parallel execution using xdist, maximizing speed while using sequentially scheduled cross-process file locks to prevent database conflicts during authentication."
    )
    pdf.paragraph_text(
        "The automated framework is structured with clean separation of concerns: Pages are isolated inside `pages/` POM classes, test data is pulled from `testdata/`, configurations are centralized in `utils/config.py`, and hooks/fixtures are defined globally in `conftest.py`."
    )

    # Section 19: Test Scenarios Covered
    pdf.chapter_title("19", "Test Scenarios Covered")
    headers_scen = ["Test Scenario", "Verified Flow", "Expected Outcome"]
    scen_data = [
        ["test_portal_login_and_logout", "Login using valid credentials and logout.", "Redirects to dashboard and clean exit."],
        ["test_login_empty_credentials", "Login with blank fields.", "Asserts mandatory email/password warnings."],
        ["test_login_invalid_password", "Valid email with random password.", "Asserts invalid credentials modal and dismisses it."],
        ["test_create_account_dbe_yes", "Start account creation indicating DBE status.", "Bypasses company name, verifies submit button."],
        ["test_create_account_dbe_no", "Start account creation indicating Non-DBE status.", "Company name required, fills form via Faker."],
        ["test_license_application_payment", "Fill license form and complete gateway checkout.", "Creates draft, navigates payment, confirms success."],
        ["test_permit_application_popup", "Submit permit structure with locations and attachments.", "Asserts domain alert, uploads sketch, pays successfully."],
        ["test_permit_transfer_payment", "Transfer active permit and process fee.", "Fills permit numbers, uploads document, completes checkout."],
        ["test_name_change_flow", "Name correction application submission.", "Saves successfully without charging fee, returns home."],
        ["test_action_items_pagination", "Paginates action items grid to last page.", "Confirms Kendo grid handles data volume."],
        ["test_applications_history_export", "Search, clear filters, and download history.", "Confirms file download saved in downloads/."],
        ["test_payment_activity_filters", "Filter activity by multiple timeframes and export.", "Verifies grid updates dynamically and exports CSV."]
    ]
    pdf.add_table(headers_scen, scen_data, [45, 65, 70])

    # Section 20: Gaps & Missing Coverage
    pdf.add_page()
    pdf.chapter_title("20", "Gaps & Missing Coverage")
    pdf.bullet_item("Form Field Length Boundaries: Testing maximum character inputs on address and company text boxes.")
    pdf.bullet_item("Document File Type Validations: Negative tests attempting to upload invalid extensions (e.g. .exe, .zip) to check if the portal rejects them.")
    pdf.bullet_item("Session Timeout: Automation behavior when the page remains idle until the session token expires.")
    pdf.bullet_item("Refund Flows: Automating the refund/reversal request from the payment activity tab.")

    # Section 21: Known Limitations
    pdf.chapter_title("21", "Known Limitations")
    pdf.bullet_item("AJAX Latency: Kendo UI widgets sometimes delay loading dynamic data under heavy server load, requiring robust explicit wait conditions rather than hardcoded timeouts.")
    pdf.bullet_item("Payment Sandbox: The credit card gateway uses a test environment card number. Real credit card testing must be executed in production manually.")
    pdf.bullet_item("Zoom Incompatibility: The UI layout shifts slightly under CSS zoom levels, requiring force-clicks on certain Kendo checkbox elements.")

    # Section 22: Team Knowledge Base
    pdf.chapter_title("22", "Team Knowledge Base")
    pdf.paragraph_text(
        "Critical operational notes for developers and QA engineers:"
    )
    pdf.bullet_item("Authentication State: Authentication is cached per worker process inside the '.auth/' directory. To trigger a completely fresh physical login, clear the '.auth/' folder.")
    pdf.bullet_item("Kendo DroDowns: Do not attempt to input text directly to select options. Always use the Kendo JavaScript API (`_select_first_valid_option`) to ensure dropdown change triggers fire properly.")
    pdf.bullet_item("Parallel staggered delay: Tests run on multiple cores. To avoid overloading the test server with simultaneous dashboard queries, each worker ID has a staggered startup delay of 4 seconds.")

    # Section 23: AI Learning Notes
    pdf.chapter_title("23", "AI Learning Notes")
    pdf.paragraph_text(
        "Learnings for agentic coding and test generation platforms:"
    )
    pdf.bullet_item("Popups and PDF Capture: Inline PDF previews open in separate browser tabs without standard download events. Intercept them using context 'popup' handlers and fetch bytes via context request APIs.")
    pdf.bullet_item("Lock Files: Parallel runs require an exclusive login lock file to stagger the initial login calls. This avoids concurrent session overwrites.")

    # Section 24: Future Automation Opportunities
    pdf.chapter_title("24", "Future Automation Opportunities")
    pdf.bullet_item("Email Validation Automation: Intercept emails dispatched to the point of contact to check verification links.")
    pdf.bullet_item("Cross-Browser Suite: Extend test execution to Safari (Webkit) and Firefox to ensure complete cross-browser layout consistency.")

    # Section 25: Future Product Enhancement Opportunities
    pdf.chapter_title("25", "Future Product Enhancement Opportunities")
    pdf.bullet_item("Autofill Company Registry: Integrate with New Jersey state business databases to fetch address and officer details automatically.")
    pdf.bullet_item("Interactive Mapping: Add GIS map selection tool so applicants can select sign coordinates by dropping a pin, rather than manually typing latitude/longitude.")
    
    # Save the PDF file
    output_path = r"c:\Users\Mohan(QAQC)\PlaywrightProjects\NJDOT_Outdoor_Advertising\NJDOT_Outdoor_Advertising_Documentation.pdf"
    pdf.output(output_path)
    print(f"[INFO] PDF documentation generated successfully at: {output_path}")

if __name__ == "__main__":
    generate_pdf()
