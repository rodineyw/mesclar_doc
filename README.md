# 📄 Mesclador Inteligente de PDFs

> **Automatize a organização dos seus documentos PDF com detecção inteligente de similaridade por números e textos!**

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

## 🚀 O que faz este programa?

O **Mesclador Inteligente de PDFs** é uma ferramenta que identifica automaticamente arquivos PDF relacionados baseado em:

- **📊 Números sequenciais** (ex: processos, protocolos, códigos)
- **📝 Similaridade textual** nos nomes dos arquivos
- **🔗 Agrupamento automático** e mesclagem em um único PDF

### Exemplo Prático:
```
📁 Pasta de entrada:
├── Sentença_249023_inicial.pdf
├── Parecer_249023_técnico.pdf
├── Citação_249023_final.pdf
├── Contrato_1390_João.pdf
├── Aditivo_1390_alterações.pdf

📁 Resultado:
├── Mesclado_249023.pdf (3 arquivos mesclados)
├── Mesclado_1390.pdf (2 arquivos mesclados)
```

## ✨ Características Principais

### 🎯 Detecção Inteligente
- **Números de 3+ dígitos**: Detecta automaticamente códigos, protocolos, processos
- **Similaridade textual**: Compara palavras-chave nos nomes
- **Algoritmo híbrido**: Combina análise numérica (80%) + textual (20%)

### 🛡️ Tratamento Robusto
- **PDFs criptografados**: Detecta e pula automaticamente
- **Nomes duplicados**: Sistema de numeração automática
- **Log detalhado**: Rastreamento completo do processo
- **Interface gráfica**: Fácil de usar, sem linha de comando

### ⚡ Performance
- **Processamento em lote**: Analisa centenas de arquivos
- **Memória otimizada**: Processamento eficiente de arquivos grandes
- **Executável standalone**: Não precisa do Python instalado

## 📦 Instalação

### Opção 1: Executável Pronto (Recomendado)
1. Baixe o arquivo `MescladorPDF.exe` da seção [Releases](../../releases)
2. Execute diretamente - não precisa instalar nada!

### Opção 2: Executar o Código Python
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/mesclador-pdf.git
cd mesclador-pdf

# Instale as dependências
pip install pypdf tkinter

# Execute o programa
python mesclador.py
```

### Opção 3: Compilar o Executável
```bash
# Instale o PyInstaller
pip install pyinstaller pypdf

# Compile usando o arquivo .spec
pyinstaller MescladorPDF.spec

# O executável estará em dist/MescladorPDF.exe
```

## 🎮 Como Usar

### Interface Gráfica
1. **📁 Selecione a pasta** contendo os arquivos PDF
2. **🎚️ Ajuste o nível de similaridade** (padrão: 60%)
3. **▶️ Clique em "Iniciar Mesclagem"**
4. **✅ Arquivos mesclados** serão salvos na mesma pasta

### Configurações de Similaridade
- **90-100%**: Apenas arquivos muito similares
- **70-89%**: Similaridade moderada (recomendado)
- **50-69%**: Similaridade baixa, mais agrupamentos
- **10-49%**: Muito permissivo, use com cuidado

## 🔧 Funcionalidades Técnicas

### Algoritmo de Detecção
```python
# Extração de números sequenciais
números = re.findall(r'\d{3,}', nome_arquivo)

# Normalização de texto
texto = remover_acentos_e_especiais(nome_arquivo)

# Cálculo de similaridade híbrida
if números_em_comum:
    similaridade = 0.8 * sim_numérica + 0.2 * sim_textual
else:
    similaridade = sim_textual
```

### Estrutura do Projeto
```
mesclador-pdf/
├── mesclador.py           # Código principal
├── MescladorPDF.spec      # Configuração PyInstaller
├── requirements.txt       # Dependências
├── README.md             # Esta documentação
├── LICENSE              # Licença MIT
└── exemplos/            # Arquivos de teste
```

## 📊 Exemplos de Uso

### Documentos Jurídicos
```
Processo_12345_petição_inicial.pdf
Processo_12345_contestação.pdf
Processo_12345_sentença.pdf
→ Resultado: Mesclado_12345.pdf
```

### Contratos Empresariais
```
Contrato_2024001_João_Silva.pdf
Aditivo_2024001_alteração.pdf
Rescisão_2024001_final.pdf
→ Resultado: Mesclado_2024001.pdf
```

### Relatórios Técnicos
```
Relatório_Projeto_Alpha_v1.pdf
Relatório_Projeto_Alpha_v2.pdf
Relatório_Projeto_Alpha_final.pdf
→ Resultado: Mesclado_Alpha.pdf (por similaridade textual)
```

## 🐛 Solução de Problemas

### ❌ "Módulo pypdf não encontrado"
```bash
pip install pypdf
# ou use o executável que já inclui tudo
```

### ❌ "Menos de 2 PDFs encontrados"
- Verifique se há arquivos .pdf na pasta selecionada
- Confirme se os arquivos não estão corrompidos

### ❌ "PDF criptografado ignorado"
- O programa pula PDFs com senha automaticamente
- Remova a proteção antes de processar

### ❌ Antivírus bloqueia o executável
- Isso é normal com executáveis do PyInstaller
- Adicione uma exceção no antivírus

## 🤝 Como Contribuir

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. Abra um **Pull Request**

### Ideias para Contribuições
- [ ] Suporte a outros formatos (Word, Excel)
- [ ] Interface web
- [ ] Modo linha de comando
- [ ] Detecção de arquivos duplicados
- [ ] Preview dos arquivos antes da mesclagem
- [ ] Suporte a pastas recursivas

## 📋 Roadmap

### v2.0 (Próxima versão)
- [ ] **Interface modernizada** com tema escuro
- [ ] **Arrastar e soltar** arquivos
- [ ] **Preview** dos grupos antes da mesclagem
- [ ] **Configurações avançadas** de detecção

### v2.1 (Futuro)
- [ ] **API REST** para integração
- [ ] **Processamento em nuvem**
- [ ] **Machine Learning** para detecção mais precisa

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Rod** - [GitHub](https://github.com/rodineyw) | [LinkedIn](https://linkedin.com/in/rodineyw)

---

## 📈 Estatísticas do Projeto

![GitHub stars](https://img.shields.io/github/stars/rodineyw/mesclador-pdf)
![GitHub forks](https://img.shields.io/github/forks/rodineyw/mesclador-pdf)
![GitHub issues](https://img.shields.io/github/issues/rodineyw/mesclador-pdf)

---

**⭐ Se este projeto te ajudou, deixe uma estrela no repositório!**
