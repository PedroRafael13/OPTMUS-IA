# api.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import core

app = Flask(__name__)
CORS(app)

database.setup_database()

@app.route("/")
def index():
    return jsonify({"message": "API do RADAR OPTMUS está no ar!"})

# --- CLIENTES E DIAGNÓSTICO ---

@app.route("/api/clientes", methods=['GET'])
def get_clientes():
    try:
        clientes = database.get_all_companies()
        return jsonify(clientes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clientes", methods=['POST'])
def register_cliente():
    data = request.json
    alias = data.get('alias')
    cnpj = data.get('cnpj')

    if not alias or not cnpj:
        return jsonify({"error": "Alias and CNPJ are required"}), 400

    all_data = {}
    receita_result = core.fetch_receita_data(cnpj)
    if receita_result['status'] != 'success':
        return jsonify(receita_result), 404
    all_data['receita'] = receita_result['data']

    serasa_result = core.fetch_credit_bureau_data_mock(cnpj)
    all_data['serasa'] = serasa_result.get('data', {})
    
    ibge_result = core.fetch_ibge_data(all_data['receita'].get('codigo_municipio_ibge'))
    all_data['ibge'] = ibge_result.get('data', {})
    
    new_company_id = database.save_company_data(alias, all_data)
    
    if new_company_id:
        for debt in all_data.get('serasa', {}).get('debts', []):
            database.add_debt(new_company_id, debt['type'], debt['creditor'], debt['balance'], debt['details'])
        return jsonify({"message": "Client registered successfully", "id": new_company_id}), 201
    else:
        return jsonify({"error": "CNPJ already registered or database error"}), 409

@app.route("/api/clientes/<int:company_id>", methods=['DELETE'])
def delete_cliente(company_id):
    if database.delete_company_by_id(company_id):
        return jsonify({"message": "Client deleted successfully"}), 200
    return jsonify({"error": "Client not found or could not be deleted"}), 404

@app.route("/api/diagnostico/<int:company_id>", methods=['GET'])
def get_full_diagnostic(company_id):
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    company['maturity_scores'] = database.get_maturity_scores(company_id)
    return jsonify(company)

# --- MERCADO E ESTRATÉGIA ---

@app.route("/api/mercado/analise/<int:company_id>", methods=['POST'])
def run_market_analysis(company_id):
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    if not company.get('annual_revenue'):
        return jsonify({"error": "Annual revenue is required to run market analysis"}), 400

    analysis_result = core.calculate_market_analysis(company)
    if analysis_result['status'] == 'success':
        data = analysis_result['data']
        database.update_market_data(company_id, data['market_share'], data['market_rank'])
        return jsonify(data), 200
    else:
        return jsonify({"error": analysis_result['message']}), 500

@app.route("/api/recomendacoes/<int:company_id>", methods=['GET'])
def get_recommendations(company_id):
    recs = database.get_recommendations(company_id)
    return jsonify(recs)

@app.route("/api/recomendacoes/<int:company_id>/gerar", methods=['POST'])
def generate_recommendations_route(company_id):
    new_recs = core.generate_recommendations(company_id)
    if new_recs:
        database.save_recommendations(company_id, new_recs)
        return jsonify(new_recs), 201
    return jsonify({"error": "Failed to generate new recommendations"}), 500

# --- FINANCEIRO E DÍVIDAS ---

@app.route("/api/dashboard/general/<int:company_id>", methods=['GET'])
def get_general_dashboard(company_id):
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404
        
    financial_data = database.get_financial_dashboard_data(period_days=30, company_id=company_id)
    contracts = database.get_all_contracts_with_company_info(company_id=company_id)
    revenue_evolution = database.get_monthly_revenue_evolution(company_id=company_id)
    
    prev_revenue = financial_data.get('previous_revenue', 0)
    
    dashboard_summary = {
        "monthly_revenue": financial_data.get('current_revenue', 0),
        "revenue_change_percent": ((financial_data['current_revenue'] / prev_revenue) - 1) * 100 if prev_revenue > 0 else 0,
        "active_contracts": len(contracts),
        "average_ticket": sum(c['monthly_price'] for c in contracts) / len(contracts) if contracts else 0,
        "market_share": company.get('market_share', 0),
        "market_rank": f"#{company.get('market_rank', 'N/A')} em Manaus",
        "revenue_evolution_data": revenue_evolution
    }
    return jsonify(dashboard_summary)

@app.route("/api/financeiro/faturamento/<int:company_id>", methods=['PUT'])
def set_annual_revenue(company_id):
    data = request.json
    revenue = data.get('annual_revenue')
    if revenue is None:
        return jsonify({"error": "annual_revenue is required"}), 400
    database.update_company_revenue(company_id, float(revenue))
    return jsonify({"message": "Annual revenue updated successfully"}), 200

@app.route("/api/financeiro/fluxo-caixa/<int:company_id>", methods=['PUT'])
def set_cash_flow(company_id):
    data = request.json
    cash_flow = data.get('monthly_cash_flow')
    if cash_flow is None:
        return jsonify({"error": "monthly_cash_flow is required"}), 400
    database.update_company_cash_flow(company_id, float(cash_flow))
    return jsonify({"message": "Monthly cash flow updated successfully"}), 200

@app.route("/api/transacoes", methods=['POST'])
def add_transaction():
    data = request.json
    if not all(k in data for k in ['date', 'type', 'amount', 'description']):
        return jsonify({"error": "Missing required fields"}), 400
    
    if database.add_new_transaction(data['date'], data['type'], data['amount'], data['description'], data.get('company_id')):
        return jsonify({"message": "Transaction added successfully"}), 201
    return jsonify({"error": "Failed to add transaction"}), 500

@app.route("/api/debts/<int:company_id>", methods=['GET'])
def get_debt_analysis(company_id):
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404
    
    debts_list = database.get_debts_by_company(company_id)
    analysis = core.generate_debt_analysis(company, debts_list)
    
    total_dividas = sum(d['outstanding_balance'] for d in debts_list)
    total_bancario = sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Bancária')
    total_fornecedor = sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Fornecedor')
    total_protestos = sum(d['outstanding_balance'] for d in debts_list if d['debt_type'] == 'Protesto')
    
    response_data = {
        "totals": {"total_dividas": total_dividas, "total_bancario": total_bancario, "total_fornecedor": total_fornecedor, "total_protestos": total_protestos},
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

# --- CONTRATOS E ADMINISTRAÇÃO ---

@app.route("/api/contratos/cliente/<int:company_id>", methods=['GET'])
def get_contracts(company_id):
    contracts = database.get_all_contracts_with_company_info(company_id=company_id)
    return jsonify(contracts)

@app.route("/api/contratos", methods=['POST'])
def add_contract():
    data = request.json
    if not all(k in data for k in ['company_id', 'service', 'price', 'due_date']):
        return jsonify({"error": "Missing required fields"}), 400
        
    if database.add_new_contract(data['company_id'], data['service'], data['price'], data.get('responsible', ''), data['due_date']):
        return jsonify({"message": "Contract added successfully"}), 201
    return jsonify({"error": "Failed to add contract"}), 500

@app.route("/api/reputacao/reclameaqui/<int:company_id>", methods=['POST'])
def update_ra_data(company_id):
    data = request.json
    slug = data.get('slug')
    if not slug:
        return jsonify({"error": "Reclame Aqui 'slug' is required"}), 400

    result = core.fetch_reclameaqui_data(slug)
    if result['status'] == 'success':
        database.update_company_ra_data(company_id, result['data'])
        return jsonify(result['data']), 200
    return jsonify({"error": result['message']}), 404

# --- ALERTAS E NOTIFICAÇÕES ---

@app.route("/api/alerts/<int:company_id>", methods=['GET'])
def get_alerts(company_id):
    alerts = []
    company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    credit_score = company.get('credit_score', 1000)
    if credit_score < 300:
        alerts.append({
            "id": "score_critico", "title": "Score Serasa Crítico", "priority": "alta", "icon": "⚠️",
            "description": f"Score atual: {credit_score}/1000. Necessário plano urgente de quitação de dívidas."
        })

    expiring_contracts = database.get_expiring_contracts(days_ahead=90, company_id=company_id)
    for contract in expiring_contracts:
        alerts.append({
            "id": f"contract_{contract['id']}", "title": f"Contrato Vencendo: {contract['service_description']}", "priority": "alta", "icon": "📄",
            "description": f"Contrato de R$ {contract['monthly_price']:.2f} vence em {contract['due_date']}. Iniciar negociação para renovação."
        })
    
    return jsonify(alerts)

@app.route("/api/sidebar/notifications/<int:company_id>", methods=['GET'])
def get_sidebar_notifications(company_id):
    alerts_response = get_alerts(company_id)
    if alerts_response.status_code != 200:
        return alerts_response

    alerts = alerts_response.get_json()
    high_priority_alerts = sum(1 for alert in alerts if alert.get('priority') == 'alta')
    
    expiring_contracts = database.get_expiring_contracts(days_ahead=90, company_id=company_id)
    debts = database.get_debts_by_company(company_id=company_id)
    
    notifications = {
        "dashboard": high_priority_alerts,
        "dividas": len(debts),
        "contratos": len(expiring_contracts),
    }
    return jsonify(notifications)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)