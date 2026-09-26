## Agente Langgraph de relatórios sobre Síndrome Respiratória Aguda Grave (SRAG)


### Como executar
Você precisará dos serviços: Tavily by Nebius(Free Tier), Open AI API Key, Langfuse(Free Tier).

- Configure a .env usando a .env.example na raíz do diretório.
- Baixe o dataset de SRAG em [Open DATASUS](https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026/resource/d96d6348-083a-4184-a39a-794b5e8ec337). Transfira-o para a raíz do diretório.

Com o docker instalado, execute:
```bash
docker build -t api .
docker run -p 8000:8000 api
```

Use a rota POST http://localhost:8000/chat para iniciar o agente, com a mensagem no body da requisição.
### Arquitetura

O grafo do sistema agêntico modelado, está representado a seguir:
![grafo_SRAG_Agent](assets/grafo_SRAG_Agent.png)


### Decisões de projeto

**Importante**: Como as datas de registros contemplam até o dia 12 de dezembro de 2025, então para haver possibilidade de consulta em tempo real, houve uma adaptação em que o usuário consegue obter as métricas e notícias informando uma data de referência.

Como muitas das etapas eram passos bem definidos, somente no orquestrador houve a necessidade de implantar uma LLM, e o que seriam agentes, se transformaram em graph-based workflows.

A observabilidade foi totalmente apoiada no [Langfuse](https://langfuse.com/).

Como o agente não teve liberdade de construir e executar queries, não houve necessidade de tratamento de PII(dados sensíveis).

### Tools

Apesar dos workflows serem deterministicos, as tools foram construídas com a possibilidade de implementação em agentes ReAct.

As tools:
- taxa_aumento_casos
- taxa_mortalidade
- taxa_ocupacao_UTI
- taxa_vacinacao_populacao
- numero_casos_ultimo_mes
- numero_mensal_casos_ultimo_ano
- pesquisa_web  
