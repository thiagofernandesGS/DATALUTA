# 📌 DATALUTA

Projeto desenvolvido no PET Computação da Universidade Federal do Mato Grosso do Sul (UFMS) em colaboração com a Universidade de Brasília (UnB)

---

## 🚀 Tecnologias

Este projeto foi desenvolvido com as seguintes tecnologias:

- Python 3.9
- Spacy

---

## 📦 Pré-requisitos

Antes de começar, você vai precisar ter instalado:

- [Python](https://www.python.org/)

---

## 🔧 Instalação

Criar o ambiente virtual (opcional):

```bash
python -m venv .venv
```

Ativar o ambiente virtual (opcional):
```bash
# Ative no Windows
.venv\Scripts\activate

# Ou no Linux/macOS
source .venv/bin/activate
```

Instalação do SpaCy com versões já compiladas:

```bash
pip install spacy==3.5.4 --prefer-binary
```

Verificar se a instalação ocorreu com êxito:

```bash
python -m spacy info
```

Pacote de idioma grande utilizado:

```bash
python -m spacy download pt_core_news_lg
```

## ▶️ Como usar

Após instalar, execute o seguinte comando para iniciar o projeto:

```bash
python codigoAtual.py
```

## 📝 Convenção de Commits

Este projeto segue a convenção [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/), para manter um histórico de mudanças claro e organizado.

### Formato dos commits

```bash
<tipo>(escopo opcional): descrição breve
```

### Tipos suportados

| Tipo       | Descrição                                                                 |
|------------|---------------------------------------------------------------------------|
| `feat`     | Adição de nova funcionalidade                                             |
| `fix`      | Correção de bug                                                           |
| `docs`     | Mudanças apenas na documentação                                           |
| `style`    | Alterações de formatação, como identação, sem alterar lógica              |
| `refactor` | Refatorações (alteração de código que não corrige nem adiciona funcionalidade) |
| `test`     | Adição ou alteração de testes                                             |
| `chore`    | Tarefas de manutenção (ex: build, configs, atualização de dependências)   |
