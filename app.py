from flask import Flask, render_template, send_from_directory, jsonify
import pandas as pd
import plotly
import json
from src.analysis.spotify_analyzer import SpotifyAnalyzer
import os
import shutil

app = Flask(__name__)

def ensure_static_files():
    """Garante que todos os arquivos estáticos necessários estejam nos diretórios corretos"""
    # Obter o caminho absoluto do diretório do projeto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(project_dir, 'static')
    
    # Criar diretórios necessários
    os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'icons'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'visualization'), exist_ok=True)
    
    # Copiar imagens
    src_header = os.path.join(project_dir, 'img', 'header.png')
    dst_header = os.path.join(static_dir, 'img', 'header.png')
    if os.path.exists(src_header):
        shutil.copy2(src_header, dst_header)
        print(f"Copiado header.png para {dst_header}")
    
    # Copiar ícones
    icon_files = ['linkedin_logo.png', 'instagram_logo.png', 'github_logo.png']
    for icon in icon_files:
        src_icon = os.path.join(project_dir, 'icons', icon)
        dst_icon = os.path.join(static_dir, 'icons', icon)
        if os.path.exists(src_icon):
            shutil.copy2(src_icon, dst_icon)
            print(f"Copiado {icon} para {dst_icon}")

def apply_spotify_theme(fig):
    """Aplica o tema do Spotify aos gráficos"""
    fig.update_layout(
        paper_bgcolor='#121212',
        plot_bgcolor='#282828',
        font_color='#FFFFFF',
        title_font_color='#1DB954',
        title_x=0.5,
        margin=dict(t=50, r=50, b=50, l=50),
        showlegend=True,
        legend=dict(
            font=dict(color='#FFFFFF'),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='#404040'
        )
    )
    
    # Atualizar eixos
    fig.update_xaxes(
        gridcolor='#404040',
        linecolor='#404040',
        tickfont=dict(color='#FFFFFF')
    )
    fig.update_yaxes(
        gridcolor='#404040',
        linecolor='#404040',
        tickfont=dict(color='#FFFFFF')
    )
    
    return fig

def generate_all_visualizations():
    """Gera e salva todas as visualizações ao iniciar a aplicação"""
    try:
        analyzer = SpotifyAnalyzer()
        df = analyzer.load_data()
        return analyzer.save_visualizations()
    except Exception as e:
        print(f"Erro ao gerar visualizações: {e}")
        return None

# Configurar arquivos estáticos e gerar visualizações ao iniciar
ensure_static_files()
visualizations = generate_all_visualizations()

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    try:
        analyzer = SpotifyAnalyzer()
        df = analyzer.load_data()
        graphs = {}
        
        def add_graph(name, func):
            try:
                fig = func()
                if isinstance(fig, tuple):
                    fig = apply_spotify_theme(fig[1])
                    graphs[name] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    fig = apply_spotify_theme(fig)
                    graphs[name] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return True
            except Exception as e:
                print(f"Erro ao gerar {name}: {e}")
                return False

        # Gerar todos os gráficos
        add_graph('genre_popularity', analyzer.analyze_genre_popularity)
        add_graph('explicit_analysis', analyzer.analyze_explicit_by_genre)
        add_graph('duration_dist', analyzer.analyze_duration_distribution)
        add_graph('popularity_trends', analyzer.analyze_popularity_trends)
        
        # Correlação e fatores de sucesso
        corr_results, corr_fig = analyzer.analyze_correlations()
        corr_fig = apply_spotify_theme(corr_fig)
        graphs['correlation_matrix'] = json.dumps(corr_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        success_metrics, success_fig = analyzer.analyze_genre_success_factors()
        success_fig = apply_spotify_theme(success_fig)
        graphs['success_factors'] = json.dumps(success_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Gerar insights e recomendações
        insights = analyzer.get_business_insights()
        recommendations = analyzer.generate_recommendations()
        
        return render_template('index.html',
                             graphs=graphs,
                             insights=insights,
                             recommendations=recommendations,
                             success_metrics=success_metrics.to_html(
                                 classes='table table-dark table-striped',
                                 justify='left'
                             ))
    
    except Exception as e:
        print(f"Erro ao renderizar página: {e}")
        return render_template('index.html',
                             graphs={},
                             insights={},
                             recommendations={},
                             success_metrics="")

if __name__ == '__main__':
    # Garantir que os arquivos estáticos estejam presentes antes de iniciar
    ensure_static_files()
    app.run(debug=True, port=5001)