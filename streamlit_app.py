import streamlit as st
import pandas as pd
import requests
import openai
from datetime import datetime

# Set Streamlit page configuration
st.set_page_config(page_title="Job Search App", layout="wide")

# App title
st.title("🔍 Job Search App")

# Input fields
st.sidebar.header("Search Parameters")
job_title = st.sidebar.text_input("Job Title", value="Product Manager")
job_site = st.sidebar.selectbox(
    "Select Job Site",
    ["icims.com", "greenhouse.io", "lever.co", "indeed.com"]
)
date_filter = st.sidebar.date_input(
    "Posted After",
    value=datetime.today()
)

st.sidebar.header("Resume and API Key")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Your OpenAI API key is required to extract and compare keywords."
)
resume_text = st.sidebar.text_area(
    "Paste Your Resume Text",
    height=300,
    help="Paste the full text of your resume here."
)

# Search button
search_button = st.sidebar.button("Search Jobs")

def setup_openai(api_key):
    openai.api_key = api_key

def fetch_jobs(job_title, job_site, date_filter):
    """
    Fetch job listings based on job title, site, and date filter.
    For demonstration, this function returns mocked data.
    """
    # TODO: Integrate with real job search APIs or implement web scraping here.
    
    # Mocked job data
    job_data = [
        {
            "job_name": "Product Manager",
            "company_name": "TechCorp",
            "date_posted": "2024-08-20",
            "job_link": "https://www.techcorp.com/jobs/123",
            "job_description": "We are looking for an experienced Product Manager with skills in agile methodologies, user research, and data analysis."
        },
        {
            "job_name": "Senior Product Manager",
            "company_name": "InnovateX",
            "date_posted": "2024-08-18",
            "job_link": "https://www.innovatex.com/careers/456",
            "job_description": "Join InnovateX as a Senior Product Manager. Required skills include strategic planning, stakeholder management, and market analysis."
        },
        # Add more mocked jobs as needed
    ]
    
    # Convert to DataFrame
    jobs_df = pd.DataFrame(job_data)
    
    # Filter jobs by date
    jobs_df['date_posted'] = pd.to_datetime(jobs_df['date_posted'])
    filtered_jobs = jobs_df[jobs_df['date_posted'] >= pd.to_datetime(date_filter)]
    
    return filtered_jobs.reset_index(drop=True)

import openai

# Assuming you're using openai.ChatCompletion
def extract_keywords(api_key, resume_text, job_description):
    openai.api_key = api_key

    prompt = f"Extract relevant keywords from the following job description:\n\n{job_description}\n\nThen compare them with the following resume text:\n\n{resume_text}\n\nProvide matched and missing keywords."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']



keywords_result = extract_keywords(api_key, resume_text, job_description)
print(keywords_result)


def compare_keywords(job_keywords, resume_keywords):
    """
    Compares job description keywords with resume keywords.
    Returns matched and missing keywords.
    """
    matched_keywords = list(set(job_keywords) & set(resume_keywords))
    missing_keywords = list(set(job_keywords) - set(resume_keywords))
    return matched_keywords, missing_keywords

def process_and_display_jobs(jobs_df, resume_text):
    """
    Processes each job listing to extract and compare keywords,
    then displays the results in a table.
    """
    resume_keywords = extract_keywords(resume_text)
    
    if not resume_keywords:
        st.error("Could not extract keywords from resume. Please check your resume text and API key.")
        return
    
    results = []
    
    for index, row in jobs_df.iterrows():
        job_description = row['job_description']
        job_keywords = extract_keywords(job_description)
        
        matched_keywords, missing_keywords = compare_keywords(job_keywords, resume_keywords)
        
        results.append({
            "Job Name": row['job_name'],
            "Company Name": row['company_name'],
            "Date Posted": row['date_posted'].strftime("%Y-%m-%d"),
            "Job Link": row['job_link'],
            "Matched Keywords": ", ".join(matched_keywords),
            "Missing Keywords": ", ".join(missing_keywords)
        })
    
    results_df = pd.DataFrame(results)
    
    # Display the results
    st.subheader("Job Search Results")
    st.dataframe(results_df)

if search_button:
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
    elif not resume_text.strip():
        st.error("Please enter your resume text.")
    else:
        with st.spinner("Processing..."):
            setup_openai(openai_api_key)
            jobs_df = fetch_jobs(job_title, job_site, date_filter)
            if jobs_df.empty:
                st.warning("No jobs found matching your criteria.")
            else:
                process_and_display_jobs(jobs_df, resume_text)
