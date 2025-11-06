# Correções do Docker - Resumo em Português

## Problema Relatado

O Dockerfile antigo utilizava múltiplas fases com imagens base de Rust e Node.js, exigia compilação do Aderyn a partir do código-fonte e frequentemente falhava por problemas de rede/SSL. Era necessário alinhar o build ao stack Python e garantir que todas as ferramentas (Slither, Mythril e Aderyn) estivessem presentes no container final.

## Correções Implementadas

### ✅ 1. Base da Imagem Atualizada

- A imagem base agora é `python:3.12-slim`, compatível com o servidor MCP escrito em Python.
- Dependências de sistema mínimas (build-essential, curl, libssl-dev, pkg-config) são instaladas apenas uma vez.

### ✅ 2. Ferramentas de Auditoria Empacotadas

- Slither (`slither-analyzer==0.10.0`) e Mythril (`mythril==0.24.8`) instalados via `pip` com flags de confiabilidade.
- Aderyn provisionado via [Cyfrinup](https://github.com/Cyfrin/up), baixando o binário oficial durante o build e validando com `aderyn --version`.
- Todas as ferramentas ficam disponíveis em `/opt/cyfrin/bin`, acessíveis para o usuário não-root `mcp`.

### ✅ 3. Otimizações de Build

- Shell padrão `/bin/bash -o pipefail` garante falhas imediatas em pipelines de instalação.
- Cache do `apt` removido ao final para reduzir o tamanho da imagem.
- Verificação final executa `slither --version`, `myth --version` e `aderyn --version` para garantir que tudo foi instalado corretamente.

### ✅ 4. Documentação Atualizada

- `README.md`, `DOCKER.md`, `QUICKSTART.md` e demais guias agora afirmam explicitamente que Aderyn está incluído.
- Instruções para instalação manual utilizam Cyfrinup (sem `cargo install`).
- Guias em português (`ALTERACOES.md`, `CORRECOES_DOCKER_PT.md`) alinhados com a nova arquitetura.

## Como Executar o Build sem Erros de Rede

### Solução Recomendada

```bash
make build-retry
```

O alvo pre-puxa `python:3.12-slim` e reconstrói a imagem automaticamente.

### Outras Estratégias

- **Rede lenta:** `docker pull python:3.12-slim && docker compose build`
- **Proxy corporativo:** exporte `HTTP_PROXY`/`HTTPS_PROXY` antes do build.
- **CI/CD:** `DOCKER_BUILDKIT=1 docker build --network=host -t farofino-mcp:latest .`
- **Timeout elevado:** `COMPOSE_HTTP_TIMEOUT=300 docker compose build`

Veja `DOCKER_NETWORK_TIMEOUT.md` para dicas detalhadas.

## Verificação

Após o build, execute:

```bash
make verify
```

Esse comando inicia o servidor MCP rapidamente e valida a presença de Slither, Mythril e Aderyn.

## Começar Agora

```bash
cd farofino-mcp
make build-retry
make verify
make run
```

## Referências

- `DOCKER.md` – Guia completo de uso
- `ALTERACOES.md` – Resumo das mudanças em português
- `DOCKER_NETWORK_TIMEOUT.md` – Soluções para problemas de rede
- `make help` – Lista de alvos disponíveis
