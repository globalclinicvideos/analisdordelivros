# -*- coding: cp1252 -*-
import os
import re
import pandas as pd
from pypdf import PdfReader

# ==========================================
# CONFIGURAÇÕES
# ==========================================
# Caminho para a pasta onde estão os 340 PDFs (use '.' se o script estiver na mesma pasta)
PASTA_PDFS = "./livros_pdf"

# Lista de termos ou expressões que você deseja buscar (case-insensitive por padrão)
TERMOS_BUSCA = [
    r"igreja multiplicadora",
    r"líder multiplicador",
    r"pequeno grupo",
    r"pgm",
    r"visão multiplicadora",
    r"discípulo",
    r"intencional"
]

# Tamanho do contexto extraído antes e depois do termo (em caracteres)
MARGEM_CONTEXTO = 160

# Arquivo de saída em Excel
ARQUIVO_SAIDA = "resultado_busca_tematica.xlsx"

# ==========================================
# EXECUÇÃO DA BUSCA
# ==========================================
def extrair_ocorrencias(caminho_pasta, termos):
    padroes_compilados = [re.compile(termo, re.IGNORECASE) for termo in termos]
    resultados = []
    
    arquivos = [f for f in os.listdir(caminho_pasta) if f.lower().endswith('.pdf')]
    total_arquivos = len(arquivos)
    print(f"Total de livros encontrados: {total_arquivos}\nIniciando análise...")

    for i, nome_arquivo in enumerate(arquivos, start=1):
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        print(f"[{i}/{total_arquivos}] Processando: {nome_arquivo}")
        
        try:
            leitor = PdfReader(caminho_completo)
            for num_pag, pagina in enumerate(leitor.pages, start=1):
                texto = pagina.extract_text()
                if not texto:
                    continue
                
                # Normaliza quebras de linha e múltiplos espaços
                texto_limpo = " ".join(texto.split())
                
                for padrao in padroes_compilados:
                    for match in padrao.finditer(texto_limpo):
                        inicio_match, fim_match = match.span()
                        
                        # Extrai trecho com margem de contexto antes e depois
                        inicio_corte = max(0, inicio_match - MARGEM_CONTEXTO)
                        fim_corte = min(len(texto_limpo), fim_match + MARGEM_CONTEXTO)
                        
                        trecho = texto_limpo[inicio_corte:fim_corte].strip()
                        
                        resultados.append({
                            "Arquivo / Livro": nome_arquivo,
                            "Página": num_pag,
                            "Termo Pesquisado": padrao.pattern,
                            "Termo Encontrado": match.group(0),
                            "Trecho de Contexto": f"... {trecho} ..."
                        })
        except Exception as e:
            print(f"Erro ao processar o arquivo {nome_arquivo}: {e}")
            
    return resultados

# Executa e gera a planilha
if __name__ == "__main__":
    if not os.path.exists(PASTA_PDFS):
        print(f"A pasta '{PASTA_PDFS}' não foi encontrada. Crie a pasta ou altere a variável PASTA_PDFS.")
    else:
        dados = extrair_ocorrencias(PASTA_PDFS, TERMOS_BUSCA)
        
        if dados:
            df = pd.DataFrame(dados)
            df.to_excel(ARQUIVO_SAIDA, index=False)
            print(f"\nVarredura concluída! {len(df)} ocorrências encontradas.")
            print(f"Planilha gerada com sucesso: {ARQUIVO_SAIDA}")
        else:
            print("\nNenhuma ocorrência encontrada para os termos especificados.")