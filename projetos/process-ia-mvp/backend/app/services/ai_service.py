import os
import google.generativeai as genai

# Configuração da API Key (Certifique-se de que a variável de ambiente está correta)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_next_question(process_name: str, process_context: str, latest_answer: str | None = None):
    # Inicializa o modelo
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Você é um especialista em processos, Lean, Six Sigma e BPM.
    Processo: {process_name}
    Contexto atual: {process_context}
    Última resposta: {latest_answer if latest_answer else 'Nenhuma'}

    Gere um JSON com a seguinte estrutura:
    - next_question (string)
    - summary (string)
    - missing_data (lista de strings)
    - recommendations (lista de strings)
    """

    # Chamada da API com configuração para garantir resposta em formato JSON
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    return response.text
