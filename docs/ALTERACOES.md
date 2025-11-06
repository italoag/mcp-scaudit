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
- ✅ Target `verify` agora testa corretamente o servidor MCP Python
- ✅ Targets `verify` e `test` tratam Aderyn como opcional (caso instalação falhe por problemas de SSL)

### 2. Dockerfile

**Problema Original:**
- Comentários indicavam que Aderyn não era instalado devido a problemas de SSL
- Não havia ferramentas Rust/Cargo disponíveis para compilar Aderyn
- Imagem não continha todos os componentes necessários

**Correções:**
- ✅ Instalação de Rust/Cargo via rustup para suportar compilação do Aderyn
- ✅ Tentativa de instalação do Aderyn com tratamento gracioso de falhas
- ✅ Todas as ferramentas de auditoria agora configuradas:
  - **Slither** (Python) - sempre disponível ✓
  - **Mythril** (Python) - sempre disponível ✓
  - **Aderyn** (Rust) - instalado quando possível ✓
- ✅ Tratamento adequado de problemas de certificado SSL
- ✅ Mensagens claras sobre status da instalação

## Ferramentas Incluídas

### Sempre Disponíveis (Python)

1. **Slither** v0.10.0
   - Framework de análise estática para Solidity & Vyper
   - Instalação via pip sempre funciona

2. **Mythril** v0.24.8
   - Análise de execução simbólica para contratos Ethereum
   - Instalação via pip sempre funciona

### Opcionalmente Disponível (Rust)

3. **Aderyn**
   - Analisador estático baseado em Rust para Solidity
   - Instalado via `cargo install aderyn`
   - Pode não estar disponível em ambientes com restrições de SSL
   - Pode ser instalado manualmente após a construção se necessário

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
- Verificar disponibilidade do Aderyn (opcional)

### Executar o Servidor

```bash
make run
```

## Notas Importantes

### Sobre o Aderyn

O Aderyn é uma ferramenta baseada em Rust que requer compilação durante a construção da imagem Docker. Em alguns ambientes (CI/CD, redes corporativas), a instalação pode falhar devido a:

- Problemas com certificados SSL
- Restrições de rede
- Proxies com inspeção SSL

**Isto é esperado e não é um erro crítico.** As ferramentas principais (Slither e Mythril) estarão sempre disponíveis e funcionais.

### Instalação Manual do Aderyn

Se o Aderyn não estiver disponível na imagem construída, você pode instalá-lo manualmente:

```bash
# Entrar no container como root
docker run --rm -it --entrypoint /bin/bash --user root farofino-mcp:latest

# Dentro do container, instalar Aderyn
cargo install aderyn
```

### Verificar Ferramentas Disponíveis

Use o comando `check_tools` do servidor MCP para verificar quais ferramentas estão disponíveis em tempo de execução.

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
- Rust/Cargo para compilar Aderyn
- Slither e Mythril (sempre funcionais)
- Aderyn (quando ambiente permite instalação)

✅ **Tratamento robusto de erros** - falhas na instalação do Aderyn não impedem uso das outras ferramentas

✅ **Comandos atualizados** - sintaxe Docker Compose v2

✅ **Documentação completa** - guias em inglês (DOCKER_BUILD.md) e português (este arquivo)

## Documentação Adicional

- [DOCKER_BUILD.md](DOCKER_BUILD.md) - Guia completo de construção e uso (em inglês)
- [README.md](README.md) - Documentação principal do projeto
- [Dockerfile](Dockerfile) - Configuração da imagem Docker
- [Makefile](Makefile) - Comandos de automação
