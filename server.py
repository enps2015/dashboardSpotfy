if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) # Porta definida pelo Render ou 5000 como padrão
    app.run(debug=False, host='0.0.0.0', port=port)