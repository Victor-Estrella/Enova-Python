'''
Turma: 1TDSPH

Integrantes:

Leticia Cristina dos Santos Passos, rm: 555241
André Rogério Vieira Pavanela Altobelli Antunes, rm: 554764
Victor Henrique Estrella Carracci RM:556206

'''

#-----------------------Imports-----------------------#
import oracledb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#-----------------------Imports-----------------------#


#Esta função estabelece conexão com o banco de dados.
def get_connection():
    connection = oracledb.connect('rm554764/030206@oracle.fiap.com.br:1521/orcl')
    print('Conectado com sucesso:', connection.version)
    return connection

#Esta função gera uma lista de datas aleatórias dentro de um intervalo.
def gerar_datas(inicio, fim, n):
    return [inicio + timedelta(days=np.random.randint(0, (fim - inicio).days)) for _ in range(n)]

#Esta função era um DataFrame com dados simulados para análise de eficiência.
def gerar_dados_simulados(n, inicio, fim):
    datas = gerar_datas(inicio, fim, n)
    nr_producao_energia = np.round(np.random.uniform(1000, 5000, n), 2)
    nr_consumo_energia = np.round(np.random.uniform(800, 4500, n), 2)
    nr_eficiencia = np.round((nr_producao_energia / nr_consumo_energia) * 100, 2)

    return pd.DataFrame({
        'dt_analise': datas,
        'nr_producao_energia': nr_producao_energia,
        'nr_consumo_energia': nr_consumo_energia,
        'nr_eficiencia': nr_eficiencia
    })

#Esta função gera dados simulados para alertas.
def gerar_alertas_simulados(n, inicio, fim):
    datas = gerar_datas(inicio, fim, n)
    tipos = np.random.choice(['Baixa Produção', 'Manutenção Necessária', 'Falha de Sistema'], n)
    status = np.random.choice(['Ativo', 'Resolvido'], n)
    return pd.DataFrame({
        'Data': datas,
        'Tipo': tipos,
        'Status': status
    })

#Esta função gera dados simulados para manutenções.
def gerar_manutencoes_simuladas(n, inicio, fim):
    datas = gerar_datas(inicio, fim, n)
    tipos = np.random.choice(['Preventiva', 'Corretiva'], n)
    return pd.DataFrame({
        'Data': datas,
        'Tipo de Manutenção': tipos
    })

#Esta função insere os dados do DataFrame na tabela do banco de dados.
def inserir_dados(connection, df, tabela):
    try:
        cursor = connection.cursor()
        for _, row in df.iterrows():
            cursor.execute(f"""
                INSERT INTO {tabela} (
                    dt_analise, nr_producao_energia, nr_consumo_energia, nr_eficiencia
                ) VALUES (
                    TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4
                )
            """, (
                row['dt_analise'].strftime('%Y-%m-%d'),
                row['nr_producao_energia'],
                row['nr_consumo_energia'],
                row['nr_eficiencia']
            ))
        connection.commit()
        print(f"Dados inseridos com sucesso na tabela {tabela}!")
    except oracledb.DatabaseError as e:
        print("Erro ao inserir dados no banco de dados:", e)
    finally:
        if cursor:
            cursor.close()

#Esta função salva os dados gerados em um arquivo JSON.
def salvar_historico(df, caminho='historico.json'):
    try:
        df.to_json(caminho, orient='records', date_format='iso', indent=4)
        print(f"Dados salvos em {caminho}")
    except Exception as e:
        print(f"Erro ao salvar dados no arquivo: {e}")

#Esta função gera gráficos com base nos dados simulados.
def gerar_graficos(df_eficiencia, df_alertas, df_manutencoes):
    try:
        # Ordenar os dados por data
        df_eficiencia = df_eficiencia.sort_values(by='dt_analise')

        # Gráfico 1: Produção e Consumo de Energia
        plt.figure(figsize=(12, 6))
        plt.plot(df_eficiencia['dt_analise'], df_eficiencia['nr_producao_energia'], label='Produção de Energia', color='green', marker='o')
        plt.plot(df_eficiencia['dt_analise'], df_eficiencia['nr_consumo_energia'], label='Consumo de Energia', color='red', marker='x')
        plt.title('Produção vs Consumo de Energia')
        plt.xlabel('Data')
        plt.ylabel('Energia (kWh)')
        plt.legend()
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Formata a data no eixo X
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Mostra um mês por vez no eixo
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Gráfico 2: Eficiência
        plt.figure(figsize=(12, 6))
        plt.plot(df_eficiencia['dt_analise'], df_eficiencia['nr_eficiencia'], label='Eficiência (%)', color='blue', marker='.')
        plt.title('Eficiência Energética ao Longo do Tempo')
        plt.xlabel('Data')
        plt.ylabel('Eficiência (%)')
        plt.grid(True)
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Gráfico 3: Alertas por Tipo
        plt.figure(figsize=(10, 6))
        df_alertas['Tipo'].value_counts().plot(kind='bar', title='Distribuição de Tipos de Alertas')
        plt.xlabel('Tipo de Alerta')
        plt.ylabel('Frequência')
        plt.tight_layout()
        plt.show()

        # Gráfico 4: Manutenções por Tipo
        plt.figure(figsize=(10, 6))
        df_manutencoes['Tipo de Manutenção'].value_counts().plot(kind='pie', autopct='%1.1f%%', title='Distribuição de Tipos de Manutenção')
        plt.ylabel('')  # Remove o rótulo padrão do eixo Y
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Erro ao gerar gráficos: {e}")

#Esta função consulta uma análise de eficiência pelo ID e exporta para JSON.
def consultar_analise_por_id(connection, id_analise, caminho='analise_por_id.json'):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT dt_analise, nr_producao_energia, nr_consumo_energia, nr_eficiencia
            FROM t_enova_analise_eficiencia
            WHERE id_analise = :1
        """, (id_analise,))
        resultado = cursor.fetchone()
        if resultado:
            df = pd.DataFrame([resultado], columns=['dt_analise', 'nr_producao_energia', 'nr_consumo_energia', 'nr_eficiencia'])
            df.to_json(caminho, orient='records', date_format='iso', indent=4)
            print(f"Análise exportada para {caminho}.")
        else:
            print("Nenhuma análise encontrada com esse ID.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao consultar análise: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função consulta análises com eficiência abaixo de um determinado valor e exporta para JSON.
def consultar_eficiencia_abaixo(connection, valor_limite, caminho='eficiencia_abaixo.json'):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT dt_analise, nr_producao_energia, nr_consumo_energia, nr_eficiencia
            FROM t_enova_analise_eficiencia
            WHERE nr_eficiencia < :1
            ORDER BY nr_eficiencia ASC
        """, (valor_limite,))
        resultados = cursor.fetchall()
        if resultados:
            df = pd.DataFrame(resultados, columns=['dt_analise', 'nr_producao_energia', 'nr_consumo_energia', 'nr_eficiencia'])
            df.to_json(caminho, orient='records', date_format='iso', indent=4)
            print(f"Análises exportadas para {caminho}.")
        else:
            print(f"Nenhuma análise encontrada com eficiência abaixo de {valor_limite}%.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao consultar análises: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função consulta análises realizadas dentro de um intervalo de datas e exporta para JSON.
def consultar_analises_por_intervalo(connection, data_inicio, data_fim, caminho='analises_intervalo.json'):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT dt_analise, nr_producao_energia, nr_consumo_energia, nr_eficiencia
            FROM t_enova_analise_eficiencia
            WHERE dt_analise BETWEEN TO_DATE(:1, 'YYYY-MM-DD') AND TO_DATE(:2, 'YYYY-MM-DD')
            ORDER BY dt_analise
        """, (data_inicio, data_fim))
        resultados = cursor.fetchall()
        if resultados:
            df = pd.DataFrame(resultados, columns=['dt_analise', 'nr_producao_energia', 'nr_consumo_energia', 'nr_eficiencia'])
            df.to_json(caminho, orient='records', date_format='iso', indent=4)
            print(f"Análises exportadas para {caminho}.")
        else:
            print(f"Nenhuma análise encontrada entre {data_inicio} e {data_fim}.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao consultar análises: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função atualiza uma análise de eficiência no banco de dados pelo ID.
def atualizar_analise(connection, id_analise, producao, consumo, eficiencia):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE t_enova_analise_eficiencia
            SET nr_producao_energia = :1,
                nr_consumo_energia = :2,
                nr_eficiencia = :3
            WHERE id_analise = :4
        """, (producao, consumo, eficiencia, id_analise))
        connection.commit()
        print(f"Análise com ID {id_analise} atualizada com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao atualizar análise: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função deleta uma análise de eficiência pelo ID.
def deletar_analise(connection, id_analise):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM t_enova_analise_eficiencia
            WHERE id_analise = :1
        """, (id_analise,))
        connection.commit()
        print(f"Análise com ID {id_analise} deletada com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao deletar análise: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função insere uma análise manualmente no banco de dados.
def inserir_analise_manual(connection, data, producao, consumo, eficiencia):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO t_enova_analise_eficiencia (
                dt_analise, nr_producao_energia, nr_consumo_energia, nr_eficiencia
            ) VALUES (
                TO_DATE(:1, 'YYYY-MM-DD'), :2, :3, :4
            )
        """, (data, producao, consumo, eficiencia))
        connection.commit()
        print("Análise inserida com sucesso.")
    except oracledb.DatabaseError as e:
        print(f"Erro ao inserir análise manualmente: {e}")
    finally:
        if cursor:
            cursor.close()

#Esta função gerencia o fluxo principal do programa.
def menu_principal():
    connection = None
    inicio = datetime(2023, 1, 1)
    fim = datetime(2024, 1, 1)
    df_eficiencia = pd.DataFrame()
    df_alertas = pd.DataFrame()
    df_manutencoes = pd.DataFrame()

    while True:
        print("\n=== Menu Principal ===")
        print("1. Gerar dados simulados")
        print("2. Inserir dados no banco de dados")
        print("3. Salvar dados em JSON")
        print("4. Gerar gráficos")
        print("5. Consultar análise de eficiência por ID")
        print("6. Consultar análises com eficiência abaixo de um valor")
        print("7. Consultar análises por intervalo de datas")
        print("8. Atualizar análise por ID")
        print("9. Deletar análise por ID")
        print("10. Inserir análise manualmente")
        print("11. Sair")
        try:
            opcao = int(input("Escolha uma opção: "))
            if opcao == 1:
                n = int(input("Quantos registros deseja gerar? "))
                if n <= 0:
                    print("Por favor, insira um número positivo.")
                    continue
                df_eficiencia = gerar_dados_simulados(n, inicio, fim)
                df_alertas = gerar_alertas_simulados(n, inicio, fim)
                df_manutencoes = gerar_manutencoes_simuladas(n, inicio, fim)
                print(f"{n} registros gerados com sucesso!")
            elif opcao == 2:
                if df_eficiencia.empty:
                    print("Nenhum dado gerado. Por favor, gere os dados primeiro.")
                    continue
                if not connection:
                    connection = get_connection()
                inserir_dados(connection, df_eficiencia, 't_enova_analise_eficiencia')
            elif opcao == 3:
                if df_eficiencia.empty:
                    print("Nenhum dado gerado. Por favor, gere os dados primeiro.")
                    continue
                salvar_historico(df_eficiencia)
            elif opcao == 4:
                if df_eficiencia.empty:
                    print("Nenhum dado gerado. Por favor, gere os dados primeiro.")
                    continue
                gerar_graficos(df_eficiencia, df_alertas, df_manutencoes)
            elif opcao == 5:
                if not connection:
                    connection = get_connection()
                id_analise = int(input("Digite o ID da análise: "))
                consultar_analise_por_id(connection, id_analise)
            elif opcao == 6:
                if not connection:
                    connection = get_connection()
                valor_limite = float(input("Digite o valor limite de eficiência (%): "))
                consultar_eficiencia_abaixo(connection, valor_limite)
            elif opcao == 7:
                if not connection:
                    connection = get_connection()
                data_inicio = input("Digite a data de início (YYYY-MM-DD): ")
                data_fim = input("Digite a data de fim (YYYY-MM-DD): ")
                consultar_analises_por_intervalo(connection, data_inicio, data_fim)
            elif opcao == 8:
                if not connection:
                    connection = get_connection()
                id_analise = int(input("Digite o ID da análise a ser atualizada: "))
                producao = float(input("Digite o novo valor de produção de energia: "))
                consumo = float(input("Digite o novo valor de consumo de energia: "))
                eficiencia = float(input("Digite o novo valor de eficiência (%): "))
                atualizar_analise(connection, id_analise, producao, consumo, eficiencia)
            elif opcao == 9:
                if not connection:
                    connection = get_connection()
                id_analise = int(input("Digite o ID da análise a ser deletada: "))
                deletar_analise(connection, id_analise)
            elif opcao == 10:
                if not connection:
                    connection = get_connection()
                data = input("Digite a data da análise (YYYY-MM-DD): ")
                producao = float(input("Digite o valor de produção de energia: "))
                consumo = float(input("Digite o valor de consumo de energia: "))
                eficiencia = float(input("Digite o valor de eficiência (%): "))
                inserir_analise_manual(connection, data, producao, consumo, eficiencia)
            elif opcao == 11:
                if connection:
                    connection.close()
                print("Saindo do programa...")
                break
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")
        except Exception as e:
            print(f"Ocorreu um erro: {e}")


#Principal

menu_principal()
