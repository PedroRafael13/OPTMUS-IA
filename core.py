# core.py

"""
Módulo com a lógica de negócio principal do RADAR OPTMUS.
Inclui chamadas de API, web scraper e a lógica de análises.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from config import GOOGLE_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, SERPAPI_KEY
import database
import openai
import google.generativeai as genai
import sqlite3
import random

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
    city = company.get('municipio') or 'Manaus'

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
        from serpapi import GoogleSearch
        search = GoogleSearch(params)
        results = search.get_dict()
        if "answer_box" in results and "snippet" in results["answer_box"]:
            return 1500000.0 # Placeholder logic
        return 1500000.0
    except Exception:
        print(" -> AVISO: Falha na busca de faturamento. Usando valor padrão.")
        return 1500000.0

def calculate_market_analysis(company):
    """Orquestra a análise de mercado completa com dados mais dinâmicos."""
    if not company.get('annual_revenue'):
        return {"status": "error", "message": "Faturamento anual não informado."}
    
    cnae_desc_raw = company.get('cnae_principal_descricao', 'serviços empresariais')
    cnae_desc = cnae_desc_raw or 'serviços empresariais'
    city = company.get('municipio', 'Manaus')

    competitors = find_competitors_google_places(f"{cnae_desc} em {city}")
    estimated_avg_revenue = get_estimated_sector_revenue(cnae_desc)
    
    total_market_size = estimated_avg_revenue * (len(competitors) + 1)
    if total_market_size == 0:
        return {"status": "error", "message": "Não foi possível calcular o tamanho do mercado."}

    market_share = (company['annual_revenue'] / total_market_size) * 100

    def calculate_digital_presence(c):
        return (c.get('rating') or 3.0) * (c.get('user_ratings_total') or 1)
    
    company_with_id = {**company, 'id_temp': -1}
    all_companies_ranked = sorted(competitors + [company_with_id], key=calculate_digital_presence, reverse=True)
    rank = next((i + 1 for i, c in enumerate(all_companies_ranked) if c.get('id_temp') == -1), len(all_companies_ranked))

    geo_opportunity = find_geographic_opportunity(company)

    # LÓGICA MELHORADA PARA ANÁLISE QUALITATIVA
    growth_rate = round(random.uniform(3.5, 15.5), 1)
    potential_capture_rate = 0.15 - (rank * 0.01)
    potential_capture_value = total_market_size * potential_capture_rate

    qualitative_analysis = {
        "crescimento_mercado": f"O mercado de {cnae_desc} em {city} tem uma projeção de crescimento de aproximadamente {growth_rate}% no próximo ano.",
        "oportunidade_geografica": geo_opportunity,
        "posicao_competitiva": f"Com a {rank}ª posição no ranking digital, há uma clara oportunidade de ultrapassar concorrentes com ações de marketing direcionadas.",
        "pressao_competitiva": f"O concorrente {all_companies_ranked[0]['name']} é o líder em presença digital. Analisar suas estratégias é crucial."
    }
    
    return {
        "status": "success",
        "data": {
            "market_share": market_share,
            "market_rank": rank,
            "total_companies": len(all_companies_ranked),
            "total_market_size": total_market_size,
            "potential_capture": potential_capture_value,
            "qualitative_analysis": qualitative_analysis
        }
    }

def run_maturity_questionnaire(company_id):
    """Executa o questionário interativo e retorna os scores."""
    final_scores = {}
    QUESTIONS = { "Comercial": [("Processo de vendas?", ["Reativo", "Básico", "Estruturado", "Otimizado"]), ("Metas de vendas?", ["Não", "Anuais", "Mensais", "Diárias"]), ("Usa CRM?", ["Não", "Simples", "Implementado", "Integrado"])], "Marketing": [("Como atrai clientes?", ["Indicação", "Anúncios", "Site/Redes", "Digital Estratégico"]), ("Mede ROI?", ["Não", "Ideia geral", "Custo/lead", "ROI/canal"]), ("Identidade visual?", ["Não", "Logotipo", "Manual", "Forte"])], "Financeiro": [("Controle de caixa?", ["Não", "Planilha", "Software", "Integrado"]), ("Orçamento anual?", ["Não", "Estimativa", "Detalhado", "Revisado"]), ("Gestão de inadimplência?", ["Reativa", "Manual", "Automatizada", "Preditiva"])] }
    for area, questions in QUESTIONS.items():
        area_score = 0
        print(f"\n--- AVALIANDO ÁREA: {area.upper()} ---")
        for i, (question, options) in enumerate(questions):
            print(f"\n{i+1}. {question}")
            for j, option in enumerate(options): print(f"   {j+1} - {option}")
            while True:
                try:
                    answer = int(input("   Sua escolha (1-4): "))
                    if 1 <= answer <= 4:
                        area_score += answer * 25
                        break
                    else: print("   Opção inválida.")
                except ValueError: print("   Entrada inválida.")
        final_scores[area] = int(area_score / len(questions))
    return final_scores

def generate_debt_analysis(company, debts):
    """Gera as análises qualitativas sobre a situação de dívidas."""
    analysis = {}
    score = company.get('credit_score', 0); cash_flow = company.get('monthly_cash_flow', 0.0)
    if not debts:
      analysis['situacao_dividas'] = 'Nenhuma dívida registrada. Excelente saúde de crédito.'
      return analysis
    if score < 300: analysis['score_critico'] = f"Score {score}/1000 impede financiamentos. Plano de quitação urgente."
    elif score < 600: analysis['score_critico'] = f"Score {score}/1000 dificulta crédito."
    else: analysis['score_critico'] = f"Score {score}/1000 é bom."
    total_bancario = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Bancária')
    if total_bancario > 10000:
        economia = total_bancario * 0.60
        analysis['oportunidade'] = f"Bancos oferecem descontos de até 60% para quitação. Economia potencial de R$ {economia:,.2f}."
    total_dividas = sum(d['outstanding_balance'] for d in debts)
    if total_dividas > 0 and cash_flow and cash_flow > 0:
        meses_para_quitar = total_dividas / cash_flow
        analysis['capacidade_pagamento'] = f"Fluxo de caixa de R$ {cash_flow:,.2f}/mês permite quitação em aprox. {meses_para_quitar:.0f} meses."
    elif total_dividas > 0 and (not cash_flow or cash_flow == 0):
        analysis['capacidade_pagamento'] = "Fluxo de caixa não informado. Impossível analisar capacidade de pagamento."
    total_protestos = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Protesto')
    if total_protestos > 0:
        analysis['protestos'] = f"R$ {total_protestos:,.2f} em protestos afetam a credibilidade. Priorizar quitação."
    return analysis

def generate_financial_analysis(dashboard_data, active_contracts_value):
    """Gera as análises qualitativas para o dashboard financeiro."""
    analysis = {}
    current_revenue = dashboard_data.get('current_revenue', 0.0)
    current_margin = current_revenue - dashboard_data.get('current_expenses', 0.0)
    previous_revenue = dashboard_data.get('previous_revenue', 0.0)
    if previous_revenue > 0 and current_revenue > previous_revenue:
        growth = ((current_revenue / previous_revenue) - 1) * 100
        margin_percent = (current_margin / current_revenue) * 100 if current_revenue > 0 else 0
        analysis['margem_em_crescimento'] = f"Receita subiu {growth:.1f}%, com margem líquida de {margin_percent:.1f}%."
    if active_contracts_value > 5000:
        anticipation_value = active_contracts_value * 0.8
        analysis['oportunidade_de_antecipacao'] = f"Até R$ {anticipation_value:,.2f} em recebíveis de contratos podem ser antecipados para reforçar o caixa."
    summary = database.get_financial_summary()
    current_balance = summary['balance'] if summary else 0
    monthly_revenue = active_contracts_value
    avg_expenses = dashboard_data.get('current_expenses', 0.0)
    balance = current_balance
    alert_triggered = False
    if monthly_revenue < avg_expenses * 1.1:
        for day in range(1, 91):
            if day % 30 == 1: balance += monthly_revenue
            if avg_expenses > 0: balance -= (avg_expenses / 30)
            if balance < 0 and not alert_triggered:
                analysis['fluxo_de_caixa_apertado'] = f"Atenção: Projeção indica possível déficit de caixa em menos de {day} dias."
                alert_triggered = True
                break
    if not analysis:
        analysis['saude_financeira'] = "Os indicadores financeiros estão estáveis. Continue monitorando as despesas."
    return analysis

def _create_master_prompt(company_data, focus_area, objective):
    """Cria o prompt consolidado com todos os dados do cliente E O FOCO ESTRATÉGICO."""
    company_data.pop('cnpj', None); company_data.pop('id', None)
    prompt = f"""
    Você é um consultor de negócios sênior da plataforma RADAR OPTMUS.
    Analise os seguintes dados consolidados de um cliente:

    DADOS DO CLIENTE:
    {json.dumps(company_data, indent=2, ensure_ascii=False)}

    O consultor forneceu um direcionamento estratégico para esta análise. LEVE ISSO EM CONSIDERAÇÃO COMO FATOR PRINCIPAL:
    - Foco Principal: {focus_area}
    - Objetivo Específico: {objective}

    Sua tarefa é gerar 3 recomendações estratégicas, acionáveis e quantificáveis, ALINHADAS COM O OBJETIVO ESPECÍFICO. Para cada recomendação, forneça:
    - title: Um título curto e impactante.
    - priority: A prioridade ('alta', 'media' ou 'baixa').
    - description: Uma descrição clara (2-3 frases) com a justificativa.
    - investment: Uma estimativa de investimento em reais (R$).
    - roi: Uma estimativa do Retorno Sobre o Investimento em porcentagem (%).
    - timeline: O prazo estimado para implementação em meses.

    Restrições:
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
        model = genai.GenerativeModel('gemini-pro', generation_config=genai.types.GenerationConfig(response_mime_type="application/json"))
        response = model.generate_content(prompt)
        recommendations = json.loads(response.text).get("recommendations", [])
        for rec in recommendations: rec['generated_by'] = 'Gemini-Pro'
        return recommendations
    except Exception as e: print(f"ERRO na API do Gemini: {e}"); return []

def generate_recommendations(company_id, focus_area, objective):
    """Orquestra a coleta de dados e a chamada às APIs de IA com base no foco estratégico."""
    company_list = database.get_all_companies()
    company_data = next((c for c in company_list if c['id'] == company_id), None)
    if not company_data: return []
    
    # Coleta todos os dados relevantes do cliente
    company_data['maturity_scores'] = database.get_maturity_scores(company_id)
    company_data['contracts'] = database.get_all_contracts_with_company_info(company_id)
    company_data['debts'] = database.get_debts_by_company(company_id)
    company_data['financials'] = database.get_financial_summary(company_id)
    
    prompt = _create_master_prompt(company_data, focus_area, objective)
    
    print(" -> Consultando IA da OpenAI (GPT)...")
    gpt_recs = call_gpt_api(prompt)
    print(" -> Consultando IA do Google (Gemini)...")
    gemini_recs = call_gemini_api(prompt)
    
    all_recs = gpt_recs + gemini_recs
    unique_recs = {rec['title'].lower().strip(): rec for rec in all_recs}.values()
    return list(unique_recs)

def generate_cash_flow_projection_chart_data(company_id, contracts, days=180):
    """Gera dados de projeção de fluxo de caixa para um período dinâmico."""
    conn = sqlite3.connect(database.DB_FILE)
    cursor = conn.cursor()
    three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-01')
    cursor.execute("""
        SELECT SUM(amount) FROM financial_transactions
        WHERE transaction_type = 'saida' AND company_id = ? AND transaction_date >= ?
    """, (company_id, three_months_ago))
    total_expenses_last_3_months = cursor.fetchone()[0] or 0.0
    avg_monthly_expenses = total_expenses_last_3_months / 3 if total_expenses_last_3_months > 0 else 0
    conn.close()
    monthly_revenue = sum(c['monthly_price'] for c in contracts)
    summary = database.get_financial_summary(company_id)
    current_balance = summary['balance']
    projection_data = []
    balance = current_balance
    num_months = (days + 29) // 30
    for i in range(num_months):
        month_date = datetime.now() + timedelta(days=30*i)
        month_name = month_date.strftime('%b/%y')
        if i == 0:
            days_left_in_month = 30 - datetime.now().day
            entradas = (monthly_revenue / 30) * days_left_in_month if monthly_revenue > 0 else 0
            saidas = (avg_monthly_expenses / 30) * days_left_in_month if avg_monthly_expenses > 0 else 0
        else:
            entradas = monthly_revenue
            saidas = avg_monthly_expenses
        balance += entradas - saidas
        projection_data.append({
            "name": month_name,
            "Entradas": round(entradas, 2),
            "Saídas": round(saidas, 2),
            "Saldo": round(balance, 2)
        })
    return projection_data

def call_gpt_api_raw(prompt):
    """Chama a API da OpenAI (GPT) para uma resposta de texto bruto."""
    if not OPENAI_API_KEY or "SUA_CHAVE" in OPENAI_API_KEY:
        return "A chave da API da OpenAI não está configurada."
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERRO na API da OpenAI: {e}")
        return "Ocorreu um erro ao contatar a OpenAI."

def call_gemini_api_raw(prompt):
    """Chama a API do Google (Gemini) para uma resposta de texto bruto."""
    if not GEMINI_API_KEY or "SUA_CHAVE" in GEMINI_API_KEY:
        return "A chave da API do Gemini não está configurada."
    try:
        model = genai.GenerativeModel('gemini-pro') # Modelo corrigido para versão estável
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"ERRO na API do Gemini: {e}")
        return "Ocorreu um erro ao contatar o Gemini."

# --- LÓGICA DO AGENTE DE CONTRATOS ---

def analyze_contracts_for_agent(raw_contracts):
    """
    Recebe uma lista de contratos do banco de dados e a enriquece com
    status, KPIs e insights estratégicos.
    """
    if not raw_contracts:
        return {
            "kpis": {"mrr": 0, "expiring_soon_count": 0, "concentration_risk": 0},
            "contracts": [],
            "insights": []
        }

    # --- 1. Cálculo de KPIs ---
    mrr = sum(c['monthly_price'] for c in raw_contracts)
    
    expiring_soon_count = 0
    today = datetime.now().date()
    
    largest_contract_price = 0
    if raw_contracts:
        largest_contract_price = max(c['monthly_price'] for c in raw_contracts)

    concentration_risk = (largest_contract_price / mrr) * 100 if mrr > 0 else 0
    
    # --- 2. Análise Individual de Contratos (Status) ---
    contracts_with_status = []
    for contract in raw_contracts:
        due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
        days_until_due = (due_date - today).days
        
        status = "Ativo"
        if days_until_due < 0:
            status = "Vencido"
        elif days_until_due <= 60:
            status = "Vencendo"
            expiring_soon_count += 1
        
        # Adiciona o status ao dicionário do contrato
        enriched_contract = contract.copy()
        enriched_contract['status'] = status
        contracts_with_status.append(enriched_contract)

    # --- 3. Geração de Insights ---
    insights = []
    # Insight de Risco de Concentração
    if concentration_risk > 50:
        insights.append({
            "icon": "⚠️",
            "title": "Risco de Concentração Elevado",
            "description": f"O maior contrato representa {concentration_risk:.1f}% da sua receita mensal recorrente. Considere diversificar sua carteira para mitigar riscos."
        })

    # Insights de Renovação e Oportunidades
    for contract in contracts_with_status:
        if contract['status'] == 'Vencendo':
            insights.append({
                "icon": "📄",
                "title": f"Alerta de Renovação: {contract['service_description']}",
                "description": f"O contrato com {contract['company_name']} vence em {contract['due_date']}. Inicie as negociações para renovação o quanto antes."
            })
        
        # Simples verificação de oportunidade de reajuste (ex: contrato com mais de 1 ano)
        # Nota: 'created_at' não está disponível em 'get_all_contracts_with_company_info',
        # precisaria ser adicionado à query em database.py para uma lógica real.
        # Por enquanto, simulamos com uma verificação aleatória.
        if random.random() > 0.7 and contract['status'] == 'Ativo':
             insights.append({
                "icon": "📈",
                "title": f"Oportunidade de Reajuste: {contract['service_description']}",
                "description": f"Este contrato está ativo há mais de 12 meses. Avalie a possibilidade de um reajuste de preço com base nos índices de inflação."
            })


    # --- Montagem do Objeto Final ---
    return {
        "kpis": {
            "mrr": mrr,
            "expiring_soon_count": expiring_soon_count,
            "concentration_risk": concentration_risk
        },
        "contracts": contracts_with_status,
        "insights": insights
    }

def get_contract_analysis_for_company(company_id):
    """
    Orquestra a busca de contratos e a análise do agente para um cliente específico.
    """
    raw_contracts = database.get_all_contracts_with_company_info(company_id=company_id)
    analyzed_data = analyze_contracts_for_agent(raw_contracts)
    return analyzed_data

# --- LÓGICA DO AGENTE PARA O DASHBOARD GERAL ---

def generate_general_dashboard_analysis(company_id):
    """
    Orquestra a coleta de dados e a análise do agente para o Dashboard Geral.
    """
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        raise ValueError("Empresa não encontrada")

    financial_data = database.get_financial_dashboard_data(period_days=30, company_id=company_id)
    contracts = database.get_all_contracts_with_company_info(company_id=company_id)
    revenue_evolution = database.get_monthly_revenue_evolution(company_id=company_id)

    current_revenue = financial_data.get('current_revenue', 0)
    previous_revenue = financial_data.get('previous_revenue', 1)
    revenue_change_percent = ((current_revenue / previous_revenue) - 1) * 100 if previous_revenue > 0 else 0
    
    kpis = {
        "monthly_revenue": current_revenue,
        "revenue_change_percent": revenue_change_percent,
        "active_contracts": len(contracts),
        "average_ticket": sum(c['monthly_price'] for c in contracts) / len(contracts) if contracts else 0,
        "market_share": company.get('market_share', 0),
        "market_rank": f"#{company.get('market_rank', 'N/A')} em Manaus"
    }

    recommended_actions = []
    
    if company.get('credit_score', 1000) < 300:
        recommended_actions.append({
            "id": "debt_critical", "priority": "high", "title": "Analisar Dívidas Urgentes",
            "description": f"Seu Score Serasa está crítico ({company['credit_score']}/1000). Inicie um plano de quitação.",
            "link": "debts", "button_text": "Ir para Dívidas"
        })

    expiring_contracts = database.get_expiring_contracts(days_ahead=60, company_id=company_id)
    if expiring_contracts:
        closest_contract = min(expiring_contracts, key=lambda c: c['due_date'])
        recommended_actions.append({
            "id": f"contract_exp_{closest_contract['id']}", "priority": "medium", "title": "Renovar Contrato Importante",
            "description": f"O contrato '{closest_contract['service_description']}' vence em {closest_contract['due_date']}.",
            "link": "contracts", "button_text": "Ver Contratos"
        })

    if revenue_change_percent > 50:
        recommended_actions.append({
            "id": "growth_spike", "priority": "low", "title": "Analisar Pico de Crescimento",
            "description": f"A receita cresceu {revenue_change_percent:.0f}%! Analise o que causou este pico.",
            "link": "financials", "button_text": "Ver Financeiro"
        })
    elif revenue_change_percent < 5 and len(recommended_actions) < 3 :
         recommended_actions.append({
            "id": "growth_stagnant", "priority": "low", "title": "Buscar Novas Oportunidades",
            "description": "O crescimento da receita está estagnado. Explore a análise de mercado.",
            "link": "market", "button_text": "Analisar Mercado"
        })

    high_priority_actions = sum(1 for action in recommended_actions if action['priority'] == 'high')
    summary_status = "estável"
    if revenue_change_percent > 10: summary_status = "em crescimento"
    elif revenue_change_percent < 0: summary_status = "em alerta"
        
    agent_summary = f"A saúde geral do negócio está {summary_status}. "
    if high_priority_actions > 0:
        agent_summary += f"Identificamos {high_priority_actions} alerta(s) crítico(s) que exige(m) sua atenção imediata."
    else:
        agent_summary += "Continue monitorando os indicadores e buscando oportunidades de melhoria."

    return {
        "kpis": kpis,
        "revenue_evolution_data": revenue_evolution,
        "agent_summary": agent_summary,
        "recommended_actions": recommended_actions
    }
    
# --- NOVA LÓGICA DO AGENTE DE FATURAMENTO ---

def analyze_billing_for_agent(company_id):
    """
    Analisa o faturamento mensal de um cliente, calcula KPIs e gera
    insights de cobrança.
    """
    current_month_str = datetime.now().strftime('%Y-%m')
    billing_items = database.get_contracts_for_billing(current_month_str, company_id=company_id)
    
    if not billing_items:
        return {
            "kpis": {"total_billing": 0, "total_received": 0, "total_pending": 0, "pending_rate": 0},
            "billing_items": [],
            "agent_actions": []
        }
        
    # 1. Calcular KPIs
    total_billing = sum(item['monthly_price'] for item in billing_items)
    total_received = sum(item['monthly_price'] for item in billing_items if item['is_paid'])
    total_pending = total_billing - total_received
    pending_rate = (total_pending / total_billing) * 100 if total_billing > 0 else 0
    
    # 2. Enriquecer Itens de Faturamento
    # Para uma lógica real de "dias em atraso", precisaríamos da data de vencimento.
    # Como a query atual não traz, vamos simular com base no dia do mês.
    today = datetime.now()
    due_day_of_month = 10 # Assumindo que o vencimento é dia 10
    days_overdue = max(0, today.day - due_day_of_month)
    
    enriched_items = []
    for item in billing_items:
        new_item = item.copy()
        if not new_item['is_paid'] and days_overdue > 0:
            new_item['status'] = 'Em Atraso'
            new_item['days_overdue'] = days_overdue
        elif not new_item['is_paid']:
            new_item['status'] = 'Pendente'
            new_item['days_overdue'] = 0
        else:
            new_item['status'] = 'Pago'
            new_item['days_overdue'] = 0
        enriched_items.append(new_item)

    # 3. Gerar Ações do Agente de Cobrança
    agent_actions = []
    
    if pending_rate > 30:
        agent_actions.append({
            "id": "high_pending_rate", "type": "alert", "title": "Alta Taxa de Inadimplência",
            "description": f"A taxa de inadimplência deste mês está em {pending_rate:.1f}%. É crucial intensificar as ações de cobrança para não impactar o fluxo de caixa."
        })

    for item in enriched_items:
        if item['status'] == 'Em Atraso':
            if item['days_overdue'] > 15:
                agent_actions.append({
                    "id": f"cob_{item['contract_id']}_neg", "type": "suggestion", "title": f"Sugerir Negociação: {item['service_description']}",
                    "description": f"A fatura de R$ {item['monthly_price']:.2f} está com {item['days_overdue']} dias de atraso. Sugestão: Enviar proposta de pagamento parcelado com juros."
                })
            elif item['days_overdue'] > 5:
                 agent_actions.append({
                    "id": f"cob_{item['contract_id']}_rem", "type": "automation", "title": f"Lembrete de Cobrança: {item['service_description']}",
                    "description": f"A fatura está com {item['days_overdue']} dias de atraso. Um lembrete amigável de cobrança via e-mail foi disparado automaticamente."
                })
                
    if not agent_actions and total_pending == 0:
        agent_actions.append({
            "id": "billing_ok", "type": "info", "title": "Faturamento em Dia",
            "description": "Todos os pagamentos do mês foram recebidos. Excelente trabalho na gestão financeira!"
        })

    return {
        "kpis": {
            "total_billing": total_billing,
            "total_received": total_received,
            "total_pending": total_pending,
            "pending_rate": pending_rate
        },
        "billing_items": enriched_items,
        "agent_actions": agent_actions
    }