import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
from io import BytesIO
import tempfile
import os
import fitz
import re
import base64
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, A5, LETTER, LEGAL, landscape
from reportlab.lib import colors
from PIL import Image

RODAPE_LOGO_BASE64 = """
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AACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7RB0AAAAANgOQQcAAACA7fz/BODcEhDyDIoAAAAASUVORK5CYII=
"""

def remover_medidas(texto):
  """Remove TODOS os padrões de medida de uma string."""
  padrao_medida = r'\s*\d+\s*(?:CM|M)?(?:\s*X\s*\d+\s*(?:CM|M)?)?'
  return re.sub(padrao_medida, '', texto, flags=re.IGNORECASE).strip()

def extrair_informacoes(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    texto = ""
    for page in doc:
        texto += page.get_text()

    produtos_brutos = re.findall(
        r"\d+\s+(.+?)\s+([\w\s\/]+)\s+(?:De\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+Por\s+(\d{1,3}(?:\.\d{3})*,\d{2})|(\d{1,3}(?:\.\d{3})*,\d{2}))\s+\d+\s+(\d{1,3}(?:\.\d{3})*,\d{2})",
        texto,
        re.DOTALL
    )
    produtos = []
    for desc, grade_cor, preco_de, preco_por, preco_normal,total in produtos_brutos:
        # Seus tratamentos de limpeza iniciais
        desc = ' '.join(desc.split())
        grade_cor = ' '.join(grade_cor.split())
        print(f"DEBUG: desc='{desc}', grade_cor='{grade_cor}', preco_de='{preco_de}', preco_por='{preco_por}', preco_normal='{preco_normal}'")
        if any(palavra in desc.lower() for palavra in ["nota", "endereço", "telefones", "horários"]):
            continue
            
        if desc.count('-') >= 2:
            desc = desc.split('-', 2)[2].strip()
        elif '-' in desc:
            desc = desc.split('-', 1)[1].strip()
        elif '#' in desc:
            desc = desc.split('#', 1)[1].strip()
        else:
            desc = re.sub(r"^\d+\s+", "", desc)

        # --- LÓGICA FINALÍSSIMA E ROBUSTA ---

        # 1. Limpe a medida da 'desc'.
        desc_limpa = remover_medidas(desc)

        # 2. Limpe a medida da 'grade_cor'. O que sobra aqui é a cor ou outra info.
        grade_cor_limpa = remover_medidas(grade_cor)

        # 3. Capture a medida que queremos manter, buscando-a na 'grade_cor' ORIGINAL.
        medida_a_manter = ""
        match = re.search(r'\d+\s*(?:CM|M)?(?:\s*X\s*\d+\s*(?:CM|M)?)?', grade_cor, re.IGNORECASE)
        if match:
            medida_a_manter = match.group(0).strip()

        # 4. Monte a string final com as partes certas.
        #    [desc limpa] + [grade/cor limpa] + [medida da grade]
        descricao_final = f"{desc_limpa} {grade_cor_limpa}".strip()
        
        # 5. Limpeza final de espaços para um resultado perfeito.
        descricao_final = ' '.join(descricao_final.split())

        # Monta a string de preço
        if preco_por:
            preco = f"De R$ {preco_de} Por R$ {preco_por}"
        else:
            preco = f"R$ {preco_normal}"

        produtos.append((desc_limpa,medida_a_manter, preco))

    return produtos
def buscar_produto_por_url(url_nova):
    try:
        html = requests.get(url_nova).content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        # Nome do produto
        h1 = soup.find("h1", class_="w-full text-xl font-bold text-left uppercase text-primary")
        nome = h1.get_text(strip=True) if h1 else None
        if '-' in nome:
            novoNome = nome.split('-', 1)[0].strip()
            grade = nome.split('-', 1)[1].strip()
            nome = novoNome
        else:
            nome = nome
            grade = ""
        # Preço do produto
        span = soup.find("span", class_="text-xl font-bold text-primary")
        preco = span.get_text(strip=True).replace(" ", "").replace("\xa0", " ") if span else None
        span = soup.find("span", class_="text-xs text-neutral-500 line-through uppercase")
        preco_promocional = span.get_text(strip=True).replace("\xa0", " ") if span else None
        # Preço do produto
        span = soup.find("span", class_="text-xl font-bold text-primary")
        preco = span.get_text(strip=True).replace(" ", "").replace("\xa0", " ") if span else None 
        if preco_promocional is not None:
            preco = f"{preco_promocional}  Por {preco}"
        else:
            preco = preco
        if nome and preco:
            return (nome,grade, preco)
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
    return None

def buscar_produto_por_id(produto_id):
    url_busca = f"https://www.mundodoenxoval.com.br/s?q={produto_id}"
    html_busca = requests.get(url_busca).content.decode("utf-8")
    soup_busca = BeautifulSoup(html_busca, "html.parser")
    tag_link = soup_busca.find("script", {"type": "application/ld+json"})
    dados = json.loads(tag_link.string)

    # Extraindo produtos
    produtos = dados.get("products", [])
    if not produtos:
        return None
    resultado = []
    for prod in produtos:
        item = {
            "nome": prod.get("alternateName"),
            "preco": prod.get("offers", {}).get("offers", [{}])[0].get("price"),
            "link": prod.get("url")
        }
    if item is None or item == {}:
        return None
    resultado.append(item)
    url = resultado[0]['link'] if resultado else None
    url = str(url).split("?")[0] + f"?skuId={produto_id}" if url else None
    url_nova = buscar_produto_por_url(url)
    return url_nova
    
FORMATOS_PAGINA = {
    "A4 (21 x 29,7 cm)": A4,
    "A5 (14,8 x 21 cm)": A5,
    "Letter (21,6 x 27,9 cm)": LETTER,
    "Legal (21,6 x 35,6 cm)": LEGAL,
    "A4 Paisagem": landscape(A4)
}

def gerar_pdf(produtos, output_path, tamanho_pagina, margens, altura_logo_cm, titulo_grande,titulo_pequeno):
    c = canvas.Canvas(output_path, pagesize=tamanho_pagina)
    width, height = tamanho_pagina
    margem_topo, margem_base, margem_lateral = margens
    spacing = 1.5 * cm
    y = height - 3 * cm

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.gold)
    c.drawCentredString(width / 2, y, titulo_grande)
    y -= 0.6 * cm

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.orange)
    c.drawCentredString(width / 2, y, titulo_pequeno)
    y -= 2 * cm


    
    for produto,medida, preco in produtos:
        if y < margem_base * cm + 3 * cm:
            c.showPage()
            y = height - margem_topo * cm

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y, produto)
        y -= 0.6 * cm
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y, medida)
        y -= 0.6 * cm
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.gold)
        c.drawCentredString(width / 2, y, preco)
        y -= spacing

    if RODAPE_LOGO_BASE64.strip():
        img_data = base64.b64decode(RODAPE_LOGO_BASE64)
        image = Image.open(BytesIO(img_data))
        largura = 5 * cm
        altura = largura * (image.height / image.width)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
            image.save(tmp_logo.name, format="PNG")
            c.drawImage(tmp_logo.name, (width - largura) / 2, margem_base * cm - 0.2 * cm, largura, altura, mask='auto')


    c.save()

# App
st.set_page_config(page_title="Mundo do Enxoval", layout="wide")
st.title("🧾 Gerador de Orçamento")


margem_topo = 4.0
margem_base = 1.0
margem_lateral = 1.0
altura_logo_cm = 5.0



col1, col2,col3 = st.columns([1,1,1])
with col1:
    with st.form("adicionar_produto_form"):
        titulo_grande = st.text_input("Título Grande", value="MUNDO DE INSPIRAÇÕES")
        titulo_pequeno = st.text_input("Título Pequeno", value="OUTONO–INVERNO 2025")
        # Adicionar manualmente
        if st.form_submit_button("➕ Adicionar Produto Manualmente"):
            st.session_state.produtos.append(("", "", ""))
with col2:
    if 'produtos' not in st.session_state:
        st.session_state.produtos = []
    with st.form("buscar_produto_form"):
        st.subheader("🔍 Buscar Produto por skuId")
        produto_id = st.text_input("Digite o skuId do produto")
        buscar = st.form_submit_button("Buscar e Adicionar")
        if buscar and produto_id:
            resultado = buscar_produto_por_id(produto_id)
            if resultado:
                st.session_state.produtos.append(resultado)
                st.success(f"✅ Produto adicionado: {resultado[0]} - {resultado[1]}")
            else:
                st.warning("⚠️ Produto não encontrado.")

with col3:
    formato_selecionado = st.selectbox("Formato da Página", list(FORMATOS_PAGINA.keys()))
    pdf_file = st.file_uploader("Upload do PDF (opcional)", type=["pdf"])
    if pdf_file and not st.session_state.produtos:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
            tmp_input.write(pdf_file.read())
            tmp_input.flush()
            produtos_extraidos = extrair_informacoes(tmp_input.name)
            st.session_state.produtos = produtos_extraidos
# Lista de produtos
st.subheader("🛒 Produtos Selecionados")
produtos_editados = []
for idx, (nome, medida, preco) in enumerate(st.session_state.produtos):
    col1, col2, col3,col4 = st.columns([3, 1, 1, 1])
    with col1:
        novo_nome = st.text_input(f"Produto {idx+1}", value=nome, key=f"nome_{idx}")
    with col2:
        nova_medida = st.text_input(f"Grade {idx+1}", value=medida, key=f"medida_{idx}")
    with col3:
        novo_preco = st.text_input(f"Preço {idx+1}", value=preco, key=f"preco_{idx}")
    with col4:
        if st.button("❌", key=f"excluir_{idx}"):
            st.session_state.produtos.pop(idx)
            st.rerun()
    produtos_editados.append((novo_nome,nova_medida, novo_preco))
st.session_state.produtos = produtos_editados

# Gerar PDF
if st.button("📄 Gerar PDF"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:

        gerar_pdf(
            st.session_state.produtos,
            tmp_pdf.name,
            FORMATOS_PAGINA[formato_selecionado],
            (margem_topo, margem_base, margem_lateral),
            altura_logo_cm,
            titulo_grande,
            titulo_pequeno
        )

        st.success("✅ PDF gerado com sucesso!")
        with open(tmp_pdf.name, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1200px" align="center" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("⬇️ Baixar PDF", f, file_name="orcamento_completo.pdf")