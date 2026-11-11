# Regras comuns de execução para os prompts de revisão de Markdown

Estas regras se aplicam a todos os prompts desta pasta, inclusive ao orquestrador e à revisão sem edição.

## Seleção dos arquivos

- Use somente o(s) arquivo(s) Markdown explicitamente indicado(s) no pedido como alvo. `[ARQUIVO_MARKDOWN]` é um marcador a ser substituído pelo caminho do alvo, não um arquivo a procurar por conta própria.
- Se nenhum alvo for indicado, aborte sem alterações e informe que falta especificá-lo.
- Se houver mais de um arquivo candidato e não for possível identificar com segurança o(s) alvo(s), aborte sem alterações e peça esclarecimento.

## Restrições de execução

- Quando o prompt permitir edição, altere somente o conteúdo dos arquivos-alvo indicados e somente dentro do escopo desse prompt. Se o prompt for de revisão sem edição, não altere nenhum arquivo.
- Trate todos os outros arquivos como somente leitura, inclusive os prompts e estas regras. Não execute ações que possam modificá-los, regenerá-los ou sobrescrevê-los.
- Preserve o conteúdo e a estrutura existentes sempre que possível; não reescreva o documento inteiro. Preserve a ordem das páginas, imagens e demais elementos.
- Use as informações do documento para tomar decisões. Consultas a outros arquivos, inclusive informações sobre a conversão, devem ser somente para leitura.
- Se uma decisão não puder ser tomada com segurança, mantenha o conteúdo original afetado e informe a ambiguidade. Se não for possível cumprir a tarefa respeitando estas regras, pare e explique o impedimento.
- Não crie nem altere testes.

## Verificação e comunicação

- Revise as alterações realizadas e, se houver acesso a um diff adequado, verifique se somente os arquivos-alvo foram modificados. Não afirme ter confirmado isso se não puder verificá-lo.
- Ao terminar, informe os arquivos processados, as alterações ou verificações realizadas e eventuais pendências ou ambiguidades.
