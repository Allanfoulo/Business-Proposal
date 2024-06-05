# 1. Executive Summary
def generate_executive_summary(data):
    prompt = f"""
    Generate an executive summary for a business plan. The company, {data['company_name']}, operates in the {data['industry']} industry and is located in {data['location']}. The mission of the company is {data['mission']}, and its vision is {data['vision']}. The company offers {data['products_services']} and targets {data['target_market']}. Its unique value proposition is {data['value_proposition']}. Currently, the company has a revenue of {data['current_revenue']} and expenses of {data['current_expenses']}. The company seeks funding of {data['funding_requirements']}. The management team includes {data['management_team']}. The main goals and objectives of the company are {data['goals_objectives']}.
    """
    return prompt

#2. Mission, Objectives, and Keys to Success
#Mission Statement:

def generate_mission(data):
    prompt = f"""
    You will be provided with information about a company. Use this information to craft a clear and inspiring mission statement.

    Company Information:

    Company Name: {data['company_name']}
    Industry: {data['industry']}
    Mission: {data['mission']}
    Task:

    Write a concise and compelling mission statement that captures the essence of the company's purpose and values. The mission statement should be inspiring, yet realistic, and reflect the company's role in the {data['industry']} industry.

    Evaluation Criteria:

    Your mission statement will be evaluated based on its clarity, coherence, and ability to inspire and motivate. The statement should be concise, yet meaningful, and should reflect the company's values and purpose.

    Please generate a mission statement that incorporates the provided company information and meets the evaluation criteria."""
    return prompt

#Vision Statement:
def generate_vision(data):
    prompt = f"""
        Create a Compelling Mission Statement
        You will be provided with information about a company. Use this information to craft a clear and inspiring mission statement.

        Company Information:

        Company Name: {data['company_name']}
        Industry: {data['industry']}
        Vision: {data['vision']}
        Task:

        Write a concise and compelling mission statement that captures the essence of the company's purpose and values. The mission statement should be inspiring, yet realistic, and reflect the company's role in the {data['industry']} industry.

        Evaluation Criteria:

        Your mission statement will be evaluated based on its clarity, coherence, and ability to inspire and motivate. The statement should be concise, yet meaningful, and should reflect the company's values and purpose.

        Example Output:

        A sample mission statement for a company in the technology industry might be: "Empowering innovative solutions, [Company Name] strives to bridge the gap between technology and humanity, fostering a future where people and technology thrive together."

        Your Turn:

        Please generate a mission statement that incorporates the provided company information and meets the evaluation criteria. and only output the request not your reseaon as to why"""
    return prompt

#Objectives
def generate_objectives(data):
    prompt = f"""
    List the main objectives for a company named {data['company_name']}. The company aims to achieve the following goals in the short-term and long-term: {data['goals_objectives']}, expand on the context provided before. do not generate a business proposal just expand on the objectives.
    """
    return prompt

#Core Values:

def generate_core_values(data):
    prompt = f"""
    Generate a list of core values for a company named {data['company_name']}, operating in the {data['industry']} industry. Please provide 3-5 concise values that reflect the company's mission which is  {data['mission']}, vision which is  {data['vision']}, and culture, such as 'innovation', 'sustainability', or 'customer-centricity'.
    """
    return prompt

#Keys to Success:
def generate_keys_to_success(data):
    prompt = f"""
   Identify the keys to success for a company named {data['company_name']}, operating in the {data['industry']} industry. Consider factors such as market trends, competitive advantage, and operational efficiency. Please provide 3-5 key factors that are crucial for the company's success.
    """
    return prompt

#3. Company Summary
#Business Description
def generate_business_description(data):
    prompt = f"""
    Provide a detailed business description for {data['company_name']}, which operates in the {data['industry']} industry. The company is located in {data['location']} and offers {data['products_services']}. Describe the overall business model and core activities.
    """
    return prompt

#Company Location:
def generate_company_location(data):
    prompt = f"""
    Describe the location of {data['company_name']}. The company is based in {data['location']}. Provide details about the advantages of this location for the business, if you can't find the company online assume it's a small unknown startup, just utilize the location.
    """
    return prompt

#Products:
def generate_products(data):
    prompt = f"""
    Describe the products or services offered by {data['company_name']}. The company operates in the {data['industry']} industry and provides the following products/services: {data['products_services']}.
    """
    return prompt

#Ownership:
def generate_ownership(data):
    prompt = f"""
    Provide details about the ownership structure of {data['company_name']}, a company operating in the {data['industry']} industry and located in {data['location']}. The company is owned and managed by the following individuals: {data['management_team']}. Describe their roles and contributions to the company.
    """
    return prompt


#Company Structure:
def generate_company_structure(data):
    prompt = f"""
    Describe the company structure of {data['company_name']}, Company Structure - {data['company_structure']} . Include information about the organizational hierarchy and the key departments.
    """
    return prompt

#Management Profiles:
def generate_management_profiles(data):
    prompt = f"""
    Provide detailed management profiles for the key personnel of {data['company_name']}. Include their names, roles, and brief backgrounds: {data['management_team']}.
    """
    return prompt

#4. Operational Strategy
def generate_operational_strategy(data):
    prompt = f"""
    Outline the operational strategy for {data['company_name']}. The company operates in the {data['industry']} industry and plans to achieve its goals through the following operational strategies: {data['operational_strategy']}.
    """
    return prompt

#5. Marketing Strategy
#Marketing Mix:

def generate_marketing_mix(data):
    prompt = f"""
    Develop a marketing mix strategy for {data['company_name']}. The company targets {data['target_market']} and offers {data['products_services']}. Describe the strategies for product, price, place, and promotion.
    """
    return prompt


#Promotional Strategy:

def generate_promotional_strategy(data):
    prompt = f"""
    Create a promotional strategy for {data['company_name']}. The company operates in the {data['industry']} industry and aims to reach {data['target_market']} through the following promotional activities: {data['promotional_strategy']} and {data['value_proposition']}.
    """
    return prompt

#6. Market Analysis
#Demand Analysis:
def analyze_demand(data):
    prompt = f"""
    Analyze the market demand for the products/services offered by {data['company_name']}. The company operates in the {data['industry']} industry and targets {data['target_market']}. Provide insights into the demand trends and potential growth.
    """
    return prompt

#Market Segmentation:
def segment_market(data):
    prompt = f"""
    Segment the market for {data['company_name']}. The company targets {data['target_market']} and offers {data['products_services']}. Provide detailed market segments based on demographics, geography, behavior, and other relevant factors.
    """
    return prompt

#Competitor Analysis:
def analyze_competitors(data):
    prompt = f"""
    Conduct a competitor analysis for {data['company_name']}. The company operates in the {data['industry']} industry. Identify and analyze the main competitors, their strengths, weaknesses, and market positions.
    """
    return prompt

#Porter's Five Forces:
def perform_porters_five_forces(data):
    prompt = f"""
    Perform a Porter's Five Forces analysis for {data['company_name']}. The company operates in the {data['industry']} industry. Analyze the competitive forces including threat of new entrants, bargaining power of suppliers, bargaining power of buyers, threat of substitutes, and industry rivalry.
    """
    return prompt

#7. Industry Analysis
#Industry Accommodation:
def analyze_industry_accommodation(data):
    prompt = f"""
    Analyze whether the industry accommodates new businesses like {data['company_name']}. The company operates in the {data['industry']} industry and is located in {data['location']}. Discuss the industry's receptiveness to new entrants and the challenges faced.
    """
    return prompt

#Major Players:
def list_major_players(data):
    prompt = f"""
    List and describe the major players in the {data['industry']} industry where {data['company_name']} operates. Include details about their market share, strengths, and weaknesses.
    """
    return prompt

#Business Sub-Sector in Lesotho:
def analyze_business_sub_sector(data):
    prompt = f"""
     Analyze the business sub-sector in this provided location's ({data['location']}) country for {data['company_name']}. The company operates in the {data['industry']} industry. Provide insights into the sub-sector's growth, opportunities, and challenges.
    """
    return prompt

#8. SWOT Analysis
def generate_swot_analysis(data):
    prompt = f"""
    Perform a SWOT analysis for {data['company_name']}. The company operates in the {data['industry']} industry and is located in {data['location']}. Identify the strengths, weaknesses, opportunities, and threats based on the following information: 
    Strengths: Mission - {data['mission']}, Vision - {data['vision']}, Products/Services - {data['products_services']}, Value Proposition - {data['value_proposition']}, Management Team - {data['management_team']}, Current Revenue - {data['current_revenue']}.
    Weaknesses: Current Expenses - {data['current_expenses']}, Management Team - {data['management_team']}, Company Structure - {data['company_structure']}.
    Opportunities: Industry - {data['industry']}, Target Market - {data['target_market']}, Funding Requirements - {data['funding_requirements']}.
    Threats: Industry - {data['industry']}, Location - {data['location']}, Funding Requirements - {data['funding_requirements']}.
    
    """
    return prompt

#9Financial Statements
#Funding Request:

def generate_funding_request(data):
    prompt = f"""
    Create a funding request for {data['company_name']}. The company seeks funding of {data['funding_requirements']} to achieve its goals in the {data['industry']} industry.
    """
    return prompt

#Financing & Bank Loan Amortization:
def create_financing_plan(data):
    prompt = f"""
    Develop a financing plan and bank loan amortization schedule for {data['company_name']}. The company has current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}. It seeks funding of {data['funding_requirements']}.
    """
    return prompt

#Pro Forma Income Statement:
def generate_pro_forma_income_statement(data):
    prompt = f"""
    Generate a pro forma income statement for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}. Take note the currency for the income statement is from the country of this locations: ({data['location']}).
    """
    return prompt

#10. Assumptions/Predictions
#Revenue and Expenses Predictions:
def predict_revenue_expenses(data):
    prompt = f"""
    Predict the future revenue and expenses for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}.
    """
    return prompt

#Monthly Cash Flow Statement:
def generate_monthly_cash_flow(data):
    prompt = f"""
    Create a monthly cash flow statement for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}.
    """
    return prompt

#Pro Forma Annual Cash Flow:
def generate_pro_forma_annual_cash_flow(data):
    prompt = f"""
    Generate a pro forma annual cash flow statement for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}.
    """
    return prompt

#Pro Forma Balance Sheet:
def generate_pro_forma_balance_sheet(data):
    prompt = f"""
    Create a pro forma balance sheet for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}.
    """
    return prompt

#Break Even Analysis:
def perform_break_even_analysis(data):
    prompt = f"""
    Perform a break-even analysis for {data['company_name']}. The company operates in the {data['industry']} industry with current revenue of {data['current_revenue']} and expenses of {data['current_expenses']}.
    """
    return prompt

#Payback Period Analysis:
def calculate_payback_period(data):
    prompt = f"""
    Calculate the payback period for {data['company_name']}. The company seeks funding of {data['funding_requirements']} and operates in the {data['industry']} industry.
    """
    return prompt

#Financial Graphs:
def generate_financial_graphs(data):
    prompt = f"""
    Generate financial graphs for {data['company_name']} based on the current revenue of {data['current_revenue']}, expenses of {data['current_expenses']}, and funding requirements of {data['funding_requirements']}.
    """
    return prompt

#11. Risk and Mitigatory Measures
def identify_risks_mitigations(data):
    prompt = f"""
    Identify potential risks for {data['company_name']} and suggest mitigatory measures. The company operates in the {data['industry']} industry and is located in {data['location']}. Consider financial, operational, market, and industry-specific risks.
    """
    return prompt



