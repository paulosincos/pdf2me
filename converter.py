import base64
import io
import json
import sys
import urllib.request
from pathlib import Path
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRef, ImageRefMode

def consultar_ollama_imagem(pil_image, prompt, modelo="gemma-geral"):
    """Envia uma imagem PIL diretamente para o Ollama e retorna a resposta em texto."""
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]
            }
        ],
        "max_tokens": 2500
    }

    req = urllib.request.Request(
        "http://localhost:11434/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        dados = json.loads(resp.read().decode("utf-8"))
        return dados["choices"][0]["message"]["content"].strip()

def main():
    if len(sys.argv) < 2:
        print("Erro: Informe o caminho do arquivo PDF.")
        print('Uso: pdf2md "arquivo.pdf" ["pasta_saida"] [offset_paginas]')
        sys.exit(1)

    caminho_pdf = Path(sys.argv[1]).resolve()

    if not caminho_pdf.is_file():
        print(f"Erro: O arquivo '{caminho_pdf}' não foi encontrado.")
        sys.exit(1)

    # Verifica argumentos opcionais: pasta de saída e offset de páginas
    pasta_saida = caminho_pdf.parent
    offset = 0

    for arg in sys.argv[2:]:
        if arg.lstrip("-").isdigit():
            offset = int(arg)
        else:
            pasta_saida = Path(arg).resolve()
            pasta_saida.mkdir(parents=True, exist_ok=True)

    arquivo_saida = pasta_saida / f"{caminho_pdf.stem}.md"
    pasta_imagens = pasta_saida / f"{caminho_pdf.stem}_imagens"

    # 1. Configura o pipeline na CPU
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.do_picture_description = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_page_images = True
    pipeline_options.images_scale = 2.0
    pipeline_options.enable_remote_services = True

    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=8,
        device=AcceleratorDevice.CPU
    )

    prompt_triagem = (
        "Analise esta imagem com atenção. "
        "Se ela contiver texto legível (parágrafos, tabelas, quadros, listas ou diagramas com palavras), "
        "transcreva TODO o texto visível na ordem correta de leitura em Markdown, mesmo que haja ilustrações junto. "
        "Responda APENAS com a palavra DESENHO somente se a imagem for puramente uma ilustração, foto ou arte sem texto relevante para leitura."
    )

    pipeline_options.picture_description_options = PictureDescriptionApiOptions(
        url="http://localhost:11434/v1/chat/completions",
        params=dict(
            model="gemma-geral",
            max_tokens=2500,
        ),
        prompt=prompt_triagem,
        timeout=120,
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    print(f"Iniciando conversão de: {caminho_pdf.name} (Offset de páginas: {offset})...")
    resultado = converter.convert(caminho_pdf)
    doc = resultado.document

    # 2. Filtra as figuras normais e salva os desenhos
    contador_desenhos = 0
    for picture in doc.pictures:
        descricao = ""
        if picture.meta and picture.meta.description:
            descricao = picture.meta.description.text.strip()

        if "DESENHO" in descricao.upper():
            contador_desenhos += 1
            pasta_imagens.mkdir(parents=True, exist_ok=True)
            nome_img = f"ilustracao_{contador_desenhos:03d}.png"
            caminho_img = pasta_imagens / nome_img

            img_pil = picture.get_image(doc)
            if img_pil:
                img_pil.save(caminho_img, format="PNG")
                picture.image = ImageRef(
                    mimetype="image/png",
                    dpi=144,
                    size=picture.image.size,
                    uri=Path(f"{pasta_imagens.name}/{nome_img}")
                )
            picture.meta.description = None
        else:
            picture.image = None

    # 3. Monta o Markdown página por página com âncoras
    blocos_markdown = []
    for num_pagina in sorted(doc.pages.keys()):
        page = doc.pages[num_pagina]
        pagina_livro = num_pagina - offset

        md_pagina = doc.export_to_markdown(
            page_no=num_pagina,
            image_mode=ImageRefMode.REFERENCED
        ).strip()

        texto_limpo = md_pagina.replace("<!-- image -->", "").strip()
        conteudo_bloco = ""

        if len(texto_limpo) >= 40 or "![" in md_pagina:
            conteudo_bloco = md_pagina
        elif page.image and page.image.pil_image:
            print(f"Resgatando página {num_pagina} (Livro p. {pagina_livro})...")
            resposta = consultar_ollama_imagem(page.image.pil_image, prompt_triagem)

            if resposta.strip().upper() == "DESENHO":
                contador_desenhos += 1
                pasta_imagens.mkdir(parents=True, exist_ok=True)
                nome_img = f"pagina_{num_pagina:03d}.png"
                page.image.pil_image.save(pasta_imagens / nome_img, format="PNG")
                prefixo = f"{texto_limpo}\n\n" if texto_limpo else ""
                conteudo_bloco = f"{prefixo}![Página {pagina_livro}]({pasta_imagens.name}/{nome_img})"
            else:
                prefixo = f"{texto_limpo}\n\n" if texto_limpo else ""
                conteudo_bloco = f"{prefixo}{resposta}"
        elif md_pagina:
            conteudo_bloco = md_pagina

        if conteudo_bloco:
            if pagina_livro > 0:
                conteudo_bloco = f"📄 `Pág. {pagina_livro}`\n\n{conteudo_bloco}"
            blocos_markdown.append(conteudo_bloco)

    # 4. Grava o arquivo final
    conteudo_final = "\n\n".join(blocos_markdown)
    arquivo_saida.write_text(conteudo_final, encoding="utf-8")

    print(f"Concluído! Markdown salvo em: {arquivo_saida}")
    if contador_desenhos > 0:
        print(f"Total de ilustrações salvas em: {pasta_imagens}")

if __name__ == "__main__":
    main()
