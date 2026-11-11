# Prompt: vincular referências a páginas

Antes de qualquer execução ou alteração, leia integralmente e siga as [regras comuns](regras-comuns.md), resolvendo o link em relação à pasta deste prompt. Se não conseguir localizar ou ler esse arquivo, aborte sem executar a tarefa nem alterar arquivos e informe o impedimento.

Edite diretamente o conteúdo de `[ARQUIVO_MARKDOWN]` para complementar referências explícitas a páginas com links para as seções pertinentes.

## Trabalho

- Procure em todo o documento referências explícitas a páginas, como “mais detalhes na página X”. Considere variações de maiúsculas, acentos e abreviações, por exemplo: `página`, `páginas`, `pagina`, `paginas`, `pág.`, `pág`, `pag.`, `pg.`, `pg`, `p.`, `págs.`, `pgs.`, `pp.`, `page` e `pages`.
- Procure também expressões que possam acompanhar referências, como “consulte”, “veja”, “ver”, “vide” e “confira”, e outros termos, idiomas ou formas relevantes para o documento, inclusive possíveis variações introduzidas pela conversão. Esses termos são pistas, não uma lista exaustiva.
- Examine o contexto de cada ocorrência: não trate marcadores de página, números isolados, abreviações com outro significado ou expressões sem indicação explícita de página como referências a vincular.
- Junto de cada referência identificada, acrescente o título da seção relevante como um link Markdown. Exemplo: `mais detalhes na página 12 (consulte também [Nome da seção](#nome-da-secao))`.
- Para inferir a seção, use o conteúdo próximo à página mencionada. Prefira um título presente na própria página; se ela começar no meio de uma seção, use o título mais próximo que claramente abrange aquele conteúdo.
- Use o link automático do título Markdown existente como destino. Considere como o renderizador gera a âncora; não crie âncoras de página nem invente títulos.
- Não adicione âncoras aos marcadores de página `📄 \`Pág. N\``, nem altere esses marcadores para esse fim.
- Respeite eventuais ajustes de numeração aplicados pela ferramenta de conversão. Se não for possível identificar a página ou a seção com segurança, mantenha a referência original sem acrescentar um link incerto.
