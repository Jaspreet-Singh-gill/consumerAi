from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import backend.config as config

# Initialize the Groq LLM
llm = ChatOpenAI(
    model=config.GROQ_MODEL_NAME,
    api_key=config.GROQ_API_KEY,
    base_url=config.GROQ_BASE_URL,
    temperature=0.3  # Moderate temperature for creative legal drafting with precision
)

# Category-specific legal notice drafting guidelines
GUIDELINES_MAP = {
    "Defective/deficient goods": (
        "Focus on the physical defect in the goods. Cite Section 2(34) for product liability "
        "and Section 39(b) for replacement or 39(c) for refund. Demand replacement of the defective product "
        "or a full refund along with compensation for the inconvenience."
    ),
    "Deficiency in service": (
        "Focus on the shortcoming in the performance of service. Cite Section 2(11) for deficiency in service "
        "and Section 39(e)/39(d) for removal of deficiency and compensation. Demand immediate resolution of the "
        "deficiency or refund of service charges, along with compensation for consequential losses."
    ),
    "Unfair trade practice / refund denial": (
        "Focus on the deceptive trade practice, false representations, or illegal withholding of refunds. "
        "Cite Section 2(47) for unfair trade practices and Section 39(c)/39(f) to discontinue the practice "
        "and refund consideration. Demand a complete refund within 15 days, warning of legal actions under the CPA 2019."
    )
}

# Prompt Template for notice drafting
NOTICE_DRAFTING_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a senior Consumer Court Advocate in India. Your goal is to draft a formal, professional, "
        "and legally structured Legal Notice on behalf of a consumer (the Complainant) to be sent to a seller or "
        "service provider (the Opposite Party).\n\n"
        "Ensure the notice conforms to the following standard structure:\n"
        "1. HEADER: 'LEGAL NOTICE' (Bold, centered)\n"
        "2. DATE: Specify the date of drafting/sending\n"
        "3. ADDRESSEE: 'To, [Seller/Service Provider Name] (Use [Opposite Party Name] placeholder if unknown) [Address]'\n"
        "4. SUBJECT: Clear, concise statement (e.g., 'Notice under the Consumer Protection Act, 2019 regarding deficiency in service...')\n"
        "5. FACTUAL RECITALS: A numbered chronology of the facts. Mention transaction dates, product/service name, the specific consideration paid, "
        "invoices/receipts (cite invoice numbers/dates explicitly if present in evidence), the onset of defect/deficiency, and your client's subsequent "
        "unsuccessful attempts to resolve it with the Opposite Party.\n"
        "6. LEGAL COMPLAINT: Cite the relevant sections of the Consumer Protection Act, 2019 provided by the user. Explain how the Opposite Party's "
        "actions violate these sections.\n"
        "7. FINAL DEMANDS: Provide a clear demand for relief (replacement, full refund, and/or compensation for mental harassment and litigation expenses) "
        "and give them exactly 15 days from the receipt of this notice to comply.\n"
        "8. CLOSING: 'Yours faithfully, [Complainant's Name]'"
    ),
    (
        "user",
        "=== DISPUTE DETAILS ===\n"
        "Category: {category}\n"
        "Product/Service: {product_or_service}\n"
        "Amount Paid: {amount}\n"
        "Key Dates: {dates}\n"
        "Seller Response: {seller_response}\n"
        "Evidence Available: {evidence_available}\n"
        "Cited CPA Sections: {cited_sections}\n\n"
        "=== DRAFTING GUIDELINES ===\n"
        "{category_guidelines}\n\n"
        "Draft the legal notice text:"
    )
])

# LCEL Chain for Notice Drafting
notice_drafting_chain = NOTICE_DRAFTING_PROMPT | llm | StrOutputParser()
