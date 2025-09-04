# ui.py

"""
Módulo de interface com o usuário (UI) para o RADAR OPTMUS.
Contém todas as funções que imprimem na tela e recebem input do usuário.
"""

import os
import time
from datetime import datetime, timedelta
import json
import database
import core

def clear_screen():
    """Limpa a tela do console."""
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_register_company():
    """Gerencia o fluxo de cadastro de um novo cliente."""
    clear_screen()
    print("--- CADASTRAR NOVO CLIENTE ---")
    alias = input("Digite um nome de identificação para este cliente: ")
    cnpj = input("Digite o CNPJ do cliente: ")
    
    all_data = {}
    
    print("\n1/4 - Buscando dados na Receita Federal...")
    receita_result = core.fetch_receita_data(cnpj)
    if receita_result['status'] != 'success':
        print(f"ERRO: {receita_result['message']}"); input("\nPressione Enter para voltar..."); return
    all_data['receita'] = receita_result['data']
    print(" -> Sucesso.")

    print("2/4 - Consultando Bureau de Crédito (SIMULAÇÃO)...")
    serasa_result = core.fetch_credit_bureau_data_mock(cnpj)
    all_data['serasa'] = serasa_result.get('data', {})
    print(" -> Sucesso.")
    
    print("3/4 - Buscando dados demográficos no IBGE...")
    ibge_result = core.fetch_ibge_data(all_data['receita'].get('codigo_municipio_ibge'))
    all_data['ibge'] = ibge_result.get('data', {})
    print(f" -> {ibge_result['message'] if ibge_result['status'] != 'success' else 'Sucesso.'}")
    
    print("4/4 - Salvando dados consolidados...")
    if database.save_company_data(alias, all_data):
        print(f"\nSUCESSO: Cliente '{all_data['receita']['razao_social']}' cadastrado.")
        
        companies = database.get_all_companies()
        new_company_id = next((c['id'] for c in companies if c['cnpj'] == all_data['receita']['cnpj']), None)
        
        if new_company_id:
            for debt in all_data.get('serasa', {}).get('debts', []):
                database.add_debt(new_company_id, debt['type'], debt['creditor'], debt['balance'], debt['details'])
    else:
        print("\nERRO: CNPJ já cadastrado.")
    input("\nPressione Enter para voltar ao menu...")

def view_full_diagnostic():
    """Exibe um relatório consolidado de todos os clientes."""
    clear_screen()
    print("--- DIAGNÓSTICO GERAL ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input("\nPressione Enter para voltar..."); return
        
    for company in companies:
        alias = company.get('internal_alias', '[SEM APELIDO]').upper()
        razao_social = company.get('razao_social', '[SEM RAZÃO SOCIAL]')
        print(f"\n--- {alias} | {razao_social} ---")
        
        maturity_scores = database.get_maturity_scores(company['id'])
        print("\n  >> Maturidade Operacional (Interno)")
        if maturity_scores:
            for area in core.QUESTIONS.keys():
                score = maturity_scores.get(area)
                print(f"  - {area}: {score}/100" if score is not None else f"  - {area}: (Não analisado)")
        else:
            print("  - Análise de maturidade ainda não foi realizada.")
        
        print("\n  >> Reputação e Mercado (Externo)")
        print(f"  - Google: Nota {company.get('google_rating', 'N/A')}")
        print(f"  - Reclame Aqui: Nota {company.get('ra_reputation_score', 'N/A')} ({company.get('ra_status', 'N/A')})")
        print(f"  - População do Município: {company.get('municipality_population', 'N/A')}")
        
        print("\n  >> Saúde Financeira (SIMULADO)")
        print(f"  - Score de Crédito: {company.get('credit_score', 'N/A')}")
        print("  - Para ver o detalhe das dívidas, acesse a 'Análise de Dívidas'.")
        print("-" * 50)
            
    input("\nPressione Enter para voltar ao menu...")

def handle_maturity_analysis():
    """Gerencia o fluxo para iniciar a análise de maturidade."""
    clear_screen()
    print("--- SELECIONE O CLIENTE PARA ANÁLISE ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
        
    for company in companies:
        print(f"ID: {company['id']} | Identificação: {company['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente para analisar: "))
        if any(c['id'] == choice_id for c in companies):
            scores = core.run_maturity_questionnaire(choice_id)
            database.save_maturity_scores(choice_id, scores)
            print("\nAnálise de maturidade concluída e salva!")
            input("Pressione Enter para continuar...")
        else:
            print("ID inválido."); time.sleep(2)
    except ValueError:
        print("Entrada inválida."); time.sleep(2)

def handle_add_contract():
    """Gerencia o fluxo para adicionar um novo contrato."""
    clear_screen()
    print("--- ADICIONAR NOVO CONTRATO ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente para este contrato: "))
        if not any(c['id'] == choice_id for c in companies):
            print("ID de cliente inválido."); time.sleep(2); return
        service = input("Descrição do Serviço (ex: Portaria 24h): ")
        price = float(input("Preço Mensal (ex: 4500.00): "))
        responsible = input("Responsável pelo contrato (ex: João Silva): ")
        while True:
            due_date_str = input("Data de Vencimento (formato AAAA-MM-DD): ")
            try:
                datetime.strptime(due_date_str, '%Y-%m-%d'); break
            except ValueError:
                print("Formato de data inválido.")
        if database.add_new_contract(choice_id, service, price, responsible, due_date_str):
            print("\nContrato adicionado com sucesso!")
        else:
            print("\nFalha ao adicionar o contrato.")
    except ValueError:
        print("Entrada inválida."); time.sleep(2)
    input("\nPressione Enter para voltar ao menu...")

def view_contracts():
    """Exibe uma lista de todos os contratos com status calculado."""
    clear_screen()
    print("--- GESTÃO DE CONTRATOS ---")
    contracts = database.get_all_contracts_with_company_info()
    if not contracts:
        print("Nenhum contrato cadastrado.")
    else:
        print(f"{'ID':<4} {'Cliente':<20} {'Serviço':<25} {'Preço Mensal':<15} {'Vencimento':<12} {'Status':<15}")
        print("-" * 95)
        today = datetime.now().date()
        warning_days = today + timedelta(days=30)
        for contract in contracts:
            due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
            status = "Vencido" if due_date < today else "Perto de Vencer" if due_date <= warning_days else "Ativo"
            print(f"{contract['contract_id']:<4} {contract['company_name']:<20} {contract['service_description']:<25} R$ {contract['monthly_price']:<12.2f} {contract['due_date']:<12} {status:<15}")
    input("\nPressione Enter para voltar ao menu...")

def handle_add_transaction():
    """Gerencia o fluxo para registrar uma nova transação."""
    clear_screen()
    print("--- REGISTRAR NOVA TRANSAÇÃO ---")
    while True:
        trans_type_choice = input("Qual o tipo de transação? (1 - Entrada, 2 - Saída): ")
        if trans_type_choice == '1': trans_type = 'entrada'; break
        elif trans_type_choice == '2': trans_type = 'saida'; break
        else: print("Opção inválida.")
    try:
        amount = float(input("Digite o valor (ex: 150.75): "))
        description = input("Descrição (ex: Pagamento de aluguel): ")
        while True:
            trans_date_str = input(f"Data da transação (AAAA-MM-DD) [Padrão: Hoje]: ") or datetime.now().strftime('%Y-%m-%d')
            try:
                datetime.strptime(trans_date_str, '%Y-%m-%d'); break
            except ValueError:
                print("Formato de data inválido.")
        company_id = None
        if input("Deseja vincular a um cliente? (S/N): ").upper() == 'S':
            companies = database.get_all_companies()
            if companies:
                for company in companies:
                    print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
                choice_id = int(input("Digite o ID do cliente: "))
                if any(c['id'] == choice_id for c in companies):
                    company_id = choice_id
                else:
                    print("ID de cliente inválido.")
        if database.add_new_transaction(trans_date_str, trans_type, amount, description, company_id):
            print("\nTransação registrada com sucesso!")
        else:
            print("\nFalha ao registrar a transação.")
    except ValueError:
        print("Valor inválido."); time.sleep(2)
    input("\nPressione Enter para voltar ao menu...")

def view_advanced_financials():
    """Exibe o Dashboard Financeiro, com opção de visão consolidada ou por cliente."""
    clear_screen()
    print("--- DASHBOARD FINANCEIRO AVANÇADO ---")
    print("Selecione o tipo de visualização:")
    print("1. Consolidado (Todos os Clientes)")
    print("2. Cliente Específico")
    
    choice = input("Escolha uma opção: ")
    company_id = None
    title = "CONSOLIDADO"

    if choice == '2':
        companies = database.get_all_companies()
        if not companies:
            print("Nenhum cliente cadastrado."); input(); return
        for company in companies:
            print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
        try:
            choice_id = int(input("Digite o ID do cliente para analisar: "))
            selected_company = next((c for c in companies if c['id'] == choice_id), None)
            if selected_company:
                company_id = choice_id
                title = selected_company['internal_alias'].upper()
            else:
                print("ID inválido."); time.sleep(2); return
        except ValueError:
            print("Entrada inválida."); time.sleep(2); return
    elif choice != '1':
        print("Opção inválida."); time.sleep(2); return

    clear_screen()
    print(f"--- DASHBOARD FINANCEIRO AVANÇADO: {title} ---")
    
    dashboard_data = database.get_financial_dashboard_data(period_days=30, company_id=company_id)
    
    receita_bruta = dashboard_data.get('current_revenue', 0.0)
    despesas_totais = dashboard_data.get('current_expenses', 0.0)
    margem_liquida = receita_bruta - despesas_totais
    
    receita_anterior = dashboard_data.get('previous_revenue', 0.0)
    crescimento_receita = ((receita_bruta / receita_anterior) - 1) * 100 if receita_anterior > 0 else 0
    percentual_despesa = (despesas_totais / receita_bruta) * 100 if receita_bruta > 0 else 0
    percentual_margem = (margem_liquida / receita_bruta) * 100 if receita_bruta > 0 else 0
    
    print("\n--- PERFORMANCE (ÚLTIMOS 30 DIAS) ---")
    print(f"💰 Receita Bruta:   R$ {receita_bruta:,.2f} ({crescimento_receita:+.1f}% vs período anterior)")
    print(f"💸 Despesas Totais: R$ {despesas_totais:,.2f} ({percentual_despesa:.1f}% da receita)")
    print(f"📊 Margem Líquida:  R$ {margem_liquida:,.2f} ({percentual_margem:.1f}% de margem)")
    print(f"💹 Fluxo Líquido:   R$ {margem_liquida:,.2f} (Disponível para investimento/distribuição)")

    contracts = database.get_all_contracts_with_company_info(company_id=company_id)
    active_contracts_value = sum(c['monthly_price'] for c in contracts)
    
    analysis = core.generate_financial_analysis(dashboard_data, active_contracts_value)
    
    print("\n--- ANÁLISE ESTRATÉGICA ---")
    if 'margem_crescimento' in analysis: print(f"📈 {analysis['margem_crescimento']}")
    if 'oportunidade_antecipacao' in analysis: print(f"💰 {analysis['oportunidade_antecipacao']}")

    summary = database.get_financial_summary(company_id=company_id)
    current_balance = summary['balance']
    avg_expenses_monthly = dashboard_data.get('current_expenses', 0.0) 
    
    projections = core.calculate_cash_flow_projection(current_balance, contracts, avg_expenses_monthly)
    
    if 'alerta_fluxo_caixa' in projections:
        print(f"🚨 Fluxo de Caixa Apertado: {projections['alerta_fluxo_caixa']}")

    print("\n--- PROJEÇÃO DE FLUXO DE CAIXA (SALDO ESTIMADO) ---")
    print(f"  - Em 30 dias:  R$ {projections.get(30, 0.0):,.2f}")
    print(f"  - Em 90 dias:  R$ {projections.get(90, 0.0):,.2f}")
    print(f"  - Em 180 dias: R$ {projections.get(180, 0.0):,.2f}")

    input("\nPressione Enter para voltar ao menu...")

def handle_ra_consult():
    """Gerencia o fluxo de consulta de reputação no Reclame Aqui."""
    clear_screen()
    print("--- CONSULTAR REPUTAÇÃO NO RECLAME AQUI ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
    for c in companies:
        print(f"ID: {c['id']} | Identificação: {c['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente: "))
        company = next((c for c in companies if c['id'] == choice_id), None)
        if company:
            slug = input(f"Digite o slug de '{company['internal_alias']}' no Reclame Aqui: ").strip()
            result = core.fetch_reclameaqui_data(slug)
            if result['status'] == 'success':
                database.update_company_ra_data(choice_id, result['data'])
                print("\nDados de reputação salvos com sucesso!")
            else:
                print(f"\nERRO: {result['message']}")
        else:
            print("ID inválido.")
    except ValueError:
        print("Entrada inválida.")
    input("\nPressione Enter para voltar ao menu...")

def handle_delete_company():
    """Gerencia o fluxo de exclusão de um cliente."""
    clear_screen()
    print("--- EXCLUIR CLIENTE ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
    for c in companies:
        print(f"ID: {c['id']} | Identificação: {c['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente para excluir: "))
        company = next((c for c in companies if c['id'] == choice_id), None)
        if company:
            confirm = input(f"Tem certeza que deseja excluir '{company['internal_alias']}' (S/N)? ").upper()
            if confirm == 'S':
                if database.delete_company_by_id(choice_id):
                    print("Cliente e todos os seus dados associados foram excluídos.")
                else:
                    print("Erro ao excluir o cliente.")
            else:
                print("Exclusão cancelada.")
        else:
            print("ID inválido.")
    except ValueError:
        print("Entrada inválida.")
    input("\nPressione Enter para voltar ao menu...")

def handle_set_cash_flow():
    """Gerencia a inserção do fluxo de caixa mensal."""
    clear_screen()
    print("--- ATUALIZAR FLUXO DE CAIXA MENSAL ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input("\nPressione Enter para voltar..."); return
    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente: "))
        if any(c['id'] == choice_id for c in companies):
            cash_flow = float(input("Digite o fluxo de caixa mensal LÍQUIDO (ex: 5000.00): "))
            database.update_company_cash_flow(choice_id, cash_flow)
            print("\nFluxo de caixa atualizado com sucesso!")
        else:
            print("ID inválido.")
    except ValueError:
        print("Entrada inválida.")
    input("\nPressione Enter para voltar ao menu...")

def handle_add_debt():
    """Gerencia a inserção manual de qualquer tipo de dívida."""
    clear_screen()
    print("--- ADICIONAR DÍVIDA MANUALMENTE ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente para esta dívida: "))
        if not any(c['id'] == choice_id for c in companies):
            print("ID inválido."); time.sleep(2); return
        while True:
            print("\nQual o tipo da dívida?")
            print("  1 - Bancária")
            print("  2 - Fornecedor")
            print("  3 - Protesto")
            debt_type_choice = input("Escolha uma opção: ")
            if debt_type_choice == '1': debt_type = "Bancária"; break
            elif debt_type_choice == '2': debt_type = "Fornecedor"; break
            elif debt_type_choice == '3': debt_type = "Protesto"; break
            else: print("Opção inválida.")
        creditor = input(f"Nome do Credor (ex: Banco do Brasil, Fornecedor X): ")
        balance = float(input("Valor da Dívida (R$): "))
        details = input("Detalhes (opcional, ex: Contrato 123, NF 456): ")
        database.add_debt(choice_id, debt_type, creditor, balance, details)
        print(f"\nDívida do tipo '{debt_type}' adicionada com sucesso!")
    except ValueError:
        print("Entrada inválida.")
    input("\nPressione Enter para voltar...")

def view_debt_analysis():
    """Exibe a análise completa de dívidas para um cliente selecionado."""
    clear_screen()
    print("--- ANÁLISE DE DÍVIDAS ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    try:
        choice_id = int(input("\nDigite o ID do cliente para analisar: "))
        company_to_analyze = next((c for c in companies if c['id'] == choice_id), None)
        if company_to_analyze:
            debts = database.get_debts_by_company(choice_id)
            analysis = core.generate_debt_analysis(company_to_analyze, debts)
            
            total_dividas = sum(d['outstanding_balance'] for d in debts)
            total_bancario = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Bancária')
            total_fornecedor = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Fornecedor')
            total_protestos = sum(d['outstanding_balance'] for d in debts if d['debt_type'] == 'Protesto')

            clear_screen()
            print(f"--- ANÁLISE DE DÍVIDAS: {company_to_analyze['internal_alias'].upper()} ---")
            print(f"\nTotal de Dívidas: R$ {total_dividas:,.2f}")
            print("-" * 40)
            print(f"  - Dívidas Bancárias: R$ {total_bancario:,.2f}")
            print(f"  - Fornecedores:      R$ {total_fornecedor:,.2f}")
            print(f"  - Protestos:         R$ {total_protestos:,.2f}")
            
            print("\n--- ANÁLISE ESTRATÉGICA ---")
            print(f"Score Crítico: {analysis.get('score_critico', 'Nenhuma análise gerada.')}")
            if 'oportunidade' in analysis:
                print(f"💰 Oportunidade de Negociação: {analysis['oportunidade']}")
            if 'capacidade_pagamento' in analysis:
                print(f"📈 Capacidade de Pagamento: {analysis['capacidade_pagamento']}")
            if 'protestos' in analysis:
                print(f"⚖️ Protestos Pendentes: {analysis['protestos']}")
            
            print("\n--- DETALHAMENTO DAS DÍVIDAS ---")
            if not debts:
                print("Nenhuma dívida registrada para este cliente.")
            else:
                for debt in debts:
                    print(f"  - [{debt['debt_type']}] {debt['creditor_name']}: R$ {debt['outstanding_balance']:,.2f} ({debt.get('details') or 'Sem detalhes'})")
        else:
            print("ID inválido.")
    except ValueError:
        print("Entrada inválida.")
    input("\nPressione Enter para voltar ao menu...")

def handle_recommendations():
    """Gerencia o fluxo da tela de Recomendações de IA."""
    clear_screen()
    print("--- RECOMENDAÇÕES ESTRATÉGICAS DE IA ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return
        
    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    
    try:
        choice_id = int(input("\nDigite o ID do cliente para gerar recomendações: "))
        company = next((c for c in companies if c['id'] == choice_id), None)
        if not company:
            print("ID inválido."); time.sleep(2); return

        while True:
            clear_screen()
            print(f"--- RECOMENDAÇÕES PARA: {company['internal_alias'].upper()} ---")
            
            recommendations = database.get_recommendations(choice_id)
            
            if not recommendations:
                print("\nNenhuma recomendação encontrada no banco de dados.")
            else:
                all_priorities = [rec['priority'] for rec in recommendations]
                p_alta = all_priorities.count('alta')
                p_media = all_priorities.count('media')
                p_baixa = all_priorities.count('baixa')

                print(f"\nFiltros: (1) Todas [{len(recommendations)}] | (2) Alta [{p_alta}] | (3) Média [{p_media}] | (4) Baixa [{p_baixa}]")
                filter_choice = input("Ver recomendações por prioridade (pressione Enter para Todas): ")
                
                if filter_choice == '2': recommendations = [r for r in recommendations if r['priority'] == 'alta']
                elif filter_choice == '3': recommendations = [r for r in recommendations if r['priority'] == 'media']
                elif filter_choice == '4': recommendations = [r for r in recommendations if r['priority'] == 'baixa']

                for rec in recommendations:
                    print("\n" + "-"*50)
                    print(f" Título: {rec['title']} | Prioridade: {rec['priority'].upper()}")
                    print(f" Descrição: {rec['description']}")
                    print(f" Investimento: R$ {rec.get('investment', 0):,.0f} | ROI: {rec.get('roi', 0):.0f}% | Prazo: {rec.get('timeline', 0)} meses")
                    print(f" (Gerado por: {rec['generated_by']})")
                    print("-" * 50)

            print("\nOpções:")
            print("1. Gerar Novas Recomendações (Pode incorrer em custos de API)")
            print("2. Voltar ao Menu Principal")
            choice_action = input("Escolha uma opção: ")

            if choice_action == '1':
                print("\nGerando novas recomendações... Isso pode levar um minuto.")
                new_recs = core.generate_recommendations(choice_id)
                if new_recs:
                    database.save_recommendations(choice_id, new_recs)
                    print("Novas recomendações foram geradas e salvas!")
                else:
                    print("Não foi possível gerar novas recomendações no momento.")
                input("Pressione Enter para continuar...")
            elif choice_action == '2':
                break
            else:
                print("Opção inválida."); time.sleep(1)

    except ValueError:
        print("Entrada inválida."); time.sleep(2)

def handle_set_revenue():
    """Gerencia a inserção do faturamento anual de um cliente."""
    clear_screen()
    print("--- INFORMAR FATURAMENTO ANUAL ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input("\nPressione Enter para voltar..."); return
        
    for company in companies:
        current_revenue = f"(Atual: R$ {company.get('annual_revenue'):,.2f})" if company.get('annual_revenue') else ""
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']} {current_revenue}")
    
    try:
        choice_id = int(input("\nDigite o ID do cliente para informar o faturamento: "))
        if any(c['id'] == choice_id for c in companies):
            revenue = float(input("Digite o faturamento anual total (ex: 1200000.00): "))
            database.update_company_revenue(choice_id, revenue)
            print("\nFaturamento anual atualizado com sucesso!")
        else:
            print("ID inválido.")
    except (ValueError, TypeError):
        print("Entrada inválida. Por favor, digite um número.")
        
    input("\nPressione Enter para voltar ao menu...")

def handle_market_analysis():
    """Gerencia o fluxo para a Análise de Mercado."""
    clear_screen()
    print("--- ANÁLISE DE MERCADO ---")
    companies = database.get_all_companies()
    if not companies:
        print("Nenhum cliente cadastrado."); input(); return

    for company in companies:
        print(f"ID: {company['id']} | Cliente: {company['internal_alias']}")
    
    try:
        choice_id = int(input("\nDigite o ID do cliente para analisar: "))
        company = next((c for c in companies if c['id'] == choice_id), None)
        
        if not company:
            print("ID inválido."); time.sleep(2); return

        if not company.get('annual_revenue'):
            print("\nERRO: O faturamento anual deste cliente não foi informado.")
            print("Por favor, use a opção 'Informar Faturamento Anual' no menu principal primeiro.")
            input("Pressione Enter para voltar..."); return
        
        print("\nIniciando análise de mercado... Isso pode levar um momento.")
        analysis_result = core.calculate_market_analysis(company)

        if analysis_result['status'] == 'success':
            data = analysis_result['data']
            database.update_market_data(choice_id, data['market_share'], data['market_rank'])
            
            clear_screen()
            print(f"--- ANÁLISE DE MERCADO: {company['internal_alias'].upper()} ---")
            
            print("\n--- KPIs DE MERCADO ---")
            print(f"🎯 Market Share: {data['market_share']:.2f}%")
            print(f"🏆 Posição Ranking: #{data['market_rank']} de {data['total_companies']} empresas na região")
            print(f"💰 Mercado Total (Estimado): R$ {data['total_market_size']:,.2f}")
            print(f"📈 Potencial de Captura: R$ {data['potential_capture']:,.2f}")
            
            print("\n--- INSIGHTS ESTRATÉGICOS (IA) ---")
            q_analysis = data['qualitative_analysis']
            print(f"📈 Crescimento do Mercado: {q_analysis['crescimento_mercado']}")
            print(f"🎯 Oportunidade Geográfica: {q_analysis['oportunidade_geografica']}")
            print(f"🏆 Posição Competitiva: {q_analysis['posicao_competitiva']}")
            print(f"⚠️ Pressão Competitiva: {q_analysis['pressao_competitiva']}")
        else:
            print(f"\nERRO ao gerar análise: {analysis_result['message']}")

    except ValueError:
        print("Entrada inválida.")
    
    input("\nPressione Enter para voltar ao menu...")