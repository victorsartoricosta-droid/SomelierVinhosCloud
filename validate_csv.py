import pandas as pd
import chardet

def validate_csv():
    # Detecta codificação
    with open('VinhosFinos.csv', 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    
    # Detecta delimitador
    with open('VinhosFinos.csv', encoding=encoding) as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','
    
    # Carrega dados
    df = pd.read_csv('VinhosFinos.csv', encoding=encoding, sep=delimiter)
    
    # Verifica colunas
    required = ['Nome', 'Preco_CNPJ', 'Preco_PF', 'Notas_Sabor', 'Combinacoes']
    missing = [col for col in required if col not in df.columns]
    
    print(f"\n🔍 Análise do arquivo VinhosFinos.csv:")
    print(f"• Codificação detectada: {encoding}")
    print(f"• Delimitador usado: '{delimiter}'")
    print(f"• Total de linhas: {len(df)}")
    print(f"• Colunas encontradas: {', '.join(df.columns)}")
    
    if missing:
        print(f"\n❌ ERRO: Colunas faltando: {', '.join(missing)}")
        print("SOLUÇÃO: Seu CSV deve ter EXATAMENTE estas colunas (sem acentos):")
        print(", ".join(required))
    else:
        print("\n✅ CSV VALIDADO COM SUCESSO! Estrutura correta detectada.")

if __name__ == "__main__":
    validate_csv()
