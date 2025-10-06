# database.py

"""
Módulo de gerenciamento do banco de dados para o RADAR OPTMUS.
Contém todas as funções que executam queries SQL.
"""

import sqlite3
from config import DB_FILE
from datetime import datetime, timedelta

def setup_database():
    """Garante que o banco de dados e todas as tabelas/colunas estejam atualizados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Tabela principal de empresas (clientes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internal_alias TEXT NOT NULL,
        cnpj TEXT UNIQUE NOT NULL,
        razao_social TEXT,
        nome_fantasia TEXT,
        cnae_principal_descricao TEXT,
        capital_social REAL,
        google_rating REAL,
        credit_score INTEGER,
        financial_pendencies TEXT,
        municipality_population INTEGER,
        ra_reputation_score REAL,
        ra_status TEXT,
        ra_response_rate REAL,
        monthly_cash_flow REAL,
        annual_revenue REAL,
        market_share REAL,
        market_rank INTEGER,
        average_ticket REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Adiciona colunas se não existirem para garantir compatibilidade
    columns_to_add = {
        "monthly_cash_flow": "REAL",
        "cnae_principal_descricao": "TEXT",
        "annual_revenue": "REAL",
        "market_share": "REAL",
        "market_rank": "INTEGER",
        "average_ticket": "REAL"
    }
    for column, col_type in columns_to_add.items():
        try:
            cursor.execute(f"ALTER TABLE companies ADD COLUMN {column} {col_type};")
        except sqlite3.OperationalError:
            pass # Coluna já existe

    # Tabela de maturidade
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maturity_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        area TEXT NOT NULL,
        score INTEGER NOT NULL,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_id, area),
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );
    """)

    # Tabela de contratos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        service_description TEXT NOT NULL,
        monthly_price REAL NOT NULL,
        responsible_person TEXT,
        due_date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );
    """)

    # Tabela de transações financeiras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TEXT NOT NULL,
        transaction_type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        company_id INTEGER,
        contract_id INTEGER,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE SET NULL,
        FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE SET NULL
    );
    """)

    # Tabela de Dívidas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS debts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        debt_type TEXT NOT NULL, -- 'Bancária', 'Fornecedor', 'Protesto'
        creditor_name TEXT NOT NULL,
        outstanding_balance REAL NOT NULL,
        details TEXT,
        due_date TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );
    """)

    # Tabela de Recomendações da IA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        priority TEXT NOT NULL, -- 'alta', 'media', 'baixa'
        description TEXT,
        investment REAL,
        roi REAL, -- Em porcentagem
        timeline INTEGER, -- Em meses
        generated_by TEXT, -- 'GPT-4', 'Gemini-Pro'
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );
    """)

    # Tabela de pagamentos mensais de contratos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monthly_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER NOT NULL,
        payment_month TEXT NOT NULL, -- Formato 'YYYY-MM'
        payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
        transaction_id INTEGER NOT NULL,
        UNIQUE(contract_id, payment_month),
        FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE CASCADE,
        FOREIGN KEY (transaction_id) REFERENCES financial_transactions (id) ON DELETE CASCADE
    );
    """)

    # Tabela de Concorrentes para Análise de Mercado
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        location TEXT,
        revenue REAL,
        strengths TEXT,
        weaknesses TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

def save_company_data(internal_alias, all_data):
    """Salva os dados iniciais de uma empresa, incluindo dados de crédito simulados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    p = {
        "internal_alias": internal_alias,
        "cnpj": all_data.get('receita', {}).get('cnpj'),
        "razao_social": all_data.get('receita', {}).get('razao_social'),
        "nome_fantasia": all_data.get('receita', {}).get('nome_fantasia'),
        "cnae_principal_descricao": all_data.get('receita', {}).get('cnae_fiscal_descricao'),
        "capital_social": all_data.get('receita', {}).get('capital_social'),
        "google_rating": all_data.get('google', {}).get('google_rating'),
        "credit_score": all_data.get('serasa', {}).get('credit_score'),
        "financial_pendencies": all_data.get('serasa', {}).get('financial_pendencies'),
        "municipality_population": all_data.get('ibge', {}).get('municipality_population'),
    }
    try:
        cursor.execute("""
            INSERT INTO companies (internal_alias, cnpj, razao_social, nome_fantasia, cnae_principal_descricao, capital_social,
            google_rating, credit_score, financial_pendencies, municipality_population)
            VALUES (:internal_alias, :cnpj, :razao_social, :nome_fantasia, :cnae_principal_descricao, :capital_social,
            :google_rating, :credit_score, :financial_pendencies, :municipality_population)
        """, p)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def save_maturity_scores(company_id, scores):
    """Salva ou atualiza os scores de maturidade de uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for area, score in scores.items():
        cursor.execute("INSERT INTO maturity_analysis (company_id, area, score) VALUES (?, ?, ?) ON CONFLICT(company_id, area) DO UPDATE SET score = excluded.score", (company_id, area, score))
    conn.commit()
    conn.close()

def save_recommendations(company_id, recommendations):
    """Salva uma lista de recomendações no banco de dados, limpando as antigas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE company_id = ?", (company_id,))
    
    for rec in recommendations:
        cursor.execute("""
            INSERT INTO recommendations (company_id, title, priority, description, investment, roi, timeline, generated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, rec.get('title'), rec.get('priority'), rec.get('description'), rec.get('investment'), rec.get('roi'), rec.get('timeline'), rec.get('generated_by')))
    conn.commit()
    conn.close()

def update_company_ra_data(company_id, ra_data):
    """Atualiza os dados do Reclame Aqui para uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE companies SET ra_reputation_score = ?, ra_status = ?, ra_response_rate = ? WHERE id = ?", (ra_data.get('ra_reputation_score'), ra_data.get('ra_status'), ra_data.get('ra_response_rate'), company_id))
    conn.commit()
    conn.close()

def update_company_cash_flow(company_id, cash_flow):
    """Atualiza o fluxo de caixa mensal de uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE companies SET monthly_cash_flow = ? WHERE id = ?", (cash_flow, company_id))
    conn.commit()
    conn.close()

def update_company_revenue(company_id, revenue):
    """Atualiza o faturamento anual de um cliente."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE companies SET annual_revenue = ? WHERE id = ?", (revenue, company_id))
    conn.commit()
    conn.close()
    
def update_company_pricing(company_id, ticket):
    """Atualiza o preço/ticket médio de um cliente."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE companies SET average_ticket = ? WHERE id = ?", (ticket, company_id))
    conn.commit()
    conn.close()

def update_market_data(company_id, share, rank):
    """Salva os dados de market share e ranking calculados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE companies SET market_share = ?, market_rank = ? WHERE id = ?", (share, rank, company_id))
    conn.commit()
    conn.close()

def add_new_contract(company_id, service, price, responsible, due_date_str):
    """Adiciona um novo contrato."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO contracts (company_id, service_description, monthly_price, responsible_person, due_date) VALUES (?, ?, ?, ?, ?)", (company_id, service, price, responsible, due_date_str))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def add_new_transaction(trans_date, trans_type, amount, description, company_id=None, contract_id=None):
    """Adiciona uma nova transação financeira."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO financial_transactions (transaction_date, transaction_type, amount, description, company_id, contract_id) VALUES (?, ?, ?, ?, ?, ?)", (trans_date, trans_type, amount, description, company_id, contract_id))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        return None
    finally:
        conn.close()

def add_debt(company_id, debt_type, creditor, balance, details="", due_date=None):
    """Adiciona um novo registro de dívida."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO debts (company_id, debt_type, creditor_name, outstanding_balance, details, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, debt_type, creditor, balance, details, due_date))
        conn.commit()
    finally:
        conn.close()

def get_all_companies():
    """Busca todas as empresas cadastradas."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies ORDER BY internal_alias;")
    companies = [dict(c) for c in cursor.fetchall()]
    conn.close()
    return companies

def get_maturity_scores(company_id):
    """Busca os scores de maturidade de uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT area, score FROM maturity_analysis WHERE company_id = ?", (company_id,))
    scores = {row['area']: row['score'] for row in cursor.fetchall()}
    conn.close()
    return scores

def get_recommendations(company_id):
    """Busca as recomendações salvas para uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE company_id = ? ORDER BY CASE priority WHEN 'alta' THEN 1 WHEN 'media' THEN 2 WHEN 'baixa' THEN 3 ELSE 4 END, roi DESC", (company_id,))
    recommendations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return recommendations

def get_all_contracts_with_company_info(company_id=None):
    """Busca todos os contratos, com filtro opcional por cliente."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT c.id as contract_id, co.id as company_id, co.internal_alias as company_name, c.service_description, c.monthly_price, c.responsible_person, c.due_date FROM contracts c JOIN companies co ON c.company_id = co.id"
    params = []
    if company_id:
        query += " WHERE c.company_id = ?"
        params.append(company_id)
    query += " ORDER BY c.due_date;"
    cursor.execute(query, params)
    contracts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contracts

def get_financial_summary(company_id=None):
    """Busca todas as transações (ou filtra) e calcula o balanço."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    params = []
    where_clause = ""
    if company_id:
        where_clause = " WHERE company_id = ?"
        params.append(company_id)
    cursor.execute(f"SELECT transaction_type, SUM(amount) as total FROM financial_transactions {where_clause} GROUP BY transaction_type;", params)
    totals = {row['transaction_type']: row['total'] for row in cursor.fetchall()}
    transactions_query = f"SELECT t.id, t.transaction_date, t.transaction_type, t.amount, t.description, c.internal_alias as company_name FROM financial_transactions t LEFT JOIN companies c ON t.company_id = c.id {where_clause.replace('company_id', 't.company_id')} ORDER BY t.transaction_date DESC;"
    cursor.execute(transactions_query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"total_in": totals.get('entrada', 0.0), "total_out": totals.get('saida', 0.0), "balance": totals.get('entrada', 0.0) - totals.get('saida', 0.0), "transactions": transactions}

def get_financial_dashboard_data(period_days=30, company_id=None):
    """Busca e calcula os dados para o Dashboard, com filtro opcional por cliente."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    end_date = datetime.now()
    start_date_current = end_date - timedelta(days=period_days)
    end_date_previous = start_date_current
    start_date_previous = end_date_previous - timedelta(days=period_days)

    base_query = """
        SELECT
            transaction_type,
            SUM(CASE WHEN transaction_date BETWEEN ? AND ? THEN amount ELSE 0 END) as current_period_total,
            SUM(CASE WHEN transaction_date BETWEEN ? AND ? THEN amount ELSE 0 END) as previous_period_total
        FROM financial_transactions
    """
    
    params = [
        start_date_current.strftime('%Y-%m-%d'), 
        end_date.strftime('%Y-%m-%d'), 
        start_date_previous.strftime('%Y-%m-%d'), 
        end_date_previous.strftime('%Y-%m-%d')
    ]

    if company_id:
        query = base_query + " WHERE company_id = ? GROUP BY transaction_type;"
        params.append(company_id)
    else:
        query = base_query + " GROUP BY transaction_type;"

    cursor.execute(query, params)
    
    data = {'current_revenue': 0.0, 'previous_revenue': 0.0, 'current_expenses': 0.0, 'previous_expenses': 0.0}
    for row in cursor.fetchall():
        if row['transaction_type'] == 'entrada':
            data['current_revenue'] = row['current_period_total'] or 0.0
            data['previous_revenue'] = row['previous_period_total'] or 0.0
        elif row['transaction_type'] == 'saida':
            data['current_expenses'] = row['current_period_total'] or 0.0
            data['previous_expenses'] = row['previous_period_total'] or 0.0
            
    conn.close()
    return data

def get_debts_by_company(company_id):
    """Busca todas as dívidas de uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT debt_type, creditor_name, outstanding_balance, details, due_date FROM debts WHERE company_id = ? ORDER BY debt_type", (company_id,))
    debts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return debts

def delete_company_by_id(company_id):
    """Exclui uma empresa e todos os seus dados associados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    return deleted_rows > 0

def get_monthly_revenue_evolution(company_id=None):
    """Busca a evolução da receita (entradas) dos últimos 6 meses."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-01')

    query = """
        SELECT 
            strftime('%Y-%m', transaction_date) as month,
            SUM(amount) as total_revenue
        FROM financial_transactions
        WHERE transaction_type = 'entrada' AND transaction_date >= ?
    """
    params = [six_months_ago]

    if company_id:
        query += " AND company_id = ?"
        params.append(company_id)

    query += " GROUP BY month ORDER BY month;"

    cursor.execute(query, params)

    db_results = {row[0]: row[1] for row in cursor.fetchall()}
    
    evolution_data = []
    for i in range(5, -1, -1):
        date_obj = datetime.now() - timedelta(days=30*i)
        month_key = date_obj.strftime('%Y-%m')
        month_name = date_obj.strftime('%b')
        evolution_data.append({
            "name": month_name,
            "Receita": db_results.get(month_key, 0)
        })

    conn.close()
    return evolution_data

def get_expiring_contracts(days_ahead=90, company_id=None):
    """Busca contratos que irão vencer nos próximos 'days_ahead' dias."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)
    
    query = """
        SELECT c.id, c.service_description, c.monthly_price, c.due_date
        FROM contracts c
        WHERE c.due_date BETWEEN ? AND ?
    """
    params = [today.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]

    if company_id:
        query += " AND c.company_id = ?"
        params.append(company_id)
    
    cursor.execute(query, params)
    contracts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contracts

def get_contracts_for_billing(month_str, company_id=None):
    """Busca contratos ativos e verifica se já foram pagos no mês especificado."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT
            c.id as contract_id,
            co.id as company_id,
            co.internal_alias as company_name,
            c.service_description,
            c.monthly_price,
            CASE
                WHEN p.id IS NOT NULL THEN 1
                ELSE 0
            END as is_paid
        FROM contracts c
        JOIN companies co ON c.company_id = co.id
        LEFT JOIN monthly_payments p ON c.id = p.contract_id AND p.payment_month = ?
    """
    params = [month_str]

    if company_id:
        query += " WHERE c.company_id = ?"
        params.append(company_id)

    query += " ORDER BY co.internal_alias, c.service_description;"
    
    cursor.execute(query, params)
    contracts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contracts

def mark_contract_as_paid(contract_id, company_id, amount, month_str):
    """Registra uma transação de entrada e marca o contrato como pago para o mês."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        transaction_date = datetime.now().strftime('%Y-%m-%d')
        description = f"Pagamento do contrato {contract_id} referente ao mês {month_str}"
        
        cursor.execute(
            "INSERT INTO financial_transactions (transaction_date, transaction_type, amount, description, company_id, contract_id) VALUES (?, ?, ?, ?, ?, ?)",
            (transaction_date, 'entrada', amount, description, company_id, contract_id)
        )
        transaction_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO monthly_payments (contract_id, payment_month, transaction_id) VALUES (?, ?, ?)",
            (contract_id, month_str, transaction_id)
        )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_recommendations(company_id):
    """Exclui todas as recomendações para uma empresa específica."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM recommendations WHERE company_id = ?", (company_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def get_competitors(company_id):
    """Busca todos os concorrentes de uma empresa."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitors WHERE company_id = ? ORDER BY revenue DESC", (company_id,))
    competitors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return competitors

def add_competitor(company_id, name, location, revenue):
    """Adiciona um novo concorrente."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO competitors (company_id, name, location, revenue) VALUES (?, ?, ?, ?)",
            (company_id, name, location, revenue)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def delete_competitor(competitor_id):
    """Exclui um concorrente pelo seu ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM competitors WHERE id = ?", (competitor_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    return deleted_rows > 0