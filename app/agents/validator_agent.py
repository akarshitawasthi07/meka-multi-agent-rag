from app.llm.groq_llm import get_llm

def validator_agent(state: dict):
    llm = get_llm()

    answer = state["final_answer"]
    docs = state["retrieved_docs"]

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Check if answer is grounded in context.

Context:
{context}

Answer:
{answer}

Respond ONLY:
STATUS: GROUNDED or HALLUCINATED
REASON: short reason
"""

    resp = llm.invoke(prompt).content

    status, reason = "UNKNOWN", "Could not parse"
    for line in resp.splitlines():
        if line.startswith("STATUS"):
            status = line.split(":")[1].strip()
        if line.startswith("REASON"):
            reason = line.split(":")[1].strip()

    return {
        "validation": status,
        "reason": reason
    }