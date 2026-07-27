from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import backend.config as config
from backend.models.schemas import FactExtractionResult

# 1. Groq API Client configuration via ChatOpenAI (OpenAI-compatible)
llm = ChatOpenAI(
    model=config.GROQ_MODEL_NAME,
    api_key=config.GROQ_API_KEY,
    base_url=config.GROQ_BASE_URL,
    temperature=0.0
)

# 2. Prompt Template - kept as clear constant
FACT_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert consumer rights analyst assisting Indian consumers. "
        "Your task is to analyze the consumer's dispute description and any extracted text "
        "from their uploaded evidence documents (e.g., invoice details, transaction dates, or emails).\n\n"
        "Carefully extract the following details into the required structured schema:\n"
        "1. Dispute Category: Strictly classify into 'Defective Goods', 'Deficient Services', or 'Unfair trade practice' (always return categories in this form matching the category tags used in the Consumer Protection Act data).\n"
        "2. Amount: Price paid, refund amount, or claimed value. Include currency format if possible (e.g. 'INR X').\n"
        "3. Dates: Key transaction, purchase, cancellation, or communication dates.\n"
        "4. Product or Service: Name of product or service in question.\n"
        "5. Seller Response: The seller's official reaction or standard stance (e.g. refused refund, claimed warranty void, didn't reply).\n"
        "6. Evidence Available: Documents or communications mentioned (e.g. invoice, refund receipts, emails).\n"
        "7. Discrepancy Flag: Set to true ONLY if there is a direct contradiction in details (e.g., buyer claims paying INR 50,000 but the invoice shows INR 5,000; or buyer claims delivery failed but seller claims successful delivery with tracking proof).\n"
        "8. Discrepancy Description: Provide a summary of the contradiction if discrepancy_flag is true, otherwise empty."
    ),
    (
        "user",
        "Consumer Description:\n{description}\n\n"
        "Evidence PDF Content (if available):\n{evidence_text}\n\n"
        "Extract the facts according to the schema:"
    )
])

# 3. LCEL Chain with Structured Output
fact_extraction_chain = FACT_EXTRACTION_PROMPT | llm.with_structured_output(FactExtractionResult)
