# Previsão de Chuva com Modelos Meteorológicos e Machine Learning

Este repositório contém um projeto de MVP (Minimum Viable Product) desenvolvido como parte de um MBA em Ciência de Dados. O objetivo é avaliar e melhorar previsões de **chuva acumulada** a partir de diferentes modelos meteorológicos numéricos (ex.: GFS, ICON, ECMWF, WRF) utilizando técnicas de aprendizado supervisionado.

## Objetivo do Projeto

O projeto busca comparar previsões meteorológicas de diferentes fontes e investigar se técnicas de Machine Learning podem:

* Corrigir erros sistemáticos dos modelos numéricos.  
* Combinar previsões (ensemble) para gerar estimativas mais robustas.  

## Estrutura do Repositório

* `forecasts.csv`: Dados brutos intermediários, utilizados para produzir o dado bruto completo.
* `dataset.csv`: Dado bruto completo utilizado como input no experimento.
* `datetimee.py`: Módulo auxiliar com funções de tratamento de data e hora.
* `local_api.py`: Módulo auxiliar para comunicação com a api onde o dado encontra-se.
* `script.py`: Script para download e organização dos dados brutos.
* `Machine_Learning_&_Analytics_(40530010055_20250_01).ipynb`: Notebook principal contendo o pipeline completo (pré-processamento, modelagem, tuning e avaliação).
* `README.md`

## Tecnologias Utilizadas

* Python 3.12  
* Pandas e NumPy (manipulação e análise de dados)  
* Matplotlib e Seaborn (visualização)  
* Scikit-learn (pré-processamento, modelagem e métricas)  
* XGBoost (modelagem avançada)  
* SciPy (distribuições para busca de hiperparâmetros)  

## Como Executar o Projeto

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio```

2. **Crie um ambiente virtual e instale as dependências:**
   ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
    pip install -r requirements.txt```

3. **Execute o Notebook:**
Abra o arquivo Machine_Learning_&_Analytics.ipynb em um ambiente Jupyter ou Google Colab e rode as células sequencialmente.
