import streamlit as st
import docx
import re
import tempfile
import pathlib
import os
import io
import fpdf
import time
import requests
from groq import Groq
from exa_py import Exa
from string import Template
from dotenv import load_dotenv
from retrying import retry
from funtions import *
from fpdf import FPDF
fpdf.set_global("UTF8", True)


# Load environment variables from .env file
load_dotenv()

#declare the exa search api
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

# Define your API Model and key (replace 'your-api-key' with the actual key)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
utilized_model = "llama3-70b-8192"

#the file path that contains the prompt
file_path = os.path.join(os.getcwd(), "plugins/modular_business_proposal")

#Functions for the Exa Search content & Parameters for our Highlights search
highlights_options = {
    "num_sentences": 7,  # how long our highlights should be
    "highlights_per_url": 1,  # just get the best highlight for each URL
}

@retry(wait_fixed=3100, stop_max_attempt_number=6)
def call_llm(prompt):
    proposal_parts = []
    search_response = exa.search_and_contents(query=prompt, highlights=highlights_options, num_results=3, use_autoprompt=True)
    info = [sr.highlights[0] for sr in search_response.results]

    system_prompt = "You are a Business proposal generator. Read the provided contexts and, if relevant, use them to answer the user's question."
    user_prompt = f"Sources: {info}\nQuestion: {prompt}"

    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
    data = {
        "model": utilized_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    }

    response = requests.post("https://api.groq.com/chat/completions", headers=headers, json=data)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 3))  # Default to 3 seconds if header is missing
        time.sleep(retry_after)

    response_json = response.json()
    response_text = f"Answer: {response_json['choices'][0]['message']['content']}\n\n"
    proposal_parts.append(response_text)

    proposal_text = "\n\n".join(proposal_parts)
    return proposal_text

# Function to strip markdown and unescape characters
def strip_md(text):
    text = text.replace("**", "")  # remove bold syntax
    text = text.replace("*", "")  # remove italic syntax
    text = text.replace("#", "")  # remove headings
    text = re.sub(r'([!*_=~-])', r'\\\1', text)
    return text


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
            "company_structure":company_structure,
            "promotional_strategy":promotional_strategy
        }
        st.write("Collected Information:", data)
        # Further processing can be done here (e.g., calling AI to generate the business proposal)

        
        st.title("Business Proposal Generator")

        #output=call_llm(data)
        #st.write(output)
        # Generate and display executive summary
        exec_summary_prompt = generate_executive_summary(data)
        executive_summary = call_llm(exec_summary_prompt)
        st.subheader("Executive Summary")
        st.write(executive_summary)
        
        

        #2. Mission, Objectives, and Keys to Success

        #Mission Statement:
 
        mission_prompt =generate_mission(data)
        mission_analysis = call_llm(mission_prompt)
        st.subheader("Mission Statement")
        st.write(mission_analysis)

        #Vision Statement:
        vision_statement_prompt = generate_vision(data)
        vision_analysis = call_llm(vision_statement_prompt)
        st.subheader("Vision Statement:")
        st.write(vision_analysis)

        #Objectives
        objectives_prompt= generate_objectives(data)
        objectives_analysis = call_llm(objectives_prompt)
        st.subheader("Objectives")
        st.write(objectives_analysis)

        #Core Values:
        core_values_prompt = generate_core_values(data)
        core_values_analysis = call_llm(core_values_prompt)
        st.subheader("Core Values:")
        st.write(core_values_analysis)

        #3. Company Summary
        #Business Description
        business_description_prompt = generate_business_description(data)
        business_description_analysis = call_llm(business_description_prompt)
        st.subheader("Business Descrtiption Analysis")
        st.write(business_description_analysis)

        #Company Location:

        company_location_prompt = generate_company_location(data)
        company_location_analysis = call_llm(company_location_prompt)
        st.subheader("Company location")
        st.write(company_location_analysis)

        #Products:
        products_prompt = generate_products(data)
        products_analysis = call_llm(products_prompt)
        st.subheader("Products")
        st.write(products_analysis)

        #Ownership:
        ownership_prompt = generate_ownership(data)
        owner_analysis = call_llm(ownership_prompt)
        st.subheader("Ownership")
        st.write(owner_analysis)

        #Company Structure:
        company_structure_prompt = generate_company_structure(data)
        company_structure_analysis = call_llm(company_structure_prompt)
        st.subheader("Company Structure")
        st.write(company_structure_analysis)

        #Management Profiles:
        management_profile_prompt = generate_management_profiles(data)
        management_profile_analysis = call_llm(management_profile_prompt)
        st.subheader("Management Profiles")
        st.write(management_profile_analysis)

        #4. Operational Strategy
        operational_strategy_prompt = generate_operational_strategy(data)
        operational_strategy_analysis = call_llm(operational_strategy_prompt)
        st.subheader("Operational Strategy Analysis")
        st.write(operational_strategy_analysis)

        #5. Marketing Strategy
        #Marketing Mix:
        marketing_prompt = generate_marketing_mix(data)
        marketing_analysis = call_llm(marketing_prompt)
        st.subheader("Marketing Mix Strategy")
        st.write(marketing_analysis)
        

        #Promotional Strategy:
        promotional_prompt = generate_promotional_strategy(data)
        promotional_analysis = call_llm(promotional_prompt)
        st.subheader("Promotional Strategy")
        st.write(promotional_analysis)

        #6. Market Analysis
        #Demand Analysis:
        analyze_demand_prompt = analyze_demand(data)
        analyze_demand_analysis = call_llm(analyze_demand_prompt)
        st.subheader("Demand Analysis")
        st.write(analyze_demand_analysis)

        #Market Segmentation:
        segment_market_prompt = segment_market(data)
        segment_market_analysis = call_llm(segment_market_prompt)
        st.subheader("Market Segment Analysis")
        st.write(segment_market_analysis)

        #Competitor Analysis:
        competitor_analysis_prompt = analyze_competitors(data)
        competitor_analysis = call_llm(competitor_analysis_prompt)
        st.subheader("Competitor Analysis")
        st.write(competitor_analysis)

        #Porter's Five Forces:
        porters_prompt =perform_porters_five_forces(data)
        porters_analysis = call_llm(porters_prompt)
        st.subheader("Porter's Five Forces Analysis")
        st.write(porters_analysis)

        #7. Industry Analysis
        #Industry Accommodation:
        st.subheader("Industry Analysis")
        industry_accommodation_prompt = analyze_industry_accommodation(data)
        industry_accommodation_analysis = call_llm(industry_accommodation_prompt)
        st.write(industry_accommodation_analysis)
        #Major Players:
        st.subheader("Major Players")
        list_major_players_prompt = list_major_players(data)
        list_major_players_analysis = call_llm(list_major_players_prompt)
        st.write(list_major_players_analysis)

        #Business Sub-Sector in Lesotho:
        st.subheader("Business Sub-Sector Analysis")
        business_sub_sector_analysis_prompt = analyze_business_sub_sector(data)
        business_sub_sector_analysis = call_llm(business_sub_sector_analysis_prompt)
        st.write(business_sub_sector_analysis)

        #8. SWOT Analysis
        # Generate and display SWOT analysis
        swot_prompt = generate_swot_analysis(data)
        swot_analysis = call_llm(swot_prompt)
        st.subheader("SWOT Analysis")
        st.write(swot_analysis)

        #9Financial Statements
        #Funding Request:
        st.subheader("Funding Request")
        funding_request_prompt = generate_funding_request(data)
        funding_request_analysis = call_llm(funding_request_prompt)
        st.write(funding_request_analysis)

        #Financing & Bank Loan Amortization:
        st.subheader("Financing & Bank Loan Amortization")
        financing_plan_prompt = create_financing_plan(data)
        financing_plan_analysis = call_llm(financing_plan_prompt)
        st.write(financing_plan_analysis)

        #Pro Forma Income Statement:
        st.subheader("Pro Forma Income Statement")
        pro_forma_income_statement_prompt = generate_pro_forma_income_statement(data)
        pro_forma_income_statement_analysis = call_llm(pro_forma_income_statement_prompt)
        st.write(pro_forma_income_statement_analysis)

        #10. Assumptions/Predictions
        #Revenue and Expenses Predictions:
        st.subheader("Revenue and Expenses Predictions")
        predict_revenue_expenses_prompt = predict_revenue_expenses(data)
        predict_revenue_expenses_analysis = call_llm(predict_revenue_expenses_prompt)
        st.write(predict_revenue_expenses_analysis)

        #Monthly Cash Flow Statement:
        st.subheader("Monthly Cash Flow Statement")
        monthly_cash_flow_prompt = generate_monthly_cash_flow(data)
        monthly_cash_flow_analysis = call_llm(monthly_cash_flow_prompt)
        st.write(monthly_cash_flow_analysis)

        #Pro Forma Annual Cash Flow:
        st.subheader("Pro Forma Annual Cash Flow")
        pro_forma_annual_cash_flow_prompt = generate_pro_forma_annual_cash_flow(data)
        pro_forma_annual_cash_flow_analysis = call_llm(pro_forma_annual_cash_flow_prompt)
        st.write(pro_forma_annual_cash_flow_analysis)

        #Pro Forma Balance Sheet:
        st.subheader("Pro Forma Balance Sheet")
        pro_forma_balance_sheet_prompt = generate_pro_forma_balance_sheet(data)
        pro_forma_balance_sheet_analysis = call_llm(pro_forma_balance_sheet_prompt)
        st.write(pro_forma_balance_sheet_analysis)

        #Break Even Analysis:
        st.subheader("Break Even Analysis")
        break_even_analysis_prompt = perform_break_even_analysis(data)
        break_even_analysis = call_llm(break_even_analysis_prompt)
        st.write(break_even_analysis)

        #Payback Period Analysis:
        payback_period_prompt = calculate_payback_period(data)
        payback_period_analysis = call_llm(payback_period_prompt)
        st.subheader("Payback Period Analysis")
        st.write(payback_period_analysis)

        #Financial Graphs:
        financial_graphs_prompt = generate_financial_graphs(data)
        financial_graphs_analysis = call_llm(financial_graphs_prompt)
        st.subheader("Financial Graphs")
        st.write(financial_graphs_analysis)

        #11. Risk and Mitigatory Measures
        risk_mitigations_prompt = identify_risks_mitigations(data)
        risk_mitigations_analysis = call_llm(risk_mitigations_prompt)
        st.subheader("Risk and Mitigatory Measures")
        st.write(risk_mitigations_analysis)

        # Create a PDF object
        pdf = FPDF()

        # Add a page
        pdf.add_page()

        # Set font
        pdf.set_font("Arial", size=12)

        # Add title
        pdf.cell(0, 10, txt="Business Proposal", ln=True, align="C")
        pdf.ln(10)

        # Add sections
        sections = [
            executive_summary,
            mission_analysis,
            vision_analysis,
            objectives_analysis,
            core_values_analysis,
            business_description_analysis,
            company_location_analysis,
            products_analysis,
            owner_analysis,
            company_structure_analysis,
            management_profile_analysis,
            operational_strategy_analysis,
            marketing_analysis,
            promotional_analysis,
            analyze_demand_analysis,
            segment_market_analysis,
            competitor_analysis,
            porters_analysis,
            industry_accommodation_analysis,
            list_major_players_analysis,
            business_sub_sector_analysis,
            swot_analysis,

            funding_request_analysis,
            financing_plan_analysis,
            pro_forma_income_statement_analysis,
            predict_revenue_expenses_analysis,
            monthly_cash_flow_analysis,
            pro_forma_annual_cash_flow_analysis,
            pro_forma_balance_sheet_analysis,
            break_even_analysis,
            payback_period_analysis,
            financial_graphs_analysis,
            risk_mitigations_analysis
        ]
        #Section Subheader title
        section_headers = {
            "executive_summary":"Executive Summary",
            "mission_analysis":"Mission Statement",
            "vision_analysis":"Vision Statement",
            "objectives_analysis":"Objectives",
            "core_values_analysis":"Core values",
            "business_description_analysis":"Business Description Analysis",
            "company_location_analysis":"Company Location",
            "products_analysis":"Products",
            "owner_analysis":"Ownership",
            "company_structure_analysis":"Company Structure",
            "management_profile_analysis":"Management Profiles",
            "operational_strategy_analysis":"Operational Strategy",
            "marketing_analysis":"Marketing Mix Strategy",
            "promotional_analysis":"Promotional Strategy",
            "analyze_demand_analysis":"Market Demand Analysis",
            "segment_market_analysis":"Market Segment Analysis",
            "competitor_analysis":"Competitors Analysi",
            "porters_analysis":"Porter's Five Forces Analysis",
            "industry_accommodation_analysis":"Industry Analysis",
            "list_major_players_analysis":"Major Player Analysis",
            "business_sub_sector_analysis": "Business Sub Sector Analysis",
            "swot_analysis":"Swot Analysis",
            "funding_request_analysis":"Funding Request",
            "financing_plan_analysis":"Financing & Bank Loan Amortization",         
            "pro_forma_income_statement_analysis":"Income Statement Analysis",
            "predict_revenue_expenses_analysis":"Revenue Expense Analysis",
            "monthly_cash_flow_analysis":"Montly Cash Flow Analysis",
            "pro_forma_annual_cash_flow_analysis": "Pro Forma Annual Cash Flow Analysis",
            "pro_forma_balance_sheet_analysis": "Pro Forma Balance Sheet Analysis",
            "break_even_analysis": "Break-Even Analysis",
            "payback_period_analysis": "Payback Period Analysis",
            "financial_graphs_analysis": "Financial Graphs Analysis",
            "risk_mitigations_analysis": "Risk Mitigations Analysis"
        }


        

        # Create a Word document
        doc = docx.Document()

        # Add title
        doc.add_heading("Business Proposal", 0)

        # Add sections
        for section in sections:
            header_text = ""  # Initialize an empty string
            for key, value in section_headers.items():
                if section == eval(key):  # Match variable names from sections list with keys of section_headers dictionary
                    header_text = value  # Assign the value of the key to header_text
                    break
    


            # Add a Heading 3 for the subheader
            doc.add_heading(header_text, 3)

            # Remove Markdown formatting
            section = strip_md(section)
            section = section.replace("\\", "")  # Remove backslashes

            p = doc.add_paragraph("")

            # Check if the section contains bold or italic text
            parts = section.split("**")
            p = doc.add_paragraph("")
            for part in parts:
                if part:
                    if parts.index(part) % 2 == 1:
                        # Add bold text
                        p.add_run(part).bold = True
                    else:
                        # Add non-bold text
                        p.add_run(part)

            # Check if the section contains headings
            if "#" in section:
                heading_parts = section.split("#")
                for part in heading_parts:
                    if part:
                        level = heading_parts.index(part) + 1
                        doc.add_heading(part, level)

                        

            # Check if the section contains tables
            if "|" in section:
                # Split the text into table rows
                rows = section.split("\n")
                table = doc.add_table(rows=1, cols=len(rows[0].split("|")))
                # Initialize your table
                table = doc.tables[0]  # Assuming you have a Word document with tables

                num_rows = len(table.rows)
                num_cols = len(table.columns)
                for row_idx in range(num_rows):
                    for col_idx in range(num_cols):
                        cell = section.split("\n")[row_idx].split("|")[col_idx]
                        table.cell(row_idx, col_idx).text = cell

        # Save the Word document to a BytesIO object
        mem_file = io.BytesIO()
        doc.save(mem_file)
        mem_file.seek(0)

        # Create a download button
        st.download_button("Download Business Proposal (Word)", mem_file.getvalue(), "business_proposal.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

             
            

if __name__ == "__main__":
    collect_basic_info()
