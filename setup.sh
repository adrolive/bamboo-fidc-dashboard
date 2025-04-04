#!/bin/bash

# Criar pasta para cache
mkdir -p ~/.streamlit

# Configurar o Streamlit
echo "\
[general]
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]
headless = true
enableCORS = false
port = $PORT\n\
" > ~/.streamlit/config.toml 