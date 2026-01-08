# 🧠 Python Based GenAI Career Assistant Multi-Agent (All Free Open source)

## 📋 Project Overview
An AI-powered mentor simplifies and supports your journey in Generative AI learning resume preparation interview assistance and job hunting.
<img src="docs/multiagent.png" alt="GenAI Career Assistant Architecture" width="500">

## 💡 Features
1. **Learning & Content Creation:**
   - Offers tailored learning pathways in GenAI, covering key topics and skills.
   - Assists users in creating tutorials, blogs, and posts based on their interests or queries.
2. **Q&A Support:**
   - Provides on-demand Q&A sessions for users needing guidance on concepts or coding issues.
3. **Resume/CV Building & Analysis:**
   - Generate cover letters tailored to specific job applications.
   - Extract and analyze key information from your resume to optimize job matches
   - Crafts personalized, market-relevant resumes optimized for current job trends.
4. **Interview Preparation:**
   - Hosts Q&A sessions on common and technical interview questions.
   - Simulates real interview scenarios and conducts mock interviews.
   - Gather and present key information about potential employers.
5. **Job Search Assistance:**
   - Guides users through the job search process, offering tailored insights and support.

## 📄 Architecture Overview

The GenAI Career Assistant is built on a Supervisor Multi-Agent Architecture. Here's how it works:

- **Supervisor:** Manages the overall workflow, deciding which agent to invoke next.
- **JobSearcher:** Handles job search queries and retrieves relevant listings.
- **ResumeAnalyzer:** Extracts and analyzes information from uploaded resumes.
- **CoverLetterGenerator:** Crafts customized cover letters based on resume and job details.
- **WebResearcher:** Performs web searches to gather relevant company information.
- **ChatBot:** Manages general queries and provides conversational responses.

##  🔧  Key Components

- **Agent Creation and Configuration:** A common function is used to set up agents with specific tools and prompts.
- **State Management**: Using TypedDict to define and manage the state of each customer interaction.
- **Query Categorization**: Classifying users queries into Learning, Resume Preparation, Interview or Job Search.
- **Sub Categorization**: Learning(Tutorial, Q&A), Interview(Interview prep,Mock interview).
- **Specialized Tools:** Custom tools enhance the agents' capabilities, such as job search tools, resume extractors, and web search tools.
- **Response Generation**: Creating appropriate responses based on the query category. Create .md files for Tutorial Blogs, Resume, Mock interview etc.
- **Streamlit UI:** The user interface is designed to be intuitive and responsive, facilitating interaction with the assistant.

##  🔧 Technologies Used

- **LangGraph:** For creating and managing multi-agent workflows.
- **Streamlit:** For building the user interface.
- **OpenAI API:** For leveraging large language models (LLMs).
- **SerperClient and FireCrawlClient:** For web search and scraping capabilities.

## 🧭 Requirements 

1. This project uses Python 3.12 (Python version should be higher than 3.11 but lower than 3.14). 

   ```
   python3 --version
   ```
   Create a virtual env with the following command:
   Using Conda :
   ```
   conda create --name genaiagent-setup python=3.12
   conda activate genaiagent-setup
   ```
   Mac/Linux/WSL (Using venv)

   ```
   $ python3 -m venv genaiagent-setup
   $ source genaiagent-setup/bin/activate
   $ python3 -m pip install --upgrade pip
   ```


2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   Setting up env variables
   Mac/Linux/WSL
   ```bash
   $ export API_ENV_VAR="your-api-key-here"
   ```

3. Running notebooks: Since I am using a virtualenv, when I run the command `jupyter lab` it might or might not use the virtualenv. 
   ```bash
   $ brew install jupyterlab
   $ jupyter notebook
   ```
   To make sure to use the virutalenv, run the following commands before running `jupyter lab`

   ```
   conda install ipykernel
   python -m ipykernel install --user --name genaiagent-setup
   pip install ipywidgets
   ```
4. Sign up for LangSmith: 

      Create a LangSmith account and API key. You can reference LangSmith docs.
      Then, set

      ```bash
      LANGSMITH_API_KEY="your-key"
      LANGSMITH_TRACING_V2=true
      LANGSMITH_PROJECT="langchain-academy"
      # If you are on the EU instance:
      LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
      ```
      in your environment
5. Set up environment variables by creating a `.streamlit/secrets.toml` file:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   LANGCHAIN_API_KEY = "" # if you want to trace using langsmith"
   LANGCHAIN_TRACING_V2 = "true"
   LANGCHAIN_PROJECT = "JOB_SEARCH_AGENT"
   GROQ_API_KEY = "API key of groq"
   SERPER_API_KEY = "serper API key"
   FIRECRAWL_API_KEY = "firecrawl API key"
   LINKEDIN_JOB_SEARCH = "linkedin_api" # only if you want to use python linkedin-api package
   LINKEDIN_EMAIL = "" # if you have enabled linkedin job search then both password and email are mandatory.
   LINKEDIN_PASS = ""
   ```

6. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 📁 Core Files

- `requirements.txt` – Package dependencies  
- `README.md` – Project overview and usage  
- `Dockerfile` – Container build instructions 

## 🧭 Usage

1. **Upload Your Resume:** Start by uploading your resume in PDF format.
2. **Enter Your Query:** Use the chat interface to ask questions or request specific tasks (e.g., "Find jobs in data science").
3. **Interact with the Assistant:** The assistant will guide you through job searches, resume analysis, and cover letter generation.
4. **Download Results:** Save the generated cover letters or other documents as needed.

## ⚡ Best Practices

- Track prompt versions and results  
- Separate configs using YAML files  
- Structure code by clear module boundaries  
- Cache responses to reduce latency and cost  
- Handle errors with custom exceptions  
- Use notebooks for rapid testing and iteration  
- Monitor API usage and set rate limits  
- Keep code and docs in sync