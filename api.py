# api.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import core
from datetime import datetime
import csv
import io

app = Flask(__name__)
CORS(app)

database.setup_database()

@app.route("/")
def index():
    """Rota inicial para verificar se a API está funcionando."""
    return jsonify({"message": "API do RADAR OPTMUS está no ar!"})

# --- ANÁLISE DE CONCORRENTES E CHAT IA ---

@app.route("/api/analysis/chat", methods=['POST'])
def chat_with_ai():
    """Endpoint para conversas diretas com as IAs."""
    data = request.json
    prompt = data.get('prompt')
    model_choice = data.get('model', 'gemini')

    if not prompt:
        return jsonify({"error": "O prompt não pode estar vazio"}), 400

    full_prompt = f"Pergunta do usuário: {prompt}. Responda de forma concisa e direta como um assistente de negócios."

    try:
        if model_choice == 'gpt':
            response_text = core.call_gpt_api_raw(full_prompt)
        else:
            response_text = core.call_gemini_api_raw(full_prompt)
        
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/competitors/<int:company_id>", methods=['GET'])
def get_competitors_route(company_id):
    competitors = database.get_competitors(company_id)
    return jsonify(competitors)

@app.route("/api/competitors/<int:company_id>", methods=['POST'])
def add_competitor_route(company_id):
    data = request.json
    competitor_id = database.add_competitor(
        company_id, data.get('name'), data.get('location'), data.get('revenue')
    )
    return jsonify({"id": competitor_id, **data}), 201

@app.route("/api/competitors/delete/<int:competitor_id>", methods=['DELETE'])
def delete_competitor_route(competitor_id):
    if database.delete_competitor(competitor_id):
        return jsonify({"message": "Concorrente excluído com sucesso"}), 200
    return jsonify({"error": "Concorrente não encontrado"}), 404

@app.route("/api/competitors/<int:company_id>/upload_csv", methods=['POST'])
def upload_csv_route(company_id):
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo vazio"}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input) # Pula o cabeçalho
        
        for row in csv_input:
            if len(row) == 3:
                name, location, revenue_str = row
                try:
                    revenue = float(revenue_str)
                    database.add_competitor(company_id, name, location, revenue)
                except ValueError:
                    print(f"Skipping row with invalid revenue: {row}")
                    continue
        return jsonify({"message": "CSV importado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao processar o CSV: {str(e)}"}), 500

# --- CLIENTES E DIAGNÓSTICO ---

@app.route("/api/clientes", methods=['GET'])
def get_clientes():
    try:
        clientes = database.get_all_companies()
        response = jsonify(clientes)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clientes", methods=['POST'])
def register_cliente():
    data = request.json
    alias = data.get('alias')
    cnpj = data.get('cnpj')
    if not alias or not cnpj: return jsonify({"error": "Alias e CNPJ são obrigatórios"}), 400
    all_data = {}
    receita_result = core.fetch_receita_data(cnpj)
    if receita_result['status'] != 'success': return jsonify(receita_result), 404
    all_data['receita'] = receita_result['data']
    serasa_result = core.fetch_credit_bureau_data_mock(cnpj)
    all_data['serasa'] = serasa_result.get('data', {})
    ibge_result = core.fetch_ibge_data(all_data['receita'].get('codigo_municipio_ibge'))
    all_data['ibge'] = ibge_result.get('data', {})
    new_company_id = database.save_company_data(alias, all_data)
    if new_company_id:
        for debt in all_data.get('serasa', {}).get('debts', []):
            database.add_debt(new_company_id, debt['type'], debt['creditor'], debt['balance'], debt['details'])
        return jsonify({"message": "Cliente cadastrado com sucesso", "id": new_company_id}), 201
    else:
        return jsonify({"error": "CNPJ já cadastrado ou erro no banco de dados"}), 409

@app.route("/api/clientes/<int:company_id>", methods=['DELETE'])
def delete_cliente(company_id):
    if database.delete_company_by_id(company_id):
        return jsonify({"message": "Cliente excluído com sucesso"}), 200
    return jsonify({"error": "Cliente não encontrado"}), 404

@app.route("/api/recomendacoes/<int:company_id>", methods=['GET'])
def get_recommendations(company_id):
    recs = database.get_recommendations(company_id)
    return jsonify(recs)

@app.route("/api/recomendacoes/<int:company_id>/gerar", methods=['POST'])
def generate_recommendations_route(company_id):
    data = request.json
    focus_area = data.get('focus_area')
    objective = data.get('objective')
    if not all([focus_area, objective]):
        return jsonify({"error": "Foco e objetivo são obrigatórios"}), 400
    new_recs = core.generate_recommendations(company_id, focus_area, objective)
    if new_recs:
        database.save_recommendations(company_id, new_recs)
        return jsonify(new_recs), 201
    return jsonify({"error": "Falha ao gerar novas recomendações"}), 500

@app.route("/api/recomendacoes/<int:company_id>", methods=['DELETE'])
def clear_recommendations_route(company_id):
    if database.delete_recommendations(company_id):
        return jsonify({"message": "Recomendações excluídas com sucesso"}), 200
    else:
        return jsonify({"error": "Falha ao excluir recomendações"}), 500

# --- DASHBOARDS E FINANCEIRO ---

@app.route("/api/dashboard/general/<int:company_id>", methods=['GET'])
def get_general_dashboard(company_id):
    """
    Busca e analisa os dados de um cliente para retornar a visão completa do agente
    para o Dashboard Geral.
    """
    try:
        analysis_data = core.generate_general_dashboard_analysis(company_id)
        return jsonify(analysis_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Erro ao gerar dashboard geral: {e}")
        return jsonify({"error": "Falha ao gerar dados do dashboard."}), 500

@app.route("/api/financeiro/dashboard/<int:company_id>", methods=['GET'])
def get_financial_dashboard(company_id):
    try:
        days_to_project = request.args.get('days', 180, type=int)
        performance_data = database.get_financial_dashboard_data(period_days=30, company_id=company_id)
        receita_bruta = performance_data.get('current_revenue', 0.0)
        despesas_totais = performance_data.get('current_expenses', 0.0)
        margem_liquida = receita_bruta - despesas_totais
        kpis = {"receita_bruta": receita_bruta, "despesas_totais": despesas_totais, "margem_liquida": margem_liquida, "fluxo_liquido": margem_liquida}
        contracts = database.get_all_contracts_with_company_info(company_id=company_id)
        active_contracts_value = sum(c['monthly_price'] for c in contracts)
        qualitative_analysis = core.generate_financial_analysis(performance_data, active_contracts_value)
        projection_chart_data = core.generate_cash_flow_projection_chart_data(company_id, contracts, days=days_to_project)
        dashboard_data = {"kpis": kpis, "qualitative_analysis": qualitative_analysis, "projection_chart_data": projection_chart_data}
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MODIFICADO: Esta rota agora é o "endpoint inteligente" do agente de faturamento
@app.route("/api/financeiro/billing/<int:company_id>", methods=['GET'])
def get_monthly_billing(company_id):
    """
    Busca o faturamento mensal de um cliente e retorna uma análise completa do
    agente de cobrança, com KPIs, status de inadimplência e ações sugeridas.
    """
    try:
        # Chama a nova função do core.py que faz toda a análise
        analysis_data = core.analyze_billing_for_agent(company_id)
        return jsonify(analysis_data)
    except Exception as e:
        print(f"Erro ao gerar análise de faturamento: {e}")
        return jsonify({"error": "Falha ao gerar análise de faturamento."}), 500

@app.route("/api/financeiro/billing/pay", methods=['POST'])
def pay_monthly_billing():
    data = request.json
    contract_id, company_id, amount = data.get('contract_id'), data.get('company_id'), data.get('amount')
    if not all([contract_id, company_id, amount]): return jsonify({"error": "Dados insuficientes"}), 400
    current_month = datetime.now().strftime('%Y-%m')
    success = database.mark_contract_as_paid(contract_id, company_id, amount, current_month)
    if success: return jsonify({"message": "Pagamento registrado com sucesso"}), 201
    else: return jsonify({"error": "Falha ao registrar pagamento, talvez já tenha sido pago este mês"}), 500

@app.route("/api/financeiro/faturamento/<int:company_id>", methods=['PUT'])
def set_annual_revenue(company_id):
    data = request.json
    revenue = data.get('annual_revenue')
    if revenue is None: return jsonify({"error": "annual_revenue is required"}), 400
    database.update_company_revenue(company_id, float(revenue))
    return jsonify({"message": "Faturamento anual atualizado com sucesso"}), 200

@app.route("/api/financeiro/fluxo-caixa/<int:company_id>", methods=['PUT'])
def set_cash_flow(company_id):
    data = request.json
    cash_flow = data.get('monthly_cash_flow')
    if cash_flow is None: return jsonify({"error": "monthly_cash_flow is required"}), 400
    database.update_company_cash_flow(company_id, float(cash_flow))
    return jsonify({"message": "Fluxo de caixa mensal atualizado com sucesso"}), 200

@app.route("/api/transacoes", methods=['POST'])
def add_transaction():
    data = request.json
    if not all(k in data for k in ['date', 'type', 'amount', 'description']):
        return jsonify({"error": "Missing required fields"}), 400
    database.add_new_transaction(data['date'], data['type'], data['amount'], data['description'], data.get('company_id'), data.get('contract_id'))
    return jsonify({"message": "Transaction added successfully"}), 201

@app.route("/api/debts/<int:company_id>", methods=['GET'])
def get_debt_analysis(company_id):
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company: return jsonify({"error": "Company not found"}), 404
    debts_list = database.get_debts_by_company(company_id)
    analysis = core.generate_debt_analysis(company, debts_list)
    response_data = {
        "totals": {
            "total_dividas": sum(d['outstanding_balance'] for d in debts_list),
            "total_bancario": sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Bancária'),
            "total_fornecedor": sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Fornecedor'),
            "total_protestos": sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Protesto')
        },
        "strategic_analysis": analysis,
        "details": debts_list
    }
    return jsonify(response_data)

@app.route("/api/debts/<int:company_id>", methods=['POST'])
def add_manual_debt(company_id):
    data = request.json
    if not all(k in data for k in ['debt_type', 'creditor', 'balance']):
        return jsonify({"error": "Missing required fields"}), 400
    database.add_debt(company_id, data['debt_type'], data['creditor'], data['balance'], data.get('details', ''))
    return jsonify({"message": "Debt added successfully"}), 201

# --- CONTRATOS, ALERTAS E NOTIFICAÇÕES ---

@app.route("/api/contratos/cliente/<int:company_id>", methods=['GET'])
def get_contracts(company_id):
    """
    Busca os contratos de um cliente e retorna uma análise completa do agente.
    """
    try:
        analysis_data = core.get_contract_analysis_for_company(company_id)
        return jsonify(analysis_data)
    except Exception as e:
        print(f"Erro ao gerar análise de contratos: {e}")
        return jsonify({"error": "Falha ao gerar análise de contratos."}), 500

@app.route("/api/contratos", methods=['POST'])
def add_contract():
    data = request.json
    if not all(k in data for k in ['company_id', 'service', 'price', 'due_date']):
        return jsonify({"error": "Missing required fields"}), 400
    if database.add_new_contract(data['company_id'], data['service'], data['price'], data.get('responsible', ''), data['due_date']):
        return jsonify({"message": "Contract added successfully"}), 201
    return jsonify({"error": "Failed to add contract"}), 500

@app.route("/api/alerts/<int:company_id>", methods=['GET'])
def get_alerts(company_id):
    alerts = []
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company: return jsonify({"error": "Company not found"}), 404
    credit_score = company.get('credit_score', 1000)
    if credit_score < 300:
        alerts.append({"id": "score_critico", "title": "Score Serasa Crítico", "priority": "alta", "icon": "⚠️", "description": f"Score atual: {credit_score}/1000. Plano de quitação de dívidas urgente."})
    expiring_contracts = database.get_expiring_contracts(days_ahead=90, company_id=company_id)
    for contract in expiring_contracts:
        alerts.append({"id": f"contract_{contract['id']}", "title": f"Contrato Vencendo: {contract['service_description']}", "priority": "alta", "icon": "📄", "description": f"Contrato de R$ {contract['monthly_price']:.2f} vence em {contract['due_date']}. Iniciar negociação."})
    return jsonify(alerts)

@app.route("/api/sidebar/notifications/<int:company_id>", methods=['GET'])
def get_sidebar_notifications(company_id):
    alerts_response = get_alerts(company_id)
    if alerts_response.status_code != 200: return alerts_response
    alerts = alerts_response.get_json()
    high_priority_alerts = sum(1 for alert in alerts if alert.get('priority') == 'alta')
    expiring_contracts = database.get_expiring_contracts(days_ahead=90, company_id=company_id)
    debts = database.get_debts_by_company(company_id=company_id)
    notifications = {"dashboard": high_priority_alerts, "dividas": len(debts), "contratos": len(expiring_contracts)}
    return jsonify(notifications)

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)