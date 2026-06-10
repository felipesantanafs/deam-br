import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def create_funil_violencia():
    # Caminhos
    sinan_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dados', 'sinan', 'sinan_cnes_merged.csv'))
    sim_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dados', 'sim', 'sim_feminicidios_sp.csv'))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'relatorios'))
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Lendo bases de dados...")
    df_sinan = pd.read_csv(sinan_path, low_memory=False)
    df_sim = pd.read_csv(sim_path, low_memory=False)
    
    # Processando SINAN (Ameaça e Violência Física)
    # Convertemos 'sim' para 1 e o resto para 0, se for string, mas no BD original 'ocorreu_violencia_fisica' geralmente é 'sim'/'não' ou 'Sim'/'Não'
    # 'meio_ameaca' também tem os mesmos valores
    
    # Ajustando os valores para booleanos ou 1/0
    for col in ['ocorreu_violencia_fisica', 'meio_ameaca']:
        df_sinan[col] = df_sinan[col].astype(str).str.lower().map({'sim': 1, '1': 1, '1.0': 1, 'true': 1}).fillna(0)
    
    # Agrupando por ano
    sinan_agg = df_sinan.groupby('ano').agg(
        total_ameacas=('meio_ameaca', 'sum'),
        total_lesoes=('ocorreu_violencia_fisica', 'sum'),
        total_notificacoes=('data_ocorrencia', 'count')
    ).reset_index()
    
    # Processando SIM (Feminicídios)
    sim_agg = df_sim.groupby('ano').agg(
        total_feminicidios=('data_obito', 'count')
    ).reset_index()
    
    # Merge das agregações
    funil = pd.merge(sinan_agg, sim_agg, on='ano', how='outer').fillna(0)
    funil = funil[(funil['ano'] >= 2015) & (funil['ano'] <= 2019)] # A partir de 2015 por conta da lei do feminicídio até 2019 (limite SINAN BD)
    
    funil['ano'] = funil['ano'].astype(int)
    funil = funil.sort_values('ano')
    
    print("Dados do Funil da Violência:")
    print(funil)
    
    # Salvando em CSV na pasta dados
    funil_csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dados', 'consolidado', 'funil_violencia_ano.csv')
    funil.to_csv(funil_csv_path, index=False)
    
    # Plotando o Funil Temporal
    plt.figure(figsize=(10, 6))
    
    sns.lineplot(data=funil, x='ano', y='total_ameacas', marker='o', label='Ameaças (SINAN)', color='orange')
    sns.lineplot(data=funil, x='ano', y='total_lesoes', marker='o', label='Violência Física/Lesão (SINAN)', color='red')
    sns.lineplot(data=funil, x='ano', y='total_feminicidios', marker='o', label='Feminicídios (SIM)', color='black')
    
    plt.title('Evolução do Funil da Violência (São Paulo, a partir de 2015)', fontsize=14)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel('Número de Registros', fontsize=12)
    plt.yscale('log') # Escala logarítmica devido à grande diferença de volume
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    
    # Salvando gráfico
    img_path = os.path.join(output_dir, 'funil_violencia.png')
    plt.savefig(img_path, dpi=300)
    plt.close()
    
    print(f"Gráfico salvo em {img_path}")

if __name__ == "__main__":
    create_funil_violencia()
