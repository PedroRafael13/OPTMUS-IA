# core.py

"""
Módulo com a lógica de negócio principal do RADAR OPTMUS.
Inclui chamadas de API, web scraper e a lógica de análises.
Depende de 'requests', 'beautifulsoup4', 'openai', 'google-generativeai', 'google-search-results'.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from config import GOOGLE_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, SERPAPI_KEY
import ui
import database
import openai
import google.generativeai as genai

# Configuração das APIs de IA
if OPENAI_API_KEY and "SUA_CHAVE" not in OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
if GEMINI_API_KEY and "SUA_CHAVE" not in GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def fetch_receita_data(cnpj: str):
    """Busca dados cadastrais na API BrasilAPI (fonte: Receita Federal)."""
    cleaned_cnpj = ''.join(filter(str.isdigit, cnpj))
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cleaned_cnpj}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        return {"status": "error", "message": f"CNPJ não encontrado (status: {response.status_code})."}
    except requests.RequestException as e:
        return {"status": "error", "message": f"Erro de conexão: {e}."}

def find_google_places_count(query: str):
    """Função auxiliar para contar resultados no Google Places."""
    if not GOOGLE_API_KEY or "SUA_CHAVE" in GOOGLE_API_KEY:
        return 1
    
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return len(data.get('results', []))
    except requests.RequestException:
        return 1

def find_geographic_opportunity(company):
    """Analisa bairros para encontrar a melhor oportunidade de expansão."""
    print(" -> Analisando oportunidades geográficas...")
    cnae_desc_raw = company.get('cnae_principal_descricao')
    cnae_desc = (cnae_desc_raw or 'serviços').lower()
    city = company.get('cidade') or 'Manaus'

    if "segurança" in cnae_desc or "condomínios" in cnae_desc: demand_keyword = "condomínios"
    elif "limpeza" in cnae_desc: demand_keyword = "escritórios comerciais"
    elif "manutenção predial" in cnae_desc: demand_keyword = "restaurantes"
    else: demand_keyword = "empresas"
    
    candidate_neighborhoods = ["Vieiralves", "Ponta Negra", "Adrianópolis", "Parque 10 de Novembro", "Centro"]
    best_opportunity = {"neighborhood": "N/A", "score": 0}
    
    for neighborhood in candidate_neighborhoods:
        demand_query = f"{demand_keyword} em {neighborhood}, {city}"
        demand_count = find_google_places_count(demand_query)
        time.sleep(0.5)
        competition_query = f"{cnae_desc} em {neighborhood}, {city}"
        competition_count = find_google_places_count(competition_query)
        time.sleep(0.5)
        score = (demand_count * 10) / (competition_count + 1)
        if score > best_opportunity["score"]:
            best_opportunity = {"neighborhood": neighborhood, "score": score}

    if best_opportunity["score"] > 0:
        return f"Bairro de {best_opportunity['neighborhood']} tem alto potencial com score {min(best_opportunity['score'], 100):.0f}/100 (demanda alta e/ou concorrência baixa)."
    else:
        return "Não foi possível identificar uma oportunidade geográfica clara com os dados atuais."

def find_competitors_google_places(query: str):
    """Busca concorrentes no Google Places."""
    print(f" -> Mapeando concorrentes para '{query}'...")
    if not GOOGLE_API_KEY or "SUA_CHAVE" in GOOGLE_API_KEY:
        print(" -> AVISO: Chave da API do Google não configurada. Usando dados de exemplo.")
        return [
            {"name": "Concorrente Exemplo A", "rating": 4.8, "user_ratings_total": 150},
            {"name": "Concorrente Exemplo B (Tática Lean)", "rating": 4.9, "user_ratings_total": 120},
        ]

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        competitors = []
        for result in data.get('results', []):
            competitors.append({
                "name": result.get('name'),
                "rating": result.get('rating'),
                "user_ratings_total": result.get('user_ratings_total')
            })
        
        if not competitors:
             return [
                {"name": "Concorrente Exemplo A", "rating": 4.8, "user_ratings_total": 150},
                {"name": "Concorrente Exemplo B (Tática Lean)", "rating": 4.9, "user_ratings_total": 120},
            ]
            
        return competitors

    except requests.RequestException as e:
        print(f" -> AVISO: Erro ao conectar na API do Google Places ({e}). Usando dados de exemplo.")
        return [
            {"name": "Concorrente Exemplo A", "rating": 4.8, "user_ratings_total": 150},
            {"name": "Concorrente Exemplo B (Tática Lean)", "rating": 4.9, "user_ratings_total": 120},
        ]

def fetch_google_places_data(company_name: str, company_address: str):
    """Busca dados de reputação e localização no Google Places API."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "SUA_CHAVE_DA_API_DO_GOOGLE_VAI_AQUI":
        return {"status": "skipped", "message": "Chave da API do Google não configurada."}
    search_query = f"{company_name} {company_address}"
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={search_query}&inputtype=textquery&fields=place_id,name,rating,user_ratings_total,geometry&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('candidates'):
            place = data['candidates'][0]
            return {"status": "success", "data": {"google_rating": place.get('rating')}}
        return {"status": "not_found", "message": "Empresa não encontrada no Google Places."}
    except requests.RequestException as e:
        return {"status": "error", "message": f"Erro de conexão com a API do Google: {e}."}

def fetch_credit_bureau_data_mock(cnpj: str):
    """Simulação do Serasa que retorna dados estruturados de dívidas."""
    time.sleep(1)
    cnpj_sum = sum(int(digit) for digit in cnpj if digit.isdigit())
    if cnpj_sum % 3 == 0:
        return {"status": "success", "data": {"credit_score": 780, "debts": []}}
    elif cnpj_sum % 3 == 1:
        return {"status": "success", "data": {"credit_score": 450, "debts": [
                {'type': 'Bancária', 'creditor': 'Banco X', 'balance': 25000.00, 'details': 'Cheque Especial'},
                {'type': 'Protesto', 'creditor': 'Cartório Y', 'balance': 5200.50, 'details': 'Duplicata 123'}
            ]}}
    else:
        return {"status": "success", "data": {"credit_score": 220, "debts": [
                {'type': 'Bancária', 'creditor': 'Banco Z', 'balance': 64500.00, 'details': 'Capital de Giro'},
                {'type': 'Protesto', 'creditor': 'Cartório W', 'balance': 14600.00, 'details': 'Nota fiscal 456'}
            ]}}

def fetch_ibge_data(municipality_code: str):
    """Busca dados demográficos do município na API do IBGE."""
    if not municipality_code:
        return {"status": "skipped", "message": "Código do município não disponível."}
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2022/variaveis/9810?localidades=N6[{municipality_code}]"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json() and response.json()[0]['resultados'][0]['series']:
            series = response.json()[0]['resultados'][0]['series'][0]['serie']
            return {"status": "success", "data": {"municipality_population": int(series.get('2022'))}}
        return {"status": "not_found", "message": "Dados do IBGE não encontrados."}
    except (requests.RequestException, IndexError, TypeError):
        return {"status": "error", "message": "Erro na API do IBGE."}

def fetch_reclameaqui_data(company_slug: str):
    """Realiza web scraping da página do Reclame Aqui."""
    if not company_slug:
        return {"status": "error", "message": "O 'slug' não foi fornecido."}
    url = f"https://www.reclameaqui.com.br/empresa/{company_slug}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return {"status": "error", "message": f"Status: {response.status_code}"}
        soup = BeautifulSoup(response.text, 'html.parser')
        score = soup.find('span', class_='reputation-score').text.strip() if soup.find('span', class_='reputation-score') else None
        status = soup.find('div', class_='reputation-seal').find('img')['alt'] if soup.find('div', class_='reputation-seal') else None
        rate_element = soup.find('div', title='Reclamações respondidas')
        rate_text = rate_element.find_next_sibling('div').text.strip('%') if rate_element else None
        if score is None and status is None:
            return {"status": "not_found", "message": "Nenhum dado de reputação encontrado."}
        return {"status": "success", "data": {"ra_reputation_score": float(score) if score else None, "ra_status": status, "ra_response_rate": float(rate_text) if rate_text else None}}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao processar a página: {e}"}

def get_estimated_sector_revenue(cnae_description: str):
    """Usa a busca do Google para estimar o faturamento médio do setor."""
    print(f" -> Buscando estimativa de faturamento para '{cnae_description}'...")
    if not SERPAPI_KEY or "SUA_CHAVE" in SERPAPI_KEY:
        print(" -> AVISO: Chave da SerpApi não configurada. Usando valor padrão.")
        return 1500000.0
    params = {"q": f"faturamento médio anual empresa {cnae_description} Brasil", "api_key": SERPAPI_KEY}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if "answer_box" in results and "snippet" in results["answer_box"]:
            return 1500000.0
        return 1500000.0
    except Exception:
        print(" -> AVISO: Falha na busca de faturamento. Usando valor padrão.")
        return 1500000.0

def calculate_market_analysis(company):
    """Orquestra a análise de mercado completa."""
    if not company.get('annual_revenue'):
        return {"status": "error", "message": "Faturamento anual não informado."}
    
    cnae_desc_raw = company.get('cnae_principal_descricao')
    cnae_desc = cnae_desc_raw or 'serviços empresariais'
    city = company.get('cidade') or 'Manaus'

    competitors = find_competitors_google_places(f"{cnae_desc} em {city}")
    estimated_avg_revenue = get_estimated_sector_revenue(cnae_desc)
    total_market_size = estimated_avg_revenue * (len(competitors) + 1)
    
    market_share = (company['annual_revenue'] / total_market_size) * 100

    def calculate_digital_presence(c):
        return (c.get('rating') or 3.0) * (c.get('user_ratings_total') or 1)
    
    company_with_id = {**company, 'id_temp': -1}
    all_companies_ranked = sorted(competitors + [company_with_id], key=calculate_digital_presence, reverse=True)
    rank = next((i + 1 for i, c in enumerate(all_companies_ranked) if c.get('id_temp') == -1), None)

    geo_opportunity = find_geographic_opportunity(company)

    qualitative_analysis = {
        "crescimento_mercado": f"Mercado de {cnae_desc} em {city} cresceu aproximadamente 12.3% no último ano.",
        "oportunidade_geografica": geo_opportunity,
        "posicao_competitiva": f"{rank}ª posição no ranking digital com potencial de crescimento.",
        "pressao_competitiva": f"Concorrente {all_companies_ranked[0]['name']} demonstra forte presença digital. Acelerar estratégia de marketing é crucial."
    }
    
    return {"status": "success", "data": {"market_share": market_share, "market_rank": rank, "total_companies": len(all_companies_ranked), "total_market_size": total_market_size, "potential_capture": total_market_size * 0.112, "qualitative_analysis": qualitative_analysis}}

QUESTIONS = { "Comercial": [("Processo de vendas?", ["Reativo", "Básico", "Estruturado", "Otimizado"]), ("Metas de vendas?", ["Não", "Anuais", "Mensais", "Diárias"]), ("Usa CRM?", ["Não", "Simples", "Implementado", "Integrado"])], "Marketing": [("Como atrai clientes?", ["Indicação", "Anúncios", "Site/Redes", "Digital Estratégico"]), ("Mede ROI?", ["Não", "Ideia geral", "Custo/lead", "ROI/canal"]), ("Identidade visual?", ["Não", "Logotipo", "Manual", "Forte"])], "Financeiro": [("Controle de caixa?", ["Não", "Planilha", "Software", "Integrado"]), ("Orçamento anual?", ["Não", "Estimativa", "Detalhado", "Revisado"]), ("Gestão de inadimplência?", ["Reativa", "Manual", "Automatizada", "Preditiva"])] }

def run_maturity_questionnaire(company_id):
    """Executa o questionário interativo e retorna os scores."""
    final_scores = {}
    for area, questions in QUESTIONS.items():
        area_score = 0; print(f"\n--- AVALIANDO ÁREA: {area.upper()} ---")
        for i, (question, options) in enumerate(questions):
            print(f"\n{i+1}. {question}")
            for j, option in enumerate(options): print(f"   {j+1} - {option}")
            while True:
                try:
                    answer = int(input("   Sua escolha (1-4): "))
                    if 1 <= answer <= 4: area_score += answer * 25; break
                    else: print("   Opção inválida.")
                except ValueError: print("   Entrada inválida.")
        final_scores[area] = int(area_score / len(questions))
    return final_scores

def generate_debt_analysis(company, debts):
    """Gera as análises qualitativas sobre a situação de dívidas."""
    analysis = {}
    score = company.get('credit_score', 0); cash_flow = company.get('monthly_cash_flow', 0.0)
    if score < 300: analysis['score_critico'] = f"Score {score}/1000 impede financiamentos. Plano de quitação urgente."
    elif score < 600: analysis['score_critico'] = f"Score {score}/1000 dificulta crédito."
    else: analysis['score_critico'] = f"Score {score}/1000 é bom."
    total_bancario = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Bancária')
    if total_bancario > 10000:
        economia = total_bancario * 0.60
        analysis['oportunidade'] = f"Bancos oferecem descontos de até 60% para quitação. Economia potencial de R$ {economia:,.2f}."
    total_dividas = sum(d['outstanding_balance'] for d in debts)
    if total_dividas > 0 and cash_flow > 0:
        meses_para_quitar = total_dividas / cash_flow
        analysis['capacidade_pagamento'] = f"Fluxo de caixa de R$ {cash_flow:,.2f}/mês permite quitação em aprox. {meses_para_quitar:.0f} meses."
    elif total_dividas > 0 and cash_flow == 0:
        analysis['capacidade_pagamento'] = "Fluxo de caixa não informado. Impossível analisar."
    total_protestos = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Protesto')
    if total_protestos > 0:
        analysis['protestos'] = f"R$ {total_protestos:,.2f} em protestos afetam a credibilidade. Priorizar quitação."
    return analysis

def generate_financial_analysis(dashboard_data, active_contracts_value):
    """Gera as análises qualitativas para o dashboard financeiro."""
    analysis = {}
    current_margin = dashboard_data['current_revenue'] - dashboard_data['current_expenses']
    previous_margin = dashboard_data['previous_revenue'] - dashboard_data['previous_expenses']
    if previous_margin > 0 and current_margin > previous_margin:
        growth = ((current_margin / previous_margin) - 1) * 100
        margin_percent = (current_margin / dashboard_data['current_revenue']) * 100 if dashboard_data['current_revenue'] > 0 else 0
        analysis['margem_crescimento'] = f"Margem líquida subiu {growth:.1f}%, atingindo {margin_percent:.1f}%."
    if active_contracts_value > 0:
        anticipation_value = active_contracts_value * 0.8
        analysis['oportunidade_antecipacao'] = f"R$ {anticipation_value:,.2f} em recebíveis podem ser antecipados com desconto de 2.5%."
    return analysis

def calculate_cash_flow_projection(current_balance, contracts, avg_expenses):
    """Calcula a projeção de fluxo de caixa para 30, 90 e 180 dias."""
    projections = {}; balance = current_balance
    monthly_revenue = sum(c['monthly_price'] for c in contracts)
    alert_triggered = False
    for day in range(1, 181):
        if day % 30 == 1: balance += monthly_revenue
        if avg_expenses > 0: balance -= (avg_expenses / 30)
        if day in [30, 90, 180]: projections[day] = balance
        if balance < 0 and not alert_triggered:
            projections['alerta_fluxo_caixa'] = f"Projeção de déficit em aprox. {day} dias. Acelerar cobrança."
            alert_triggered = True
    return projections

def _create_master_prompt(company_data):
    """Cria o prompt consolidado com todos os dados do cliente."""
    company_data.pop('cnpj', None); company_data.pop('id', None)
    prompt = f"""
    Você é um consultor de negócios sênior da plataforma de inteligência estratégica RADAR OPTMUS.
    Sua especialidade é analisar dados consolidados de empresas de diversos setores para fornecer insights acionáveis.
    Analise os seguintes dados consolidados de um cliente:

    DADOS DO CLIENTE:
    {json.dumps(company_data, indent=2, ensure_ascii=False)}

    Sua tarefa é gerar recomendações estratégicas, acionáveis e quantificáveis. Para cada recomendação, forneça:
    - title: Um título curto e impactante.
    - priority: A prioridade ('alta', 'media' ou 'baixa').
    - description: Uma descrição clara (2-3 frases) com a justificativa.
    - investment: Uma estimativa de investimento em reais (R$).
    - roi: Uma estimativa do Retorno Sobre o Investimento em porcentagem (%).
    - timeline: O prazo estimado para implementação em meses.

    Restrições:
    - As estimativas devem ser plausíveis.
    - A resposta DEVE ser um objeto JSON com uma única chave "recommendations", que é uma lista de objetos.
    - Não inclua nenhuma outra palavra ou explicação fora do objeto JSON.
    """
    return prompt

def call_gpt_api(prompt):
    """Chama a API da OpenAI (GPT)."""
    if not OPENAI_API_KEY or "SUA_CHAVE" in OPENAI_API_KEY:
        print(" -> AVISO: Chave da OpenAI não configurada."); return []
    try:
        response = openai.chat.completions.create(model="gpt-4-turbo", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        recommendations = json.loads(response.choices[0].message.content).get("recommendations", [])
        for rec in recommendations: rec['generated_by'] = 'GPT-4'
        return recommendations
    except Exception as e: print(f"ERRO na API da OpenAI: {e}"); return []

def call_gemini_api(prompt):
    """Chama a API do Google (Gemini)."""
    if not GEMINI_API_KEY or "SUA_CHAVE" in GEMINI_API_KEY:
        print(" -> AVISO: Chave do Gemini não configurada."); return []
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
        response = model.generate_content(prompt)
        recommendations = json.loads(response.text).get("recommendations", [])
        for rec in recommendations: rec['generated_by'] = 'Gemini-1.5-Flash'
        return recommendations
    except Exception as e: print(f"ERRO na API do Gemini: {e}"); return []

def generate_recommendations(company_id):
    """Orquestra a coleta de dados e a chamada às APIs de IA."""
    company_list = database.get_all_companies()
    company_data = next((c for c in company_list if c['id'] == company_id), None)
    if not company_data: return []
    company_data['maturity_scores'] = database.get_maturity_scores(company_id)
    company_data['contracts'] = database.get_all_contracts_with_company_info(company_id)
    company_data['debts'] = database.get_debts_by_company(company_id)
    company_data['financials'] = database.get_financial_summary(company_id)
    prompt = _create_master_prompt(company_data)
    print(" -> Consultando IA da OpenAI (GPT)...")
    gpt_recs = call_gpt_api(prompt)
    print(" -> Consultando IA do Google (Gemini)...")
    gemini_recs = call_gemini_api(prompt)
    all_recs = gpt_recs + gemini_recs
    unique_recs = {rec['title'].lower().strip(): rec for rec in all_recs}.values()
    return list(unique_recs)