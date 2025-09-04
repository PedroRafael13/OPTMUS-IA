# main.py

"""
Ponto de entrada principal para a aplicação RADAR OPTMUS.
Este script inicializa o banco de dados e executa o loop do menu principal.
"""

import time
import ui
import database

def main():
    """Função principal que executa o menu da aplicação."""
    # Garante que o banco de dados e todas as tabelas estão prontos ao iniciar
    database.setup_database() 
    
    # Mapeia as opções do menu para as funções correspondentes no módulo ui
    menu_options = {
        "1": ui.handle_register_company,
        "2": ui.view_full_diagnostic,
        "3": ui.handle_maturity_analysis,
        "4": ui.handle_market_analysis,
        "5": ui.handle_recommendations,
        "6": ui.view_advanced_financials,
        "7": ui.handle_add_transaction,
        "8": ui.view_debt_analysis,
        "9": ui.handle_add_debt,
        "10": ui.handle_set_cash_flow,
        "11": ui.handle_set_revenue,
        "12": ui.view_contracts,
        "13": ui.handle_add_contract,
        "14": ui.handle_ra_consult,
        "15": ui.handle_delete_company,
    }

    while True:
        ui.clear_screen()
        print("========= RADAR OPTMUS - v1.2 (Análise de Mercado) =========")
        
        print("\n--- Clientes e Diagnóstico ---")
        print("1. Cadastrar Novo Cliente")
        print("2. Ver Diagnóstico Geral")
        print("3. Realizar Análise de Maturidade")

        print("\n--- Mercado e Estratégia ---")
        print("4. Ver Análise de Mercado")
        print("5. Recomendações Estratégicas de IA")

        print("\n--- Financeiro e Dívidas ---")
        print("6. Ver Dashboard Financeiro Avançado")
        print("7. Registrar Transação (Entrada/Saída)")
        print("8. Ver Análise de Dívidas")
        print("9. Adicionar Dívida (Manual)")
        print("10. Informar Fluxo de Caixa Mensal")
        print("11. Informar Faturamento Anual")

        print("\n--- Contratos ---")
        print("12. Ver Todos os Contratos")
        print("13. Adicionar Novo Contrato")
        
        print("\n--- Ferramentas e Administração ---")
        print("14. Consultar no Reclame Aqui")
        print("15. Excluir um Cliente")
        print("16. Sair")
        
        choice = input("\nEscolha uma opção: ")

        if choice == '16':
            print("Saindo do sistema...")
            break
        
        # Procura a função correspondente à escolha no dicionário e a executa
        action = menu_options.get(choice)
        if action:
            action()
        else:
            print("Opção inválida. Tente novamente.")
            time.sleep(2)

# Garante que a função main() seja chamada apenas quando o script é executado diretamente
if __name__ == "__main__":
    main()