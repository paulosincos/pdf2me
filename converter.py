import sys
from pathlib import Path
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

def main():
    if len(sys.argv) < 2:
        print("Erro: Informe o caminho do arquivo PDF.")
        print('Uso: pdf2md "caminho/do/arquivo.pdf" ["pasta/de/saida"]')
        sys.exit(1)

    caminho_pdf = Path(sys.argv[1]).resolve()

    if not caminho_pdf.is_file():
        print(f"Erro: O arquivo '{caminho_pdf}' não foi encontrado.")
        sys.exit(1)

    if len(sys.argv) >= 3:
        pasta_saida = Path(sys.argv[2]).resolve()
        pasta_saida.mkdir(parents=True, exist_ok=True)
    else:
        pasta_saida = caminho_pdf.parent

    arquivo_saida = pasta_saida / f"{caminho_pdf.stem}.md"
    pasta_imagens = pasta_saida / f"{caminho_pdf.stem}_imagens"

    # 1. Configura o pipeline na CPU e ativa o recorte das imagens
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.do_picture_description = True
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0
    pipeline_options.enable_remote_services = True

    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=8,
        device=AcceleratorDevice.CPU
    )

    # 2. Prompt inteligente: separa desenhos artísticos de imagens com texto
    prompt_triagem = (
        "Analise esta imagem. Se ela for um desenho artístico, foto ou ilustração sem texto relevante para leitura, "
        "responda APENAS com a palavra: DESENHO. "
        "Caso contrário, se houver texto, gráfico ou diagrama informativo, transcreva todo o texto visível."
    )

    pipeline_options.picture_description_options = PictureDescriptionApiOptions(
        url="http://localhost:11434/v1/chat/completions",
        params=dict(
            model="gemma-geral",
            max_tokens=1024,
        ),
        prompt=prompt_triagem,
        timeout=120,
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    print(f"Iniciando conversão de: {caminho_pdf.name}...")
    resultado = converter.convert(caminho_pdf)
    doc = resultado.document

    # 3. Filtra os desenhos e limpa o que não deve ser salvo como imagem
    contador_desenhos = 0
    for picture in doc.pictures:
        descricao = ""
        if picture.meta and picture.meta.description:
            descricao = picture.meta.description.text.strip()

        if "DESENHO" in descricao.upper():
            contador_desenhos += 1
            # Limpa a descrição em meta para a palavra "DESENHO" não ir para o Markdown
            picture.meta.description = None
        else:
            # Remove a imagem binária das figuras que têm texto para o Docling não salvá-las como PNG
            picture.image = None

    # 4. Salva o Markdown e ajusta os caminhos das imagens para relativos
    if contador_desenhos > 0:
        doc.save_as_markdown(
            filename=arquivo_saida,
            artifacts_dir=pasta_imagens,
            image_mode=ImageRefMode.REFERENCED
        )

        # Lê o Markdown gerado e troca o caminho absoluto (file:///...) pelo caminho relativo limpo
        conteudo_md = arquivo_saida.read_text(encoding="utf-8")
        uri_absoluta = pasta_imagens.as_uri()
        conteudo_md = conteudo_md.replace(uri_absoluta, "./" + pasta_imagens.name)
        arquivo_saida.write_text(conteudo_md, encoding="utf-8")
    else:
        doc.save_as_markdown(
            filename=arquivo_saida,
            image_mode=ImageRefMode.PLACEHOLDER
        )

    print(f"Concluído! Markdown salvo em: {arquivo_saida}")
    if contador_desenhos > 0:
        print(f"Foram salvas {contador_desenhos} ilustrações em: {pasta_imagens}")

if __name__ == "__main__":
    main()
