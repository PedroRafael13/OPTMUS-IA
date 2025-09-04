# api.py

from flask import Flask, jsonify
from flask_cors import CORS
import database
import core

app = Flask(__name__)
# Habilita o CORS para permitir a comunicação com o frontend
CORS(app)

# Garante que o banco de dados e as tabelas existam ao iniciar
database.setup_database()

@app.route("/")
def index():
    """Rota inicial para verificar se a API está funcionando."""
    return jsonify({"message": "API do RADAR OPTMUS está no ar!"})

@app.route("/api/clientes", methods=['GET'])
def get_clientes():
    """Endpoint para listar todos os clientes cadastrados."""
    try:
        clientes = database.get_all_companies()
        return jsonify(clientes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard/general/<int:company_id>", methods=['GET'])
def get_general_dashboard(company_id):
    """Endpoint que retorna os dados para os cards principais do dashboard."""
    try:
        company = next((c for c in database.get_all_companies() if c['id'] == company_id), None)
        if not company:
            return jsonify({"error": "Company not found"}), 404
            
        financial_data = database.get_financial_dashboard_data(company_id=company_id)
        contracts = database.get_all_contracts_with_company_info(company_id=company_id)
        revenue_evolution = database.get_monthly_revenue_evolution(company_id=company_id)
        
        dashboard_summary = {
            "monthly_revenue": financial_data.get('current_revenue', 0),
            "revenue_change_percent": ((financial_data['current_revenue'] / financial_data.get('previous_revenue', 1)) - 1) * 100 if financial_data.get('previous_revenue', 0) > 0 else 0,
            "active_contracts": len(contracts),
            "average_ticket": sum(c['monthly_price'] for c in contracts) / len(contracts) if contracts else 0,
            "market_share": company.get('market_share', 0),
            "market_rank": f"#{company.get('market_rank', 'N/A')} em Manaus",
            "revenue_evolution_data": revenue_evolution
        }
        return jsonify(dashboard_summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts/<int:company_id>", methods=['GET'])
def get_alerts(company_id):
    """Endpoint que analisa e gera uma lista de alertas e insights."""
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/debts/<int:company_id>", methods=['GET'])
def get_debt_analysis(company_id):
    """Endpoint que retorna os dados quantitativos e qualitativos das dívidas."""
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Adicione este novo endpoint ao seu arquivo api.py

@app.route("/api/sidebar/notifications/<int:company_id>", methods=['GET'])
def get_sidebar_notifications(company_id):
    """Endpoint que calcula e retorna os números para as notificações da sidebar."""
    try:
        # Reutiliza a lógica do endpoint de alertas para contar itens de alta prioridade
        alerts = get_alerts(company_id).get_json() # get_alerts já retorna um jsonify object
        high_priority_alerts = sum(1 for alert in alerts if alert.get('priority') == 'alta')
        
        # Reutiliza a lógica de contratos para contar os que estão perto de vencer
        expiring_contracts = database.get_expiring_contracts(days_ahead=90, company_id=company_id)
        
        # Busca o total de dívidas
        debts = database.get_debts_by_company(company_id=company_id)
        
        notifications = {
            "dashboard": high_priority_alerts,
            "dividas": len(debts),
            "contratos": len(expiring_contracts),
            # Adicione outras contagens aqui conforme necessário
        }
        return jsonify(notifications)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Executa o servidor quando o script é chamado
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)