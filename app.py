import streamlit as st
import docx
import re
import tempfile
import pathlib
import os
import io
import time
import requests
import logging
from groq import Groq
from exa_py import Exa
from string import Template
from dotenv import load_dotenv, dotenv_values
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from funtions import *
from fpdf import FPDF
from cache_manager import cache_llm_response
from llm_parallel import generate_all_sections_parallel, convert_results_to_ordered_list

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()
# Fallback to project root .env when running from worktree
root_env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
if root_env_path.exists():
    load_dotenv(dotenv_path=str(root_env_path))
    _root_env = dotenv_values(str(root_env_path))
else:
    _root_env = {}

EXA_API_KEY = os.getenv("EXA_API_KEY") or _root_env.get("EXA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or _root_env.get("GROQ_API_KEY")

#declare the exa search api
exa = Exa(api_key=EXA_API_KEY)

# Define your API Model and key (replace 'your-api-key' with the actual key)
client = Groq(api_key=GROQ_API_KEY)
utilized_model = "openai/gpt-oss-120b"

#the file path that contains the prompt
file_path = os.path.join(os.getcwd(), "plugins/modular_business_proposal")

#Functions for the Exa Search content & Parameters for our Highlights search
highlights_options = {
    "num_sentences": 7,  # how long our highlights should be
    "highlights_per_url": 1,  # just get the best highlight for each URL
}
@cache_llm_response
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(6),
    retry=retry_if_exception_type((requests.exceptions.RequestException, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def call_llm(prompt):

    proposal_parts = []
    #for question in questions:
    #Insert input data into placeholder in question prompts
    
    search_response = exa.search_and_contents(query=prompt, highlights=highlights_options, num_results=3, use_autoprompt=True)
    info = [sr.highlights[0] for sr in search_response.results]
    
    system_prompt = "You are a Business proposal generator. Read the provided contexts and, if relevant, use them to answer the user's question."
    user_prompt = f"Sources: {info}\nQuestion: {prompt}"
    
    completion = client.chat.completions.create(
        model=utilized_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1,
        max_tokens=8192,
        top_p=1,
        stream=True,
        stop=None
    )

    # Collect streamed chunks into a single response string
    streamed_parts = []
    for chunk in completion:
        try:
            content_chunk = chunk.choices[0].delta.content or ""
        except Exception:
            content_chunk = ""
        if content_chunk:
            streamed_parts.append(content_chunk)

    response_text = "".join(streamed_parts)
    response = f"Answer: {response_text}\n\n"
    proposal_parts.append(response)

    proposal_text = "\n\n".join(proposal_parts)
    return proposal_text
# Function to strip markdown and unescape characters
def strip_md(text):
    text = text.replace("**", "")  # remove bold syntax
    text = text.replace("*", "")  # remove italic syntax
    text = text.replace("#", "")  # remove headings
    text = re.sub(r'([!*_=~-])', r'\\\1', text)
    return text


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


def collect_basic_info():
    st.title("Business Proposal Generator")

    st.header("Basic Company Information")
    company_name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    location = st.text_input("Location")

    st.header("Mission and Vision")
    mission = st.text_area("Mission Statement")
    vision = st.text_area("Vision Statement")

    st.header("Products or Services")
    products_services = st.text_area("Description of Products/Services")

    st.header("Target Market")
    target_market = st.text_area("Customer Segments (e.g., demographics, location)")

    st.header("Unique Value Proposition")
    value_proposition = st.text_area("Competitive Advantage")
    
    st.header("Promotional Strategy")
    promotional_strategy=st.text_area("Mention your potential Promotional Strategy")

    st.header("Financial Information")
    current_revenue = st.number_input("Current Revenue (R)", min_value=0.0, format="%f")
    current_expenses = st.number_input("Current Expenses (R)", min_value=0.0, format="%f")
    funding_requirements = st.text_area("Funding Requirements")

    st.header("Management Team")
    management_team = st.text_area("Key Personnel (name and roles)")

    st.header("Company Structure")
    company_structure=st.text_area("What is your organizational structure")

    st.header("Goals and Objectives")
    goals_objectives = st.text_area("Short-term and Long-term Goals")

    st.header("Operational Plan")
    operational_strategy = st.text_area("Basic Operational Strategy")

    st.header("Market Analysis")
    market_overview = st.text_area("Brief Market Overview (size, trends, etc.)")

    if st.button('Submit'):
        # Process the collected data
        data = {
            "company_name": company_name,
            "industry": industry,
            "location": location,
            "mission": mission,
            "vision": vision,
            "products_services": products_services,
            "target_market": target_market,
            "value_proposition": value_proposition,
            "current_revenue": current_revenue,
            "current_expenses": current_expenses,
            "funding_requirements": funding_requirements,
            "management_team": management_team,
            "goals_objectives": goals_objectives,
            "operational_strategy": operational_strategy,
            "market_overview": market_overview,
            "company_structure": company_structure,
            "promotional_strategy": promotional_strategy
        }
        st.write("Collected Information:", data)

        # Phase 3: Parallel section generation controls
        st.sidebar.header("Generation Settings")
        parallel_enabled = st.sidebar.checkbox("Generate sections in parallel (faster)", value=True)
        max_workers = st.sidebar.slider("Concurrent LLM calls", min_value=1, max_value=12, value=5)

        st.title("Business Proposal Generator")

        # Define section generators with keys
        section_generators = [
            ("executive_summary", generate_executive_summary),
            ("mission", generate_mission),
            ("vision", generate_vision),
            ("objectives", generate_objectives),
            ("core_values", generate_core_values),
            ("business_description", generate_business_description),
            ("company_location", generate_company_location),
            ("products", generate_products),
            ("ownership", generate_ownership),
            ("company_structure", generate_company_structure),
            ("management_profiles", generate_management_profiles),
            ("operational_strategy", generate_operational_strategy),
            ("marketing_mix", generate_marketing_mix),
            ("promotional_strategy", generate_promotional_strategy),
            ("demand_analysis", analyze_demand),
            ("market_segmentation", segment_market),
            ("competitor_analysis", analyze_competitors),
            ("porters_five_forces", perform_porters_five_forces),
            ("industry_accommodation", analyze_industry_accommodation),
            ("major_players", list_major_players),
            ("business_sub_sector", analyze_business_sub_sector),
            ("swot_analysis", generate_swot_analysis),
            ("funding_request", generate_funding_request),
            ("financing_plan", create_financing_plan),
            ("pro_forma_income_statement", generate_pro_forma_income_statement),
            ("revenue_expenses_predictions", predict_revenue_expenses),
            ("monthly_cash_flow", generate_monthly_cash_flow),
            ("pro_forma_annual_cash_flow", generate_pro_forma_annual_cash_flow),
            ("pro_forma_balance_sheet", generate_pro_forma_balance_sheet),
            ("break_even_analysis", perform_break_even_analysis),
            ("payback_period", calculate_payback_period),
            ("financial_graphs", generate_financial_graphs),
            ("risk_mitigations", identify_risks_mitigations),
        ]

        section_order = [key for key, _ in section_generators]

        # Generate sections (parallel or sequential fallback)
        if parallel_enabled:
            results_map = generate_all_sections_parallel(
                data,
                call_llm,
                section_generators,
                max_workers=max_workers
            )
        else:
            st.info("Generating sections sequentially...")
            results_map = {}
            progress_bar = st.progress(0)
            total_tasks = len(section_generators)
            for idx, (section_name, generator) in enumerate(section_generators, start=1):
                try:
                    prompt = generator(data)
                    results_map[section_name] = call_llm(prompt)
                    progress_bar.progress(idx / total_tasks)
                except Exception as e:
                    st.error(f"Error generating {section_name}: {e}")
                    results_map[section_name] = f"[Error generating {section_name}: {str(e)}]"
            progress_bar.empty()

        # Section headers mapping by key
        section_to_header = {
            "executive_summary": "Executive Summary",
            "mission": "Mission Statement",
            "vision": "Vision Statement",
            "objectives": "Objectives",
            "core_values": "Core Values",
            "business_description": "Business Description Analysis",
            "company_location": "Company Location",
            "products": "Products",
            "ownership": "Ownership",
            "company_structure": "Company Structure",
            "management_profiles": "Management Profiles",
            "operational_strategy": "Operational Strategy Analysis",
            "marketing_mix": "Marketing Mix Strategy",
            "promotional_strategy": "Promotional Strategy",
            "demand_analysis": "Demand Analysis",
            "market_segmentation": "Market Segment Analysis",
            "competitor_analysis": "Competitor Analysis",
            "porters_five_forces": "Porter's Five Forces Analysis",
            "industry_accommodation": "Industry Analysis",
            "major_players": "Major Players",
            "business_sub_sector": "Business Sub-Sector Analysis",
            "swot_analysis": "SWOT Analysis",
            "funding_request": "Funding Request",
            "financing_plan": "Financing & Bank Loan Amortization",
            "pro_forma_income_statement": "Pro Forma Income Statement",
            "revenue_expenses_predictions": "Revenue and Expenses Predictions",
            "monthly_cash_flow": "Monthly Cash Flow Statement",
            "pro_forma_annual_cash_flow": "Pro Forma Annual Cash Flow",
            "pro_forma_balance_sheet": "Pro Forma Balance Sheet",
            "break_even_analysis": "Break Even Analysis",
            "payback_period": "Payback Period Analysis",
            "financial_graphs": "Financial Graphs",
            "risk_mitigations": "Risk and Mitigatory Measures",
        }

        # Display all sections in order
        for key in section_order:
            st.subheader(section_to_header.get(key, key))
            st.write(results_map.get(key, f"[Missing: {key}]"))

        # Create a PDF object
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title
        pdf.cell(0, 10, txt="Business Proposal", ln=True, align="C")
        pdf.ln(10)

        # Populate PDF with sections by key
        for key in section_order:
            header_text = section_to_header.get(key, "Section")
            content_text = results_map.get(key, f"[Missing: {key}]")

            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, header_text, ln=True)

            pdf.set_font("Arial", size=12)
            content = strip_md(content_text)
            pdf.multi_cell(0, 10, content)
            pdf.ln(5)

        # Save PDF to BytesIO
        pdf_mem_file = io.BytesIO()
        pdf_mem_file.write(pdf.output(dest='S').encode('latin1'))
        pdf_mem_file.seek(0)

        # Create a Word document
        doc = docx.Document()
        doc.add_heading("Business Proposal", 0)

        # Add sections in order
        for key in section_order:
            header_text = section_to_header.get(key, "Section")
            content_text = results_map.get(key, f"[Missing: {key}]")

            doc.add_heading(header_text, 3)

            section_text = strip_md(content_text).replace("\\", "")
            p = doc.add_paragraph()
            process_markdown_to_runs(p, section_text)

            if "|" in section_text:
                add_markdown_table(doc, section_text)

        # Save the Word document to a BytesIO object
        mem_file = io.BytesIO()
        doc.save(mem_file)
        mem_file.seek(0)

        # Create download buttons
        st.download_button(
            "Download Business Proposal (PDF)",
            pdf_mem_file.getvalue(),
            "business_proposal.pdf",
            "application/pdf"
        )

        st.download_button(
            "Download Business Proposal (Word)",
            mem_file.getvalue(),
            "business_proposal.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

             
            

if __name__ == "__main__":
    collect_basic_info()
