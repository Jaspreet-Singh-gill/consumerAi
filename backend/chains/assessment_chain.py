from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import backend.config as config
from backend.models.schemas import AssessmentResult

# Initialize the Grok LLM
llm = ChatOpenAI(
    model=config.GROK_MODEL_NAME,
    api_key=config.GROK_API_KEY,
    base_url=config.GROK_BASE_URL,
    temperature=0.0
)

# Prompt Template for dispute assessment
ASSESSMENT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert consumer rights attorney specializing in India's Consumer Protection Act (CPA), 2019.\n"
        "Your task is to analyze the extracted facts of a consumer dispute and assess the case's strength. "
        "You are provided with relevant sections of the CPA 2019 and past judgment precedents from the National Consumer Disputes Redressal Commission (NCDRC).\n\n"
        "CRITICAL RULES:\n"
        "1. Ground every statement and claim strictly in the provided CPA Sections and Precedents context. DO NOT make any unsupported legal claims or fabricate any legal provisions.\n"
        "2. Do not cite any sections or cases that are not present in the provided context.\n"
        "3. Provide an objective strength rating ('Weak', 'Moderate', 'Strong') and a confidence score between 0.0 and 1.0.\n"
        "4. In the reasoning, reference which retrieved sections apply to the dispute and how the past precedents support or contradict the consumer's case."
    ),
    (
        "user",
        "=== EXTRACTED FACTS ===\n"
        "Dispute Category: {category}\n"
        "Product/Service: {product_or_service}\n"
        "Transaction Amount: {amount}\n"
        "Key Dates: {dates}\n"
        "Seller Response: {seller_response}\n"
        "Evidence Available: {evidence_available}\n"
        "Discrepancy (if any): {discrepancy_info}\n\n"
        "=== RETRIEVED CPA 2019 SECTIONS ===\n"
        "{sections_context}\n\n"
        "=== RETRIEVED PAST PRECEDENTS ===\n"
        "{precedents_context}\n\n"
        "Perform the legal triage assessment:"
    )
])

# LCEL Chain for Assessment
assessment_chain = ASSESSMENT_PROMPT | llm.with_structured_output(AssessmentResult)
