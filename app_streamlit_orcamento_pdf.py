
import streamlit as st
import fitz
import re
import tempfile
import os
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, LETTER, LEGAL, landscape
from PIL import Image

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

FORMATOS_PAGINA = {
    "A4 (21 x 29,7 cm)": A4,
    "A5 (14,8 x 21 cm)": A5,
    "Letter (21,6 x 27,9 cm)": LETTER,
    "Legal (21,6 x 35,6 cm)": LEGAL,
    "A4 Paisagem": landscape(A4)
}

def gerar_pdf(produtos, output_path, tamanho_pagina, logo_path, margens, altura_logo_cm, titulo_pequeno, titulo_grande):
    c = canvas.Canvas(output_path, pagesize=tamanho_pagina)
    width, height = tamanho_pagina

    margem_topo, margem_base, margem_lateral = margens
    spacing = 1.2 * cm

    y = height - 0.5 * cm

    if logo_path:
        img = Image.open(logo_path)
        img_width, img_height = img.size
        aspect = img_height / img_width
        largura_logo = altura_logo_cm * cm / aspect
        altura_logo = altura_logo_cm * cm
        c.drawImage(logo_path, (width - largura_logo) / 2, y - altura_logo, largura_logo, altura_logo, preserveAspectRatio=True, mask='auto')
        y = y - altura_logo + 0 * cm
    else:
        y = height - margem_topo * cm

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.HexColor("#BBAA88"))
    c.drawCentredString(width / 2, y, titulo_pequeno)
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, y, titulo_grande)
    y -= 1.5 * cm

    c.setFillColor(colors.black)

    for produto, preco in produtos:
        if y < margem_base * cm + 3 * cm:
            c.showPage()
            y = height - margem_topo * cm

        if len(produto) > 60:
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, y, produto[:60])
            y -= 0.5 * cm
            c.drawCentredString(width / 2, y, produto[60:])
        else:
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, y, produto)

        y -= 0.6 * cm
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2, y, preco)
        y -= spacing

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.HexColor("#BBAA88"))
    c.drawCentredString(width / 2, margem_base * cm, "Mundo do Enxoval")

    c.save()

# Streamlit App
st.set_page_config(page_title="Gerador de Orçamento", layout="wide")
st.title("Gerador de Orçamento - Mundo do Enxoval")

# Sidebar
st.sidebar.title("Configurações")

pdf_file = st.sidebar.file_uploader("Upload do PDF (opcional)", type=["pdf"])
logo_file = st.sidebar.file_uploader("Upload do Logo (opcional)", type=["png", "jpg", "jpeg"])
formato_selecionado = st.sidebar.selectbox("Formato da Página", list(FORMATOS_PAGINA.keys()))

margem_topo = st.sidebar.slider("Margem Superior (texto)", 1.0, 10.0, 2.0, step=0.5)
margem_base = st.sidebar.slider("Margem Inferior", 1.0, 5.0, 1.0, step=0.5)
margem_lateral = st.sidebar.slider("Margem Lateral", 1.0, 5.0, 1.0, step=0.5)
altura_logo_cm = st.sidebar.slider("Altura da Logo (em cm)", 2.0, 10.0, 5.0, step=0.5)

titulo_pequeno = st.text_input("Título Pequeno", value="OUTONO–INVERNO 2025")
titulo_grande = st.text_input("Título Grande", value="MUNDO DE INSPIRAÇÕES")

# Controle dos produtos
if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if pdf_file and not st.session_state.produtos:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
        tmp_input.write(pdf_file.read())
        tmp_input.flush()
        produtos_extraidos = extrair_informacoes(tmp_input.name)
        st.session_state.produtos = produtos_extraidos
        os.unlink(tmp_input.name)

st.subheader("Produtos")

# Botão para adicionar produto manualmente
if st.button("Adicionar Novo Produto"):
    st.session_state.produtos.append(("", ""))

# Listar todos os produtos para edição
produtos_editados = []
for idx, (desc, preco) in enumerate(st.session_state.produtos):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        novo_desc = st.text_input(f"Produto {idx+1}", value=desc, key=f"desc_{idx}")
    with col2:
        novo_preco = st.text_input(f"Preço {idx+1}", value=preco, key=f"preco_{idx}")
    with col3:
        if st.button("❌", key=f"excluir_{idx}"):
            st.session_state.produtos.pop(idx)
            st.rerun()

    if idx < len(st.session_state.produtos):
        produtos_editados.append((novo_desc, novo_preco))

# Atualizar a lista com os produtos editados
st.session_state.produtos = produtos_editados

# Gerar PDF
if st.button("Gerar PDF"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_output:
        logo_path = None
        if logo_file:
            logo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            logo_temp.write(logo_file.read())
            logo_temp.close()
            logo_path = logo_temp.name

        gerar_pdf(
            st.session_state.produtos,
            tmp_output.name,
            FORMATOS_PAGINA[formato_selecionado],
            logo_path,
            (margem_topo, margem_base, margem_lateral),
            altura_logo_cm,
            titulo_pequeno,
            titulo_grande
        )

        st.success("PDF gerado com sucesso!")

        with open(tmp_output.name, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

        with open(tmp_output.name, "rb") as f:
            st.download_button("Baixar PDF", f, file_name="orcamento_customizado.pdf")

        if logo_path:
            os.unlink(logo_path)
