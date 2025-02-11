import os
import pandas as pd
import numpy as np

class SpotifyDataLoader:
    def __init__(self):
        self.raw_data_path = 'data/raw'
        self.processed_data_path = 'data/processed'
        self.input_file = os.path.join(self.raw_data_path, 'spoty_tracks.csv')
        
    def analyze_data_types(self, df):
        """Análise detalhada dos tipos de dados e estatísticas básicas"""
        print("\n=== ANÁLISE DOS TIPOS DE DADOS ===")
        
        # Informações sobre tipos de dados
        print("\nTipos de dados por coluna:")
        for col in df.columns:
            print(f"{col}: {df[col].dtype}")
            
        # Análise de valores únicos para variáveis categóricas
        print("\nQuantidade de valores únicos por coluna:")
        for col in df.columns:
            n_unique = df[col].nunique()
            print(f"{col}: {n_unique} valores únicos")
        
        # Estatísticas básicas para variáveis numéricas
        print("\nEstatísticas básicas para variáveis numéricas:")
        print(df.describe())
        
        # Análise de valores nulos
        print("\nValores nulos por coluna:")
        null_counts = df.isnull().sum()
        for col in df.columns:
            print(f"{col}: {null_counts[col]} valores nulos")
            
        return {
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(exclude=[np.number]).columns.tolist(),
            'null_counts': null_counts.to_dict(),
            'unique_counts': df.nunique().to_dict()
        }
    
    def process_data(self):
        """Processamento inicial dos dados"""
        print("Processando dados...")
        
        # Verificar se o arquivo existe
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Arquivo {self.input_file} não encontrado. Por favor, coloque o arquivo spotify_dataset.csv na pasta data/raw/")
        
        # Carrega o dataset
        df = pd.read_csv(self.input_file)
        print(f"Dataset carregado com {len(df)} registros")
        
        # Informações básicas sobre o dataset
        print("\nInformações do dataset:")
        print(df.info())
        
        # Limpeza básica
        df = df.dropna()  # Remove linhas com valores nulos
        print(f"\nDataset após limpeza: {len(df)} registros")
        
        # Convertendo duration_ms para minutos se existir
        if 'duration_ms' in df.columns:
            df['duration_min'] = df['duration_ms'] / 60000
        
        # Análise dos tipos de dados
        data_analysis = self.analyze_data_types(df)
        
        # Salvando dados processados
        output_file = os.path.join(self.processed_data_path, 'processed_spotify.csv')
        os.makedirs(self.processed_data_path, exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"\nDados processados salvos em: {output_file}")
        return df, data_analysis

if __name__ == "__main__":
    loader = SpotifyDataLoader()
    df, analysis = loader.process_data()
    print("\nAnálise concluída! Os dados estão prontos para processamento posterior.")