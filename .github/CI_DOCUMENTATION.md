# CI/CD - Test, Build and Release

Este documento descreve o fluxo de Integração Contínua (CI) e Entrega Contínua (CD) do projeto. O pipeline automatiza a execução de testes, o versionamento semântico, a construção da imagem Docker e a publicação no Azure Container Registry (ACR).

---

## 🚀 Visão Geral do Fluxo

Toda vez que uma alteração de código é enviada para a branch `master`, o GitHub Actions inicia automaticamente o workflow (`azure-identity` runner). O processo passa pelas seguintes etapas:

1. **Checkout e Configuração:** Baixa o código mais recente e prepara o ambiente com Python 3.13.
2. **Testes Automatizados (CI):** Instala as dependências de teste e executa o `pytest`. Se os testes falharem, o pipeline é interrompido imediatamente, garantindo que código quebrado não seja publicado.
3. **Versionamento (Bump Version):** Lê o histórico de commits, calcula automaticamente a próxima versão e cria uma nova Tag (ex: `v1.2.0`).
4. **Build e Push (CD):** Faz login no Azure, constrói a imagem Docker da aplicação e faz o push para o ACR com duas tags: a versão específica gerada e a tag `latest`.
5. **Release Note:** Gera uma página de Release automática no repositório do GitHub detalhando o que mudou com base nos commits aprovados.

---

## 🛑 Gatilhos (Triggers) e Exceções

O pipeline é acionado automaticamente **apenas em eventos de `push` na branch `master`** (o que inclui o *merge* de Pull Requests).

**Exceções:**
Alterações focadas exclusivamente na documentação não disparam o pipeline para economizar recursos. Arquivos ignorados:
- `README.md`
- `Readme.md`
- `readme.md`
- `CI_DOCUMENTATION.md`

---

## 🏷️ Padrão de Commits e Versionamento Semântico

Este pipeline utiliza o **Conventional Commits** para determinar qual será o próximo número de versão da aplicação de forma matemática e automática. 

O versionamento segue o formato **`vX.Y.Z`** (Major.Minor.Patch). Para que o pipeline incremente a versão corretamente, as mensagens dos seus commits (ou o título do seu Pull Request ao fazer o Squash/Merge) devem seguir as regras abaixo:

### 1. Atualização de Patch (`v1.0.0` ➔ `v1.0.1`)
Utilizado para **correções de bugs**. O commit deve começar com `fix:`.
* **Exemplo:** `fix: resolve timeout na conexao com o banco`

### 2. Atualização Minor (`v1.0.0` ➔ `v1.1.0`)
Utilizado para **novas funcionalidades** que não quebram a compatibilidade com o que já existe. O commit deve começar com `feat:`.
* **Exemplo:** `feat: adiciona nova rota /generic`

### 3. Atualização Major (`v1.0.0` ➔ `v2.0.0`)
Utilizado para **alterações críticas** que quebram a compatibilidade (Breaking Changes). Deve conter `BREAKING CHANGE:` no corpo do commit ou um `!` no prefixo.
* **Exemplo:** `feat!: altera formato de resposta da API de xml para json`

> ⚠️ **ATENÇÃO AO COMPORTAMENTO PADRÃO (DEFAULT BUMP):**
> O pipeline está configurado com `default_bump: minor`. Isso significa que se uma alteração for enviada para a `master` com uma mensagem de commit genérica, que **não siga** os padrões acima (ex: `atualizando rotas`, `refatoracao do codigo`), o sistema assumirá por padrão que é uma nova funcionalidade e **fará um salto de Minor** (ex: de `v1.0.0` direto para `v1.1.0`). Portanto, manter o padrão nas mensagens é fundamental para um versionamento coerente.

---

## 🐳 Infraestrutura e Container Registry

As imagens geradas são armazenadas no **Azure Container Registry (ACR)** da organização.

* **Registry:** `acrapplications.azurecr.io`
* **Repositório:** `woopi-operacoes/monitoring-api`

A imagem sempre estará disponível em duas versões após um pipeline bem-sucedido:
1. Pela tag exata da versão (ex: `acrapplications.azurecr.io/woopi-operacoes/monitoring-api:v1.0.0`) - *Recomendado para estabilidade.*
2. Pela tag flutuante `latest` (ex: `acrapplications.azurecr.io/woopi-operacoes/monitoring-api:latest`) - *Sempre aponta para o último build feito na master.*