# Prompt executável: orquestrar a revisão de Markdown convertido

Antes de qualquer execução ou alteração, leia integralmente e siga as [regras comuns](regras-comuns.md), resolvendo o link em relação à pasta deste prompt. Se não conseguir localizar ou ler esse arquivo, aborte sem executar a tarefa nem alterar arquivos e informe o impedimento.

Use este arquivo como ponto de entrada para revisar e corrigir o(s) documento(s) Markdown indicado(s) no pedido. Delegue cada etapa aos prompts auxiliares desta pasta e aplique-os ao documento-alvo; não se limite a listar ou resumir as etapas.

## Delegação e execução

Para cada arquivo-alvo, leia e siga integralmente os prompts auxiliares abaixo, substituindo `[ARQUIVO_MARKDOWN]` pelo caminho desse alvo:

1. [Corrigir a hierarquia dos títulos](corrigir-hierarquia-dos-titulos.md): infira níveis coerentes e reúna títulos claramente partidos.
2. [Padronizar a capitalização dos títulos](padronizar-capitalizacao-dos-titulos.md): ajuste somente títulos inteiramente em maiúsculas.
3. [Vincular referências a páginas](vincular-referencias-a-paginas.md): acrescente links às seções identificáveis, sem criar links incertos.
4. [Revisar sem editar](revisar-markdown-sem-editar.md): confira o resultado após as etapas de edição e relate pendências.

Execute as etapas em ordem e conclua uma etapa antes de iniciar a próxima no mesmo arquivo. Se houver mais de um alvo explicitamente indicado, processe-os um por vez. Preserve os critérios de cada prompt auxiliar; a delegação não amplia o escopo de edição.
