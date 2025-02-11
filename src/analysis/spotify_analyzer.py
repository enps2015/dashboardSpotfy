import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from scipy import stats
import os

class SpotifyAnalyzer:
    def __init__(self):
        self.data_path = Path('data/processed/processed_spotify.csv')
        self.visualization_path = Path('static/visualization')
        self.df = None
        
        # Criar diretório de visualização se não existir
        os.makedirs(self.visualization_path, exist_ok=True)
        print(f"Diretório de visualizações criado em: {self.visualization_path}")
    
    def load_data(self):
        """Carrega os dados processados"""
        self.df = pd.read_csv(self.data_path)
        
        # Criando categorias de popularidade para análises
        self.df['popularity_category'] = pd.cut(
            self.df['popularity'],
            bins=[0, 20, 40, 60, 80, 100],
            labels=['Muito Baixa', 'Baixa', 'Média', 'Alta', 'Muito Alta']
        )
        
        # Criando categorias de duração
        self.df['duration_category'] = pd.cut(
            self.df['duration_min'],
            bins=[0, 2, 3, 4, 5, float('inf')],
            labels=['Muito Curta', 'Curta', 'Média', 'Longa', 'Muito Longa']
        )
        
        return self.df
    
    def analyze_genre_popularity(self):
        """Análise da relação entre gêneros e popularidade usando gráfico de dispersão"""
        genre_stats = self.df.groupby('genre').agg({
            'popularity': ['mean', 'std', 'count']
        }).round(2)
        
        genre_stats.columns = ['popularity_mean', 'popularity_std', 'track_count']
        genre_stats = genre_stats.reset_index()
        genre_stats = genre_stats[genre_stats['track_count'] >= 5]
        
        fig = px.scatter(
            genre_stats,
            x='popularity_mean',
            y='track_count',
            size='track_count',
            color='popularity_mean',
            color_continuous_scale=[[0, '#282828'], [0.5, '#404040'], [1, '#1DB954']],
            title='Popularidade vs. Quantidade de Músicas por Gênero',
            labels={
                'popularity_mean': 'Popularidade Média',
                'track_count': 'Quantidade de Músicas',
                'genre': 'Gênero'
            }
        )
        
        # Remover rótulos e ajustar aparência
        fig.update_traces(
            textposition=None,
            text=None,
            hovertemplate="<br>".join([
                "Gênero: %{customdata[0]}",
                "Popularidade Média: %{x:.1f}",
                "Quantidade: %{y}",
                "<extra></extra>"
            ]),
            customdata=genre_stats[['genre']],
            marker=dict(
                line=dict(color='#1DB954', width=1)
            )
        )
        
        return fig
    
    def analyze_explicit_by_genre(self):
        """Análise de conteúdo explícito por gênero"""
        explicit_by_genre = self.df.groupby('genre')['explicit'].agg(['mean', 'count']).reset_index()
        explicit_by_genre['explicit_percentage'] = explicit_by_genre['mean'] * 100
        explicit_by_genre = explicit_by_genre[explicit_by_genre['count'] >= 10]
        explicit_by_genre = explicit_by_genre.sort_values('explicit_percentage', ascending=False)
        
        fig = px.bar(
            explicit_by_genre.head(10),
            x='genre',
            y='explicit_percentage',
            title='Porcentagem de Conteúdo Explícito por Gênero (Top 10)',
            labels={
                'genre': 'Gênero',
                'explicit_percentage': 'Porcentagem de Músicas Explícitas'
            }
        )
        
        fig.update_traces(marker_color='#1DB954')
        return fig
    
    def analyze_duration_distribution(self):
        """Análise da distribuição de duração das músicas"""
        fig = go.Figure()
        
        fig.add_trace(go.Violin(
            y=self.df['duration_min'],
            box_visible=True,
            line_color='#1DB954',
            fillcolor='rgba(29, 185, 84, 0.3)',
            name='Distribuição'
        ))
        
        fig.update_layout(
            title='Distribuição da Duração das Músicas',
            yaxis_title='Duração (minutos)',
            showlegend=False
        )
        return fig
    
    def analyze_popularity_trends(self):
        """Análise das tendências de popularidade"""
        popularity_stats = self.df.groupby('popularity_category').agg({
            'duration_min': 'mean',
            'explicit': 'mean',
            'id': 'count'
        }).reset_index()
        
        popularity_stats['explicit_percentage'] = popularity_stats['explicit'] * 100
        popularity_stats['count_percentage'] = (popularity_stats['id'] / len(self.df)) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=popularity_stats['popularity_category'],
            y=popularity_stats['count_percentage'],
            name='% do Total de Músicas',
            marker_color='#1DB954',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=popularity_stats['popularity_category'],
            y=popularity_stats['duration_min'],
            name='Duração Média (min)',
            line=dict(color='#FFFFFF'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Análise de Popularidade vs. Duração',
            yaxis=dict(title='Porcentagem do Total'),
            yaxis2=dict(
                title='Duração Média (min)',
                overlaying='y',
                side='right',
                titlefont=dict(color='#FFFFFF'),
                tickfont=dict(color='#FFFFFF')
            ),
            barmode='group'
        )
        return fig
    
    def get_business_insights(self):
        """Gera insights de negócio baseados nas análises"""
        insights = {
            'generos_populares': self.df.groupby('genre')['popularity'].mean().nlargest(5).to_dict(),
            'duracao_ideal': {
                'media': self.df[self.df['popularity'] >= 60]['duration_min'].mean(),
                'mediana': self.df[self.df['popularity'] >= 60]['duration_min'].median()
            },
            'explicit_impact': stats.pointbiserialr(
                self.df['explicit'],
                self.df['popularity']
            ).correlation,
            'distribuicao_popularidade': self.df['popularity_category'].value_counts().to_dict()
        }
        return insights
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nas análises"""
        insights = self.get_business_insights()
        
        recommendations = {
            'composicao_playlist': {
                'generos_recomendados': list(insights['generos_populares'].keys()),
                'duracao_ideal': f"{insights['duracao_ideal']['media']:.2f} minutos",
                'distribuicao_sugerida': {
                    'musicas_populares': '40%',
                    'musicas_trending': '30%',
                    'musicas_descoberta': '30%'
                }
            },
            'estrategia_conteudo': {
                'conteudo_explicito': 'Moderar' if insights['explicit_impact'] < 0 else 'Manter',
                'foco_duracao': 'Priorizar músicas entre 2-4 minutos',
                'diversidade': f"Incluir pelo menos {len(insights['generos_populares'])} gêneros diferentes"
            }
        }
        return recommendations

    def analyze_correlations(self):
        """Análise de correlações entre variáveis numéricas e categóricas"""
        numeric_corr = self.df[['popularity', 'duration_min']].corr()
        
        genres = self.df['genre'].unique()
        genre_groups = [self.df[self.df['genre'] == genre]['popularity'] for genre in genres]
        f_statistic, p_value = stats.f_oneway(*genre_groups)
        
        contingency = pd.crosstab(self.df['genre'], self.df['explicit'])
        chi2, p_value_chi2, dof, expected = stats.chi2_contingency(contingency)
        
        genre_trends = self.df.groupby(['genre', 'popularity_category'])['id'].count().unstack(fill_value=0)
        genre_trends_pct = genre_trends.div(genre_trends.sum(axis=1), axis=0) * 100
        
        results = {
            'correlacoes': numeric_corr.to_dict(),
            'anova_genero_popularidade': {
                'f_statistic': f_statistic,
                'p_value': p_value
            },
            'chi2_genero_explicit': {
                'chi2': chi2,
                'p_value': p_value_chi2
            },
            'tendencias_genero': genre_trends_pct.to_dict()
        }
        
        # Melhorar a visualização da matriz de correlação
        fig = go.Figure(data=go.Heatmap(
            z=numeric_corr.values,
            x=['Popularidade', 'Duração (min)'],
            y=['Popularidade', 'Duração (min)'],
            colorscale=[[0, '#282828'], [0.5, '#404040'], [1, '#1DB954']],
            showscale=True,
            hoverongaps=False,
            hovertemplate='%{x} x %{y}<br>Correlação: %{z:.2f}<extra></extra>',
            texttemplate='%{z:.2f}',
            textfont={"color": "#FFFFFF"}
        ))
        
        fig.update_layout(
            title='Matriz de Correlação entre Variáveis',
            xaxis_title='Variáveis',
            yaxis_title='Variáveis',
            width=600,
            height=500
        )
        
        return results, fig
    
    def analyze_genre_success_factors(self):
        """Análise dos fatores de sucesso por gênero"""
        success_metrics = self.df.groupby('genre').agg({
            'popularity': ['mean', 'std', 'count'],
            'duration_min': 'mean',
            'explicit': 'mean'
        }).round(2)
        
        success_metrics['popularity', 'ci_95'] = success_metrics.apply(
            lambda x: stats.norm.interval(
                0.95,
                loc=x[('popularity', 'mean')],
                scale=x[('popularity', 'std')] / np.sqrt(x[('popularity', 'count')])
            )[1] - x[('popularity', 'mean')],
            axis=1
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Popularidade Média',
            x=success_metrics.index,
            y=success_metrics[('popularity', 'mean')],
            marker_color='#1DB954',
            error_y=dict(
                type='data',
                array=success_metrics[('popularity', 'ci_95')],
                visible=True,
                color='#FFFFFF'
            )
        ))
        
        fig.add_trace(go.Scatter(
            name='Duração Média (min)',
            x=success_metrics.index,
            y=success_metrics[('duration_min', 'mean')],
            line=dict(color='#FFFFFF'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Análise de Fatores de Sucesso por Gênero',
            yaxis=dict(title='Popularidade Média'),
            yaxis2=dict(
                title='Duração Média (min)',
                overlaying='y',
                side='right',
                titlefont=dict(color='#FFFFFF'),
                tickfont=dict(color='#FFFFFF')
            ),
            showlegend=True
        )
        
        return success_metrics, fig

    def save_visualizations(self):
        """Gera e salva todas as visualizações"""
        print("Gerando visualizações...")
        
        try:
            # Gerar gráficos
            genre_pop_fig = self.analyze_genre_popularity()
            print("Gerado gráfico de popularidade por gênero")
            
            explicit_fig = self.analyze_explicit_by_genre()
            print("Gerado gráfico de análise de conteúdo explícito")
            
            duration_fig = self.analyze_duration_distribution()
            print("Gerado gráfico de distribuição de duração")
            
            popularity_fig = self.analyze_popularity_trends()
            print("Gerado gráfico de tendências de popularidade")
            
            corr_results, corr_fig = self.analyze_correlations()
            print("Gerada matriz de correlação")
            
            success_metrics, success_fig = self.analyze_genre_success_factors()
            print("Gerado gráfico de fatores de sucesso")
            
            # Salvar gráficos como HTML e PNG
            for name, fig in [
                ('genre_popularity', genre_pop_fig),
                ('explicit_analysis', explicit_fig),
                ('duration_distribution', duration_fig),
                ('popularity_trends', popularity_fig),
                ('correlation_matrix', corr_fig),
                ('success_factors', success_fig)
            ]:
                html_path = self.visualization_path / f"{name}.html"
                png_path = self.visualization_path / f"{name}.png"
                
                print(f"Salvando {name} em {html_path}")
                fig.write_html(str(html_path))
                
                print(f"Salvando {name} em {png_path}")
                fig.write_image(str(png_path))
            
            print("Todas as visualizações foram salvas com sucesso!")
            
            return {
                'genre_popularity': genre_pop_fig,
                'explicit_analysis': explicit_fig,
                'duration_dist': duration_fig,
                'popularity_trends': popularity_fig,
                'correlation_matrix': corr_fig,
                'success_factors': success_fig
            }
        except Exception as e:
            print(f"Erro ao gerar visualizações: {str(e)}")
            raise

if __name__ == "__main__":
    analyzer = SpotifyAnalyzer()
    df = analyzer.load_data()
    
    # Gerar e salvar todas as visualizações
    visualizations = analyzer.save_visualizations()
    
    # Gerar insights e recomendações
    insights = analyzer.get_business_insights()
    recommendations = analyzer.generate_recommendations()
    
    print("\nANOVA - Relação entre Gênero e Popularidade:")
    print(f"F-statistic: {corr_results['anova_genero_popularidade']['f_statistic']:.3f}")
    print(f"p-value: {corr_results['anova_genero_popularidade']['p_value']:.3f}")
    
    print("\nChi-quadrado - Independência entre Gênero e Conteúdo Explícito:")
    print(f"Chi2: {corr_results['chi2_genero_explicit']['chi2']:.3f}")
    print(f"p-value: {corr_results['chi2_genero_explicit']['p_value']:.3f}")
    
    print("\n=== MÉTRICAS DE SUCESSO POR GÊNERO ===")
    print(success_metrics)