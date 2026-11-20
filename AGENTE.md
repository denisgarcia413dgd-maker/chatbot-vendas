# AGENTE EXTERNO - REGRAS DO PROJETO CHATBOT-VENDAS

Você é um agente de programação convidado para ajudar no projeto de dropshipping do Deivão.
Você tem liberdade para corrigir bugs, mas com responsabilidade. Siga estas regras sem exceção.

## 1. QUEM MANDA
- Dono do projeto: Dennis Garcia Duarte (Deivão)
- Você propõe, ele aprova. NUNCA faça merge direto na branch `main`.
- Sempre trabalhe em uma branch nova: `fix/agente-descricao-curta`
- Abra um Pull Request com resumo do que mudou.

## 2. O QUE VOCÊ PODE FAZER
- Ler todos os arquivos do projeto
- Corrigir bugs de sintaxe, indentação, imports
- Corrigir erros de `vendas.py`, `medico.py`, `aplicativo.py`
- Sugerir melhorias de performance e segurança
- Criar testes simples para validar a correção
- Chamar o `medico.py` para diagnosticar erros, sem expor dados

## 3. O QUE VOCÊ NUNCA PODE FAZER - PROIBIDO
- NUNCA pedir, exibir, copiar ou vazar senhas, tokens, chaves de API
- NUNCA colocar chave no código. Use sempre `os.environ.get("NOME_DA_CHAVE")`
- NUNCA mandar CPF, nome completo, endereço, telefone de cliente para API externa
- NUNCA apagar o banco de dados, coleções `orders`, `products`, `status_checks`
- NUNCA mexer em `requirements.txt` sem avisar o motivo no PR
- NUNCA fazer deploy no Render sem autorização do Deivão
- NUNCA inventar dados de cliente para testar

## 4. COMO ACESSAR CHAVES E SENHAS
- Você NÃO tem acesso direto às chaves.
- As chaves estão salvas no Render em Environment:
    - `ANTHROPIC_API_KEY` - chave do Claude
    - `MONGO_URI` - conexão MongoDB Atlas
- No código, acesse assim:
  ```python
  import os
  chave = os.environ.get("ANTHROPIC_API_KEY")
