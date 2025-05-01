
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
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, A5, LETTER, LEGAL, landscape
from reportlab.lib import colors
from PIL import Image

RODAPE_LOGO_BASE64 = """
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
"""

def extrair_informacoes(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    texto = ""
    for page in doc:
        texto += page.get_text()
    produtos_brutos = re.findall(
        r"\d+\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+\d+\s+(\d{1,3}(?:\.\d{3})*,\d{2})",
        texto,
        re.DOTALL
    )
    produtos = []
    for desc, preco_unitario, _ in produtos_brutos:
        desc = ' '.join(desc.split())
        if any(palavra in desc.lower() for palavra in ["nota", "endereço", "telefones", "horários"]):
            continue
        if 'Descrição' in desc or 'Grade' in desc or 'Preço' in desc:
            continue
        if '-' in desc:
            desc = desc.split('-', 1)[1].strip()
        produtos.append((desc, f"R$ {preco_unitario}"))
    return produtos

def buscar_produto_por_url(url_nova):
    try:
        html = requests.get(url_nova).content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        # Nome do produto
        h1 = soup.find("h1", class_="w-full text-xl font-bold text-left uppercase text-primary")
        nome = h1.get_text(strip=True) if h1 else None
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
            return (nome, preco)
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

def gerar_pdf(produtos, output_path, tamanho_pagina, margens, altura_logo_cm, titulo_pequeno, titulo_grande):
    c = canvas.Canvas(output_path, pagesize=tamanho_pagina)
    width, height = tamanho_pagina
    margem_topo, margem_base, margem_lateral = margens
    spacing = 1.2 * cm
    y = height - 0.5 * cm

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.HexColor("#BBAA88"))
    c.drawCentredString(width / 2, y, titulo_pequeno)
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y, titulo_grande)
    y -= 2 * cm

    c.setFillColor(colors.black)
    for produto, preco in produtos:
        if y < margem_base * cm + 3 * cm:
            c.showPage()
            y = height - margem_topo * cm

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, y, produto)
        y -= 0.6 * cm
        c.setFont("Helvetica-Bold", 12)
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


margem_topo = 2.0
margem_base = 1.0
margem_lateral = 1.0
altura_logo_cm = 5.0



col1, col2,col3 = st.columns([1,1,1])
with col1:
    with st.form("adicionar_produto_form"):
        titulo_pequeno = st.text_input("Título Pequeno", value="OUTONO–INVERNO 2025")
        titulo_grande = st.text_input("Título Grande", value="MUNDO DE INSPIRAÇÕES")
        # Adicionar manualmente
        if st.form_submit_button("➕ Adicionar Produto Manualmente"):
            st.session_state.produtos.append(("", ""))
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
for idx, (nome, preco) in enumerate(st.session_state.produtos):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        novo_nome = st.text_input(f"Produto {idx+1}", value=nome, key=f"nome_{idx}")
    with col2:
        novo_preco = st.text_input(f"Preço {idx+1}", value=preco, key=f"preco_{idx}")
    with col3:
        if st.button("❌", key=f"excluir_{idx}"):
            st.session_state.produtos.pop(idx)
            st.rerun()
    produtos_editados.append((novo_nome, novo_preco))
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
            titulo_pequeno,
            titulo_grande
        )

        st.success("✅ PDF gerado com sucesso!")
        with open(tmp_pdf.name, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1200px" align="center" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("⬇️ Baixar PDF", f, file_name="orcamento_completo.pdf")


