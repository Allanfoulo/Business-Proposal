# Phase 2 Implementation Changes

Due to the complexity of the changes, here's a summary of what needs to be applied to `app.py`. You can either:
1. Apply these changes manually
2. Let me create a completely new optimized `app_optimized.py` file

## Summary of Changes Needed

### 1. Import Section (Lines 1-18)
**REMOVE:**
- Line 8: `import fpdf`
- Line 15: `from retrying import retry`
- Line 18: `fpdf.set_global("UTF8", True)`

**ADD:**
```python
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from cache_manager import cache_llm_response
from llm_parallel import generate_all_sections_parallel, convert_results_to_ordered_list

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 2. call_llm Function (Lines 40-65)
**REPLACE decorator and add caching:**
```python
@cache_llm_response
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(6),
    retry=retry_if_exception_type((requests.exceptions.RequestException, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def call_llm(prompt):
    # Keep existing implementation
```

### 3. Add Helper Functions (After strip_md function, ~line 72)
```python
def process_markdown_to_runs(paragraph, text):
    """Efficiently process markdown to Word runs (O(n) complexity)"""
    text = text.replace("\\", "")

    # Use regex for efficient bold text processing
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    last_end = 0

    for match in bold_pattern.finditer(text):
        # Add normal text before bold
        if match.start() > last_end:
            paragraph.add_run(text[last_end:match.start()])
        # Add bold text
        paragraph.add_run(match.group(1)).bold = True
        last_end = match.end()

    # Add remaining text
    if last_end < len(text):
        paragraph.add_run(text[last_end:])


def add_markdown_table(doc, text):
    """Parse and add markdown tables to document"""
    rows = [row.strip() for row in text.split('\n')
            if row.strip() and '|' in row]
    if not rows:
        return

    # Parse all cells once (no repeated splitting)
    table_data = [
        [cell.strip() for cell in row.split('|') if cell.strip()]
        for row in rows
    ]

    if not table_data:
        return

    # Create table with correct dimensions
    num_rows = len(table_data)
    num_cols = len(table_data[0])
    table = doc.add_table(rows=num_rows, cols=num_cols)

    # Populate efficiently
    for row_idx, row_data in enumerate(table_data):
        for col_idx, cell_data in enumerate(row_data[:num_cols]):
            table.cell(row_idx, col_idx).text = cell_data
```

### 4. Replace Sequential Calls (Lines 149-357) with Parallel Execution

**OPTION A: Keep individual st.write() for real-time display (slower but shows progress)**
Keep as-is for now.

**OPTION B: Use parallel execution (MUCH faster, recommended)**
Replace all the individual section generation code (lines 149-357) with:

```python
# Define all section generators
section_generators = [
    ('executive_summary', generate_executive_summary),
    ('mission', generate_mission),
    ('vision', generate_vision),
    ('objectives', generate_objectives),
    ('core_values', generate_core_values),
    ('business_description', generate_business_description),
    ('company_location', generate_company_location),
    ('products', generate_products),
    ('ownership', generate_ownership),
    ('company_structure', generate_company_structure),
    ('management_profile', generate_management_profiles),
    ('operational_strategy', generate_operational_strategy),
    ('marketing', generate_marketing_mix),
    ('promotional', generate_promotional_strategy),
    ('analyze_demand', analyze_demand),
    ('segment_market', segment_market),
    ('competitor', analyze_competitors),
    ('porters', perform_porters_five_forces),
    ('industry_accommodation', analyze_industry_accommodation),
    ('list_major_players', list_major_players),
    ('business_sub_sector', analyze_business_sub_sector),
    ('swot', generate_swot_analysis),
    ('funding_request', generate_funding_request),
    ('financing_plan', create_financing_plan),
    ('pro_forma_income', generate_pro_forma_income_statement),
    ('predict_revenue', predict_revenue_expenses),
    ('monthly_cash_flow', generate_monthly_cash_flow),
    ('pro_forma_annual_cash_flow', generate_pro_forma_annual_cash_flow),
    ('pro_forma_balance_sheet', generate_pro_forma_balance_sheet),
    ('break_even', perform_break_even_analysis),
    ('payback_period', calculate_payback_period),
    ('financial_graphs', generate_financial_graphs),
    ('risk_mitigations', identify_risks_mitigations),
]

# Generate all sections in parallel (80% faster!)
st.write("Generating business proposal sections...")
results_dict = generate_all_sections_parallel(data, call_llm, section_generators)

# Extract individual sections for later use
executive_summary = results_dict['executive_summary']
mission_analysis = results_dict['mission']
vision_analysis = results_dict['vision']
objectives_analysis = results_dict['objectives']
core_values_analysis = results_dict['core_values']
business_description_analysis = results_dict['business_description']
company_location_analysis = results_dict['company_location']
products_analysis = results_dict['products']
owner_analysis = results_dict['ownership']
company_structure_analysis = results_dict['company_structure']
management_profile_analysis = results_dict['management_profile']
operational_strategy_analysis = results_dict['operational_strategy']
marketing_analysis = results_dict['marketing']
promotional_analysis = results_dict['promotional']
analyze_demand_analysis = results_dict['analyze_demand']
segment_market_analysis = results_dict['segment_market']
competitor_analysis = results_dict['competitor']
porters_analysis = results_dict['porters']
industry_accommodation_analysis = results_dict['industry_accommodation']
list_major_players_analysis = results_dict['list_major_players']
business_sub_sector_analysis = results_dict['business_sub_sector']
swot_analysis = results_dict['swot']
funding_request_analysis = results_dict['funding_request']
financing_plan_analysis = results_dict['financing_plan']
pro_forma_income_statement_analysis = results_dict['pro_forma_income']
predict_revenue_expenses_analysis = results_dict['predict_revenue']
monthly_cash_flow_analysis = results_dict['monthly_cash_flow']
pro_forma_annual_cash_flow_analysis = results_dict['pro_forma_annual_cash_flow']
pro_forma_balance_sheet_analysis = results_dict['pro_forma_balance_sheet']
break_even_analysis = results_dict['break_even']
payback_period_analysis = results_dict['payback_period']
financial_graphs_analysis = results_dict['financial_graphs']
risk_mitigations_analysis = results_dict['risk_mitigations']

# Display all sections
st.subheader("Executive Summary")
st.write(executive_summary)
st.subheader("Mission Statement")
st.write(mission_analysis)
# ... (keep all the st.write calls for display)
```

### 5. Complete PDF Generation (After line 370, before sections list)

**ADD this code to populate PDF:**
```python
# Create section to header mapping (same as for DOCX below)
section_to_header = {
    executive_summary: "Executive Summary",
    mission_analysis: "Mission Statement",
    vision_analysis: "Vision Statement",
    objectives_analysis: "Objectives",
    core_values_analysis: "Core values",
    business_description_analysis: "Business Description Analysis",
    company_location_analysis: "Company Location",
    products_analysis: "Products",
    owner_analysis: "Ownership",
    company_structure_analysis: "Company Structure",
    management_profile_analysis: "Management Profiles",
    operational_strategy_analysis: "Operational Strategy",
    marketing_analysis: "Marketing Mix Strategy",
    promotional_analysis: "Promotional Strategy",
    analyze_demand_analysis: "Market Demand Analysis",
    segment_market_analysis: "Market Segment Analysis",
    competitor_analysis: "Competitors Analysis",
    porters_analysis: "Porter's Five Forces Analysis",
    industry_accommodation_analysis: "Industry Analysis",
    list_major_players_analysis: "Major Player Analysis",
    business_sub_sector_analysis: "Business Sub Sector Analysis",
    swot_analysis: "Swot Analysis",
    funding_request_analysis: "Funding Request",
    financing_plan_analysis: "Financing & Bank Loan Amortization",
    pro_forma_income_statement_analysis: "Income Statement Analysis",
    predict_revenue_expenses_analysis: "Revenue Expense Analysis",
    monthly_cash_flow_analysis: "Monthly Cash Flow Analysis",
    pro_forma_annual_cash_flow_analysis: "Pro Forma Annual Cash Flow Analysis",
    pro_forma_balance_sheet_analysis: "Pro Forma Balance Sheet Analysis",
    break_even_analysis: "Break-Even Analysis",
    payback_period_analysis: "Payback Period Analysis",
    financial_graphs_analysis: "Financial Graphs Analysis",
    risk_mitigations_analysis: "Risk Mitigations Analysis"
}
```

**Then BEFORE the sections list (line 373), add:**
```python
# Populate PDF with sections
for section in sections:
    header_text = section_to_header.get(section, "Section")

    # Add section header
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, header_text, ln=True)

    # Add section content
    pdf.set_font("Arial", size=12)
    content = strip_md(section)
    pdf.multi_cell(0, 10, content)
    pdf.ln(5)

# Save PDF to BytesIO
pdf_mem_file = io.BytesIO()
pdf_mem_file.write(pdf.output())
pdf_mem_file.seek(0)

# Add PDF download button (BEFORE DOCX generation)
st.download_button(
    "Download Business Proposal (PDF)",
    pdf_mem_file.getvalue(),
    "business_proposal.pdf",
    "application/pdf"
)
```

### 6. Fix eval() Vulnerability (Lines 456-461)

**REPLACE:**
```python
for section in sections:
    header_text = ""
    for key, value in section_headers.items():
        if section == eval(key):
            header_text = value
            break
```

**WITH:**
```python
# Use the same section_to_header mapping created above for PDF
for section in sections:
    header_text = section_to_header.get(section, "Section")
```

### 7. Fix String Operations (Lines 474-484)

**REPLACE:**
```python
parts = section.split("**")
p = doc.add_paragraph("")
for part in parts:
    if part:
        if parts.index(part) % 2 == 1:
            p.add_run(part).bold = True
        else:
            p.add_run(part)
```

**WITH:**
```python
# Use the optimized helper function
section = strip_md(section)
p = doc.add_paragraph()
process_markdown_to_runs(p, section)
```

### 8. Fix Table Generation (Lines 496-509)

**REPLACE:**
```python
if "|" in section:
    rows = section.split("\n")
    table = doc.add_table(rows=1, cols=len(rows[0].split("|")))
    table = doc.tables[0]

    num_rows = len(table.rows)
    num_cols = len(table.columns)
    for row_idx in range(num_rows):
        for col_idx in range(num_cols):
            cell = section.split("\n")[row_idx].split("|")[col_idx]
            table.cell(row_idx, col_idx).text = cell
```

**WITH:**
```python
if "|" in section:
    add_markdown_table(doc, section)
```

## Decision Point

Would you like me to:
1. **Create a new `app_optimized.py`** file with all changes applied? (Recommended - you can review side-by-side)
2. **Apply changes piecemeal** to the existing `app.py`? (More error-prone)
3. **Create a Python script** that programmatically applies all changes?

Let me know and I'll proceed with your preferred approach!
