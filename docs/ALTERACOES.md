# Correções no Makefile e Dockerfile

## Problema Identificado

O projeto farofino-mcp é baseado em Python, mas o Makefile estava configurado incorretamente para utilizar imagens base de Rust e Node.js. Além disso, o Aderyn (ferramenta de auditoria baseada em Rust) não estava sendo incluído na imagem Docker.

## Alterações Realizadas

### 1. Makefile

**Problema Original:**

- O target `pull-images` estava baixando imagens `rust:1.75-slim` e `node:20-slim`
- Comandos usando `docker-compose` (sintaxe antiga)
- Verificações não testavam corretamente o servidor Python

**Correções:**

- ✅ Alterado `pull-images` para baixar `python:3.12-slim` (imagem correta para projeto Python)
- ✅ Atualizado todos os comandos `docker-compose` para `docker compose` (sintaxe v2)
- ✅ Target `verify` agora testa corretamente o servidor MCP Python e a disponibilidade de todas as ferramentas (incluindo Aderyn)

### 2. Dockerfile

**Problema Original:**

- Comentários indicavam que Aderyn não era instalado devido a problemas de SSL
- Não havia ferramentas Rust/Cargo disponíveis para compilar Aderyn
- Imagem não continha todos os componentes necessários

- ✅ Instalação automatizada via Cyfrinup para provisionar o Aderyn sem depender diretamente do cargo/crates.io
- ✅ Todas as ferramentas de auditoria agora configuradas e verificadas em tempo de build:
  - **Slither** (Python) - sempre disponível ✓
  - **Mythril** (Python) - sempre disponível ✓
  - **Aderyn** (Rust via Cyfrinup) - sempre disponível ✓
- ✅ Tratamento adequado de problemas de certificado SSL
- ✅ Mensagens claras sobre status da instalação

## Ferramentas Incluídas

### Ferramentas Sempre Disponíveis

1. **Slither** v0.10.0 (Python)
   - Framework de análise estática para Solidity & Vyper
   - Instalado via pip com flags de SSL resilientes

2. **Mythril** v0.24.8 (Python)
   - Análise de execução simbólica para contratos Ethereum
   - Instalado via pip com flags de SSL resilientes

3. **Aderyn** (Rust)
   - Analisador estático baseado em Rust para Solidity
   - Instalado via [Cyfrinup](https://github.com/Cyfrin/up) dentro da imagem Docker
   - Disponível imediatamente para todos os usuários do container

## Como Usar

### Construir a Imagem

```bash
# Método recomendado
make build

# Ou com pré-download das imagens base
make build-retry

# Ou sem cache
make build-no-cache
```

### Verificar Instalação

```bash
make verify
```

Isto irá:

- Testar inicialização do servidor MCP
- Verificar disponibilidade do Slither ✓
- Verificar disponibilidade do Mythril ✓
- Verificar disponibilidade do Aderyn ✓

### Executar o Servidor

```bash
make run
```

## Notas Importantes

### Sobre o Aderyn

O Aderyn agora é instalado durante o build através do Cyfrinup, que baixa o binário oficial diretamente do repositório da Cyfrin. Isso evita problemas de compilação e garante que a versão mais recente esteja disponível na imagem final. Caso seu ambiente bloqueie downloads externos, utilize um proxy confiável ou faça o pré-download do script do Cyfrinup.

### Verificar Ferramentas Disponíveis

Use o comando `check_tools` do servidor MCP para verificar e registrar as versões disponíveis em tempo de execução.

## Comandos do Makefile

| Comando | Descrição |
|---------|-----------|
| `make help` | Mostra todos os comandos disponíveis |
| `make pull-images` | Baixa imagem base Python |
| `make build` | Constrói a imagem Docker |
| `make build-no-cache` | Constrói sem usar cache |
| `make build-retry` | Constrói com retry para problemas de rede |
| `make run` | Executa o servidor MCP |
| `make verify` | Verifica instalação de ferramentas |
| `make test` | Executa testes de saúde |
| `make clean` | Remove imagens e containers |
| `make logs` | Mostra logs do container |
| `make size` | Mostra tamanho da imagem |

## Resumo das Correções

✅ **Makefile agora está aderente ao projeto Python** - usa `python:3.12-slim` ao invés de imagens Rust/Node

✅ **Dockerfile inclui todos os componentes necessários**:

- Slither e Mythril (sempre funcionais)
- Aderyn provisionado via Cyfrinup (sem dependência de compilação local)
- Ferramentas instaladas com verificação de versão durante o build

✅ **Tratamento robusto de erros** - logs claros em caso de falha no download do Cyfrinup ou das ferramentas, com instruções de retry

✅ **Comandos atualizados** - sintaxe Docker Compose v2

✅ **Documentação completa** - guias em inglês (DOCKER_BUILD.md) e português (este arquivo)

## Documentação Adicional

- [DOCKER_BUILD.md](DOCKER_BUILD.md) - Guia completo de construção e uso (em inglês)
- [README.md](README.md) - Documentação principal do projeto
- [Dockerfile](Dockerfile) - Configuração da imagem Docker
- [Makefile](Makefile) - Comandos de automação
