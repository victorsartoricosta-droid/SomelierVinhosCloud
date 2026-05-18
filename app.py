import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sommelier de Vinhos Premium",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados com cache para melhor performance
@st.cache_data
def load_wine_data():
    try:
        # Detecta automaticamente codificação e delimitador
        with open("VinhosFinos.csv", 'rb') as f:
            result = chardet.detect(f.read())
        
        # Tenta detectar delimitador
        sample = open("VinhosFinos.csv", encoding=result['encoding']).read(1024)
        delimiter = ';' if ';' in sample else ','
        
        df = pd.read_csv("VinhosFinos.csv", encoding=result['encoding'], sep=delimiter)
        
        # Verifica colunas EXATAS
        required_columns = ['Nome', 'Preco_CNPJ', 'Preco_PF', 'Notas_Sabor', 'Combinacoes']
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            st.error(f"❌ COLUNAS FALTANDO: {', '.join(missing)}")
            st.warning("📌 **Solução:** Seu CSV deve ter EXATAMENTE estas colunas (sem acentos, sem espaços):")
            st.code("Nome, Preco_CNPJ, Preco_PF, Notas_Sabor, Combinacoes")
            
            # Mostra as colunas reais do CSV para comparação
            st.info(f"🔍 Colunas encontradas no seu CSV: {', '.join(df.columns)}")
            
            # Botão para baixar modelo correto
            st.download_button(
                "📥 BAIXAR MODELO CORRETO DE CSV",
                data="Nome,Preco_CNPJ,Preco_PF,Notas_Sabor,Combinacoes\nVinho Exemplo,100.00,200.00,\"Notas de prova\",\"Combinações sugeridas\"",
                file_name="modelo_vinhos_correto.csv",
                mime="text/csv"
            )
            st.stop()
            
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.error("🔧 **Dica profissional:** Abra seu CSV em um editor de texto (não no Excel) para verificar a estrutura real")
        st.stop()

# Função para calcular desconto seguro
def calculate_safe_discount(base_price, min_price, discount_percent):
    max_allowed_discount = ((base_price - min_price) / base_price) * 100
    if discount_percent > max_allowed_discount:
        return min_price, max_allowed_discount
    discounted_price = base_price * (1 - discount_percent/100)
    return discounted_price, discount_percent

# Interface principal
def main():
    # Cabeçalho
    st.title("🍷 Sommelier de Vinhos Premium")
    st.markdown("##### Sistema inteligente de consulta e cálculo de preços com proteção de margem")
    
    # Carregar dados
    df = load_wine_data()
    
    # Barra lateral com informações
    with st.sidebar:
        st.header("Informações do Sistema")
        st.info(f"**Atualizado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.info(f"**Total de vinhos disponíveis:** {len(df)}")
        st.markdown("---")
        st.warning("⚠️ O desconto máximo é calculado com base no preço mínimo (CNPJ)")
        st.markdown("O sistema **automaticamente bloqueia** descontos que ultrapassem o valor mínimo permitido")
    
    # Campo de busca
    search_term = st.text_input(
        "🔍 Buscar vinho por nome, sabor ou combinação:",
        placeholder="Ex: Cabernet, carne, frutas vermelhas...",
        help="Digite qualquer termo relacionado ao vinho que deseja encontrar"
    ).strip().lower()
    
    # Filtro de resultados
    if search_term:
        mask = (
            df['Nome'].str.lower().str.contains(search_term) |
            df['Notas_Sabor'].str.lower().str.contains(search_term) |
            df['Combinacoes'].str.lower().str.contains(search_term)
        )
        results = df[mask]
    else:
        results = df
    
    # Exibir resultados
    if len(results) == 0:
        st.warning("Nenhum vinho encontrado com os critérios de busca. Tente outro termo.")
        st.image("https://images.unsplash.com/photo-1513516247808-dac266865643?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", 
                 caption="Explore nossa seleção de vinhos finos")
    else:
        # Seletor de vinho
        selected_wine = st.selectbox(
            "Selecione um vinho para consultar:",
            results['Nome'].unique(),
            format_func=lambda x: f"🍷 {x}"
        )
        
        # Obter dados do vinho selecionado
        wine = results[results['Nome'] == selected_wine].iloc[0]
        
        # Layout em colunas
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📊 Valores do Vinho")
            st.metric("Preço Mínimo (CNPJ)", f"R$ {wine['Preco_CNPJ']:.2f}", 
                     help="Valor mínimo para venda a empresas")
            st.metric("Preço Máximo (Pessoa Física)", f"R$ {wine['Preco_PF']:.2f}",
                     help="Valor de tabela para consumidor final")
            
            # Calculadora de desconto
            st.subheader("🧮 Calculadora de Desconto")
            discount = st.slider(
                "Selecione a porcentagem de desconto:",
                min_value=0,
                max_value=100,
                value=0,
                help="O sistema bloqueia automaticamente descontos que ultrapassem o valor mínimo"
            )
            
            # Cálculo do desconto com proteção
            discounted_price, actual_discount = calculate_safe_discount(
                wine['Preco_PF'], wine['Preco_CNPJ'], discount
            )
            
            # Exibir resultados do cálculo
            if actual_discount < discount:
                st.error(f"⚠️ Desconto máximo permitido: {actual_discount:.2f}%")
                st.info(f"Preço mínimo atingido: R$ {wine['Preco_CNPJ']:.2f}")
            else:
                st.success(f"✅ Desconto aplicado: {actual_discount:.2f}%")
            
            st.metric("Preço com Desconto", f"R$ {discounted_price:.2f}")
            
            # Botão para nova consulta
            if st.button("🔄 Nova Consulta", use_container_width=True):
                st.experimental_rerun()
        
        with col2:
            st.subheader("📝 Relatório Completo do Vinho")
            
            # Exibir informações do vinho
            st.markdown(f"### {wine['Nome']}")
            st.markdown(f"**Notas de Sabor:**\n{wine['Notas_Sabor']}")
            st.markdown(f"**Combinações Gastronômicas:**\n{wine['Combinacoes']}")
            
            # Visualização do margem
            margin = ((wine['Preco_PF'] - wine['Preco_CNPJ']) / wine['Preco_PF']) * 100
            st.markdown("**Margem de Negociação:**")
            st.progress(int(margin))
            st.caption(f"Você pode oferecer até {margin:.2f}% de desconto mantendo o preço mínimo")
    
    # Rodapé
    st.markdown("---")
    st.caption("""
    Sistema desenvolvido com Python • Atualizado em tempo real com os dados do arquivo VinhosFinos.csv
    © 2026 Sommelier de Vinhos Premium - Todos os direitos reservados
    """)

if __name__ == "__main__":
    main()
