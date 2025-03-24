# Based on: https://github.com/tonykipkemboi/crewai-streamlit-demo
import streamlit as st
import sys
from contextlib import contextmanager
from io import StringIO
import re
import streamlit as st
from textwrap import dedent
from crewai import Agent, Task, Crew, Process, LLM
import dotenv

dotenv.load_dotenv()

#--------------------------------#
#         Output Handler         #
#--------------------------------#
class StreamlitProcessOutput:
    def __init__(self, container):
        self.container = container
        self.output_text = ""
        self.seen_lines = set()
        
    def clean_text(self, text):
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        
        # Remove LiteLLM debug messages
        if text.strip().startswith('LiteLLM.Info:') or text.strip().startswith('Provider List:'):
            return None
            
        # Clean up the formatting
        text = text.replace('[1m', '').replace('[95m', '').replace('[92m', '').replace('[00m', '')
        return text
        
    def write(self, text):
        cleaned_text = self.clean_text(text)
        if cleaned_text is None:
            return
            
        # Split into lines and process each line
        lines = cleaned_text.split('\n')
        new_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in self.seen_lines:
                self.seen_lines.add(line)
                new_lines.append(line)
        
        if new_lines:
            # Add the new lines to the output
            new_content = '\n'.join(new_lines)
            self.output_text = f"{self.output_text}\n{new_content}" if self.output_text else new_content
            
            # Update the display
            self.container.text(self.output_text)
        
    def flush(self):
        pass

@contextmanager
def capture_output(container):
    """Capture stdout and redirect it to a Streamlit container."""
    string_io = StringIO()
    output_handler = StreamlitProcessOutput(container)
    old_stdout = sys.stdout
    sys.stdout = output_handler
    try:
        yield string_io
    finally:
        sys.stdout = old_stdout

# Export the capture_output function
__all__ = ['capture_output']

#--------------------------------#
#             Main               #
#--------------------------------#

# Configure the page
st.set_page_config(
    page_title="CrewAI Research Assistant",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🔍 :red[CrewAI] Research Assistant", anchor=False)

# Create two columns for the input section
input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
with input_col2:
    task_description = st.text_area(
        "What would you like to research?",
        value="Research the latest AI Agent news in February 2025 and summarize each.",
        height=68
    )

col1, col2, col3 = st.columns([1, 0.5, 1])
with col2:
    start_research = st.button("🚀 Start Research", use_container_width=False, type="primary")


if start_research:
    with st.status("🤖 Researching...", expanded=True) as status:
        try:
            # Create persistent container for process output with fixed height.
            process_container = st.container(height=300, border=True)
            output_container = process_container.container()
            
            # Single output capture context.
            with capture_output(output_container):
                #llm = LLM(
                #    base_url="http://localhost:11434",
                #    model=f"ollama/llama3.2:3b",
                #)

                llm = LLM(model="gpt-4o-mini")
                
                researcher = Agent(
                    role='Research Analyst',
                    goal='Conduct thorough research on given topics for the current year 2025',
                    backstory='Expert at analyzing and summarizing complex information',
                    llm=llm,
                    verbose=True,
                    allow_delegation=False,
                )
                
                task = Task(
                    description=task_description,
                    expected_output=dedent("""A comprehensive research report for the year 2025. 
                    The report must be detailed yet concise, focusing on the most significant and impactful findings.
                    
                    Format the output in clean markdown (without code block markers or backticks) using the following structure:

                    # Executive Summary
                    - Brief overview of the research topic (2-3 sentences)
                    - Key highlights and main conclusions
                    - Significance of the findings

                    # Key Findings
                    - Major discoveries and developments
                    - Market trends and industry impacts
                    - Statistical data and metrics (when available)
                    - Technological advancements
                    - Challenges and opportunities

                    # Analysis
                    - Detailed examination of each key finding
                    - Comparative analysis with previous developments
                    - Industry expert opinions and insights
                    - Market implications and business impact

                    # Future Implications
                    - Short-term impacts (next 6-12 months)
                    - Long-term projections
                    - Potential disruptions and innovations
                    - Emerging trends to watch

                    # Recommendations
                    - Strategic suggestions for stakeholders
                    - Action items and next steps
                    - Risk mitigation strategies
                    - Investment or focus areas

                    # Citations
                    - List all sources with titles and URLs
                    - Include publication dates when available
                    - Prioritize recent and authoritative sources
                    - Format as: "[Title] (URL) - [Publication Date if available]"

                    Note: Ensure all information is current and relevant to 2025. Include specific dates, 
                    numbers, and metrics whenever possible to support findings. All claims should be properly 
                    cited using the sources discovered during research.
                    """),
                    agent=researcher,
                    output_file="research_report.md"
                )
                
                crew = Crew(
                    agents=[researcher],
                    tasks=[task],
                    verbose=False,
                    process=Process.sequential
                )
                result = crew.kickoff()
                status.update(label="✅ Research completed!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Error occurred", state="error")
            st.error(f"An error occurred: {str(e)}")
            st.stop()

    # Display the final result
    st.markdown(str(result))
