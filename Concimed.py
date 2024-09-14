import pandas as pd
import streamlit as st

# Define a função para carregar os dados da planilha
def load_data(file):
    df = pd.read_excel(file)
    # Filtrar apenas as linhas onde a "Fase do negócio" é "NF Enviadas"
    df = df[df['Fase do negócio'] == 'NF Enviadas']
    return df

# Define a função para filtrar os dados
def filter_data(df, selected_month):
    df['Data Recebimento'] = pd.to_datetime(df['Data Recebimento'])
    df['Mês'] = df['Data Recebimento'].dt.to_period('M')
    
    # Lista de todos os meses
    months_available = df['Mês'].unique()
    months_available = [str(m) for m in sorted(months_available, reverse=True)]
    
    # Filtrar dados para o mês selecionado
    current_month = pd.Period(selected_month, freq='M')
    df_current_month = df[df['Mês'] == current_month]
    
    # Encontrar empresas sem notas no mês selecionado
    all_companies = df['Nome'].unique()
    companies_with_notes = df_current_month['Nome'].unique()
    missing_companies = set(all_companies) - set(companies_with_notes)
    
    # DataFrame com empresas que precisam de notas
    missing_notes = df[df['Nome'].isin(missing_companies)]
    missing_notes = missing_notes.drop_duplicates(subset=['Nome'])
    
    # Adicionar informação do mês
    missing_notes['Mês Pendência'] = selected_month
    result = missing_notes[['Nome', 'Mês Pendência']]
    
    return result, months_available

# Função principal
def main():
    # Configurar a página
    st.set_page_config(page_title="Controle de Notas Fiscais", page_icon=":ledger:", layout="wide")

    # Adicionar CSS customizado
    st.markdown("""
        <style>
            .main {
                background-color: #333333; /* Fundo cinza escuro */
                color: #ffffff; /* Texto branco para contraste */
            }
            .css-1a0w0r4 {
                background-color: #ff8c00; /* Laranja escuro para a barra superior */
                color: white;
            }
            .css-1b2rc0y {
                background-color: #ff8c00;
            }
            .css-1y0k33x {
                color: #ff8c00; /* Laranja escuro para o texto */
            }
            .css-18e3th9 {
                padding: 1rem;
                color: #ffffff; /* Texto branco para visibilidade no fundo escuro */
            }
            .css-1y0k33x img {
                height: 60px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Logo da empresa
    st.markdown('<img src="https://concimedbr.com.br/wp-content/uploads/2023/12/Assets.svg" class="css-1y0k33x" />', unsafe_allow_html=True)

    st.title('Controle de Notas Fiscais - Concimed')
    st.write("Desenvolvido por Gabrielle Carvalho")

    uploaded_file = st.file_uploader("Escolha a planilha de notas emitidas", type="xlsx")

    if uploaded_file:
        df = load_data(uploaded_file)

        st.write("Planilha carregada:")
        st.dataframe(df)

        months_available = df['Data Recebimento'].dt.to_period('M').unique()
        months_available = [str(m) for m in sorted(months_available, reverse=True)]
        
        selected_month = st.selectbox("Selecione o mês de referência", months_available)

        if selected_month:
            result, months_available = filter_data(df, selected_month)
            if result.empty:
                st.write(f"Parabéns! Sem notas para emitir nesse período ({selected_month}).")
            else:
                st.write(f"Empresas que ainda precisam emitir nota para o mês {selected_month}:")
                st.dataframe(result)
                
                # Criar um link para download do relatório
                csv = result.to_csv(index=False)
                st.download_button(
                    label="Baixar relatório de pendências",
                    data=csv,
                    file_name=f'relatorios_pendencias_{selected_month}.csv',
                    mime='text/csv'
                )
    
if __name__ == "__main__":
    main()
