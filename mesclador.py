import os
import re
import unicodedata
import logging
from logging.handlers import RotatingFileHandler
from difflib import SequenceMatcher
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, DoubleVar
from pypdf import PdfReader, PdfWriter

APP_NAME = "MescladorPDF"
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "mesclador.log"

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)

_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(_console)

_file = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
_file.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(_file)


def _extrair_numeros_sequenciais(nome_arquivo: str) -> list:
    """
    Extrai sequências numéricas de 3+ dígitos do nome do arquivo.
    Ex: 'Sentença 249023 final' -> ['249023']
    """
    # Remove extensão
    base = os.path.splitext(nome_arquivo)[0]
    # Encontra sequências de 3 ou mais dígitos
    numeros = re.findall(r'\d{3,}', base)
    return numeros


def _normalizar_texto_sem_numeros(nome_arquivo: str) -> str:
    """
    Normaliza o texto removendo números, acentos e caracteres especiais
    para comparação de similaridade textual.
    """
    base = os.path.splitext(nome_arquivo)[0]
    
    # Remove acentos e caracteres especiais
    base = unicodedata.normalize("NFKD", base).encode("ASCII", "ignore").decode("ASCII")
    
    # Remove números
    base = re.sub(r'\d+', ' ', base)
    
    # Remove caracteres especiais e substitui por espaços
    base = re.sub(r'[\W_]+', ' ', base)
    
    # Remove espaços múltiplos
    base = re.sub(r'\s+', ' ', base)
    
    return base.strip().lower()


def _calcular_similaridade_inteligente(arquivo1: str, arquivo2: str) -> dict:
    """
    Calcula similaridade considerando tanto números quanto texto.
    Retorna um dicionário com diferentes métricas de similaridade.
    """
    # Extrai números sequenciais de ambos os arquivos
    nums1 = _extrair_numeros_sequenciais(arquivo1)
    nums2 = _extrair_numeros_sequenciais(arquivo2)
    
    # Extrai texto normalizado
    texto1 = _normalizar_texto_sem_numeros(arquivo1)
    texto2 = _normalizar_texto_sem_numeros(arquivo2)
    
    # Calcula similaridade textual
    similaridade_texto = SequenceMatcher(None, texto1, texto2).ratio()
    
    # Calcula similaridade numérica
    numeros_comuns = set(nums1) & set(nums2)
    if nums1 or nums2:
        # Se há números em comum, alta similaridade numérica
        if numeros_comuns:
            similaridade_numerica = 1.0
        else:
            similaridade_numerica = 0.0
    else:
        # Se nenhum arquivo tem números, considera neutro
        similaridade_numerica = 0.0
    
    # Calcula similaridade combinada com peso maior para números
    if numeros_comuns:
        # Se tem números em comum, prioriza isso
        similaridade_final = 0.8 * similaridade_numerica + 0.2 * similaridade_texto
    else:
        # Se não tem números em comum, usa só texto
        similaridade_final = similaridade_texto
    
    return {
        'final': similaridade_final,
        'texto': similaridade_texto,
        'numerica': similaridade_numerica,
        'numeros_arquivo1': nums1,
        'numeros_arquivo2': nums2,
        'numeros_comuns': list(numeros_comuns)
    }


def _criar_pasta_mesclados(diretorio_base: Path) -> Path:
    """
    Cria a pasta 'Mesclados' no diretório base se não existir.
    Retorna o caminho da pasta criada.
    """
    pasta_mesclados = diretorio_base / "Mesclados"
    pasta_mesclados.mkdir(exist_ok=True)
    logger.info("Pasta criada/verificada: %s", pasta_mesclados)
    return pasta_mesclados


def _configurar_log_pasta_mesclados(pasta_mesclados: Path):
    """
    Configura um logger específico para salvar erros na pasta Mesclados.
    """
    log_file_mesclados = pasta_mesclados / "log_erros_mesclagem.txt"
    
    # Remove handler anterior se existir
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler) and "mesclagem" in str(handler.baseFilename):
            logger.removeHandler(handler)
            handler.close()
    
    # Adiciona novo handler para a pasta Mesclados
    error_handler = logging.FileHandler(log_file_mesclados, mode='a', encoding='utf-8')
    error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    error_handler.setLevel(logging.WARNING)  # Só warnings e erros
    logger.addHandler(error_handler)
    
    logger.info("Log de erros configurado: %s", log_file_mesclados)
    return log_file_mesclados


def _proximo_nome_disponivel(caminho_saida: Path) -> Path:
    """Encontra próximo nome disponível se arquivo já existir"""
    if not caminho_saida.exists():
        return caminho_saida
    stem, suffix = caminho_saida.stem, caminho_saida.suffix
    n = 2
    while True:
        cand = caminho_saida.with_name(f"{stem} ({n}){suffix}")
        if not cand.exists():
            return cand
        n += 1


def encontrar_e_mesclar_similares(diretorio: str, limiar_similaridade: float = 0.7):
    """
    Versão melhorada que detecta similaridade por números e texto.
    Salva arquivos mesclados na pasta 'Mesclados' e logs de erro na mesma pasta.
    """
    try:
        dirpath = Path(diretorio)
        if not dirpath.exists() or not dirpath.is_dir():
            messagebox.showerror("Erro", "Pasta inválida.")
            logger.error("Pasta inválida: %s", diretorio)
            return

        logger.info("=== INICIANDO PROCESSO DE MESCLAGEM ===")
        logger.info("Diretório de origem: %s", diretorio)

        # Criar pasta 'Mesclados'
        pasta_mesclados = _criar_pasta_mesclados(dirpath)
        
        # Configurar log específico para a pasta Mesclados
        log_file_mesclados = _configurar_log_pasta_mesclados(pasta_mesclados)

        arquivos_pdf = sorted([f for f in os.listdir(diretorio) if f.lower().endswith(".pdf")])
        logger.info("Encontrados %d arquivos PDF", len(arquivos_pdf))

        if len(arquivos_pdf) < 2:
            logger.warning("Menos de 2 PDFs encontrados.")
            messagebox.showwarning("Aviso", "Precisa de ao menos 2 PDFs na pasta para mesclar.")
            return

        processados = set()
        grupos_mesclados = 0
        arquivos_com_erro = []

        logger.info("Analisando %d arquivos PDF com limiar de %.0f%%...", len(arquivos_pdf), limiar_similaridade * 100)

        for i in range(len(arquivos_pdf)):
            atual = arquivos_pdf[i]
            if atual in processados:
                continue

            grupo = [atual]
            
            # Compara com todos os outros arquivos
            for j in range(i + 1, len(arquivos_pdf)):
                outro = arquivos_pdf[j]
                if outro in processados:
                    continue
                
                # Calcula similaridade inteligente
                similaridade = _calcular_similaridade_inteligente(atual, outro)
                
                logger.debug("Comparando '%s' x '%s': %.2f%% (texto: %.2f%%, números: %s)", 
                           atual, outro, 
                           similaridade['final'] * 100,
                           similaridade['texto'] * 100,
                           similaridade['numeros_comuns'])
                
                if similaridade['final'] >= limiar_similaridade:
                    grupo.append(outro)
                    logger.info("Adicionado ao grupo: %s (similaridade: %.0f%%, números comuns: %s)", 
                              outro, similaridade['final'] * 100, similaridade['numeros_comuns'])

            # Se encontrou grupo com mais de 1 arquivo
            if len(grupo) > 1:
                logger.info("=== GRUPO ENCONTRADO ===")
                logger.info("Arquivos: %s", grupo)
                
                # Mostra detalhes da análise
                primeiro = grupo[0]
                nums_primeiro = _extrair_numeros_sequenciais(primeiro)
                logger.info("Números de referência (%s): %s", primeiro, nums_primeiro)
                
                processados.update(grupo)

                # Mescla os PDFs
                writer = PdfWriter()
                adicionados = 0
                
                for pdf_file in grupo:
                    caminho = dirpath / pdf_file
                    try:
                        reader = PdfReader(str(caminho))
                        if getattr(reader, "is_encrypted", False):
                            logger.warning("PDF criptografado ignorado: %s", pdf_file)
                            continue
                        
                        for page in reader.pages:
                            writer.add_page(page)
                        adicionados += 1
                        logger.info("Adicionado: %s (%d páginas)", pdf_file, len(reader.pages))
                        
                    except Exception as e_file:
                        logger.error("Falha ao ler '%s': %s", pdf_file, e_file, exc_info=True)

                # Salva o arquivo mesclado se tiver pelo menos 2 PDFs válidos
                if adicionados >= 2:
                    # Nome baseado no primeiro arquivo + números encontrados
                    nums_referencia = _extrair_numeros_sequenciais(grupo[0])
                    if nums_referencia:
                        nome_saida = f"Mesclado_{nums_referencia[0]}.pdf"
                    else:
                        nome_saida = f"{Path(grupo[0]).stem}_mesclado.pdf"
                    
                    # Salvar na pasta 'Mesclados'
                    caminho_saida = _proximo_nome_disponivel(pasta_mesclados / nome_saida)
                    logger.info("Salvando arquivo mesclado: %s", caminho_saida.name)
                    
                    try:
                        with open(caminho_saida, "wb") as f:
                            writer.write(f)
                        
                        logger.info("✓ Arquivo criado com sucesso: %s", caminho_saida.name)
                        logger.info("📁 Localização: %s", caminho_saida.relative_to(dirpath))
                        
                    except Exception as e_save:
                        logger.error("❌ Erro ao salvar arquivo '%s': %s", nome_saida, e_save)
                        arquivos_com_erro.append(f"Erro ao salvar {nome_saida}: {str(e_save)}")
                        continue
                        
                else:
                    logger.warning("⚠️ Grupo descartado. Menos de 2 PDFs válidos após processamento.")
                    if len(grupo) > 1:
                        arquivos_com_erro.append(f"Grupo {grupo} descartado: PDFs inválidos ou criptografados")

                grupos_mesclados += 1
                logger.info("=== FIM DO GRUPO %d ===", grupos_mesclados)

        # Resultado final e relatório
        logger.info("=== PROCESSO CONCLUÍDO ===")
        
        # Gerar relatório de erros se houver
        if arquivos_com_erro:
            relatorio_erros = pasta_mesclados / "relatorio_erros.txt"
            try:
                with open(relatorio_erros, 'w', encoding='utf-8') as f:
                    f.write(f"RELATÓRIO DE ERROS - MESCLAGEM DE PDFs\n")
                    f.write(f"{'=' * 50}\n")
                    f.write(f"Data/Hora: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
                    f.write(f"Pasta processada: {dirpath}\n")
                    f.write(f"Total de arquivos processados: {len(arquivos_pdf)}\n")
                    f.write(f"Grupos criados com sucesso: {grupos_mesclados}\n")
                    f.write(f"Erros encontrados: {len(arquivos_com_erro)}\n\n")
                    f.write("DETALHES DOS ERROS:\n")
                    f.write("-" * 30 + "\n")
                    for i, erro in enumerate(arquivos_com_erro, 1):
                        f.write(f"{i}. {erro}\n")
                    f.write(f"\nVerifique também o log completo: {log_file_mesclados.name}\n")
                
                logger.warning("📄 Relatório de erros gerado: %s", relatorio_erros.name)
                
            except Exception as e_relatorio:
                logger.error("Erro ao gerar relatório: %s", e_relatorio)

        if grupos_mesclados > 0:
            mensagem_sucesso = f"""✅ MESCLAGEM CONCLUÍDA!

📊 Resultado:
• {grupos_mesclados} grupo(s) de PDFs mesclados
• Arquivos salvos na pasta: 'Mesclados'
• Total de PDFs processados: {len(arquivos_pdf)}"""

            if arquivos_com_erro:
                mensagem_sucesso += f"""

⚠️ Atenção:
• {len(arquivos_com_erro)} arquivo(s) com problemas
• Verifique o relatório de erros na pasta 'Mesclados'"""

            logger.info("CONCLUÍDO! %d grupo(s) processado(s) com sucesso.", grupos_mesclados)
            messagebox.showinfo("Mesclagem Concluída", mensagem_sucesso)
        else:
            logger.info("Nenhum grupo encontrado com similaridade >= %.0f%%", limiar_similaridade * 100)
            mensagem = f"""ℹ️ PROCESSO CONCLUÍDO

Nenhum grupo atingiu a similaridade mínima de {limiar_similaridade*100:.0f}%.

💡 Sugestões:
• Diminua o nível de similaridade
• Verifique se os arquivos têm elementos em comum
• Consulte o log na pasta 'Mesclados' para mais detalhes"""
            
            messagebox.showinfo("Nenhum Grupo Encontrado", mensagem)

    except Exception as e:
        logger.error("❌ ERRO CRÍTICO no processo: %s", e, exc_info=True)
        messagebox.showerror("Erro Crítico", 
                           f"Ocorreu um erro inesperado durante o processamento:\n\n{str(e)}\n\n"
                           f"Verifique o log de erros para mais detalhes.")
        
        # Tentar salvar erro crítico na pasta Mesclados se possível
        try:
            if 'pasta_mesclados' in locals():
                erro_critico = pasta_mesclados / "erro_critico.txt"
                with open(erro_critico, 'w', encoding='utf-8') as f:
                    f.write(f"ERRO CRÍTICO - {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n")
                    f.write(f"{'=' * 50}\n")
                    f.write(f"Diretório: {diretorio}\n")
                    f.write(f"Erro: {str(e)}\n")
                    f.write(f"Trace completo disponível no log principal.\n")
        except:
            pass  # Se não conseguir salvar, pelo menos o erro principal foi logado


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mesclador Inteligente de PDFs")
        self.geometry("580x380")

        self.diretorio_selecionado = ""
        self.limiar_var = DoubleVar(value=0.6)  # Baixei pra 60% como padrão

        frame = ttk.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)

        # Título
        titulo = ttk.Label(frame, text="Mesclador Inteligente de PDFs", 
                          font=("Arial", 12, "bold"))
        titulo.pack(pady=5)

        # Seleção de pasta
        ttk.Button(frame, text="Selecionar Pasta com PDFs", 
                  command=self.selecionar_pasta).pack(pady=10, fill="x")
        
        self.lbl_pasta = ttk.Label(frame, text="Nenhuma pasta selecionada", 
                                  foreground="gray")
        self.lbl_pasta.pack(pady=5)

        # Configuração de similaridade
        config_frame = ttk.LabelFrame(frame, text="Configurações", padding="10")
        config_frame.pack(pady=10, fill="x")

        ttk.Label(config_frame, text="Nível de Similaridade Mínima").pack()
        
        scale = ttk.Scale(config_frame, from_=0.1, to=1.0, variable=self.limiar_var,
                         command=self.atualizar_label_limiar, orient="horizontal")
        scale.pack(pady=5, fill="x")
        
        self.lbl_limiar = ttk.Label(config_frame, text=f"{self.limiar_var.get()*100:.0f}%")
        self.lbl_limiar.pack()

        # Explicação
        explicacao = ttk.Label(config_frame, 
                             text="✅ Detecta números iguais automaticamente\n"
                                  "📁 Salva arquivos mesclados na pasta 'Mesclados'\n"
                                  "📋 Gera relatório de erros quando necessário",
                             font=("Arial", 8), foreground="blue")
        explicacao.pack(pady=5)

        # Botão iniciar
        self.btn_iniciar = ttk.Button(frame, text="🔄 Iniciar Mesclagem Inteligente",
                                     command=self.iniciar_processo, state="disabled")
        self.btn_iniciar.pack(pady=15, fill="x")

    def selecionar_pasta(self):
        path = filedialog.askdirectory(title="Selecione a pasta com os PDFs")
        if path:
            self.diretorio_selecionado = path
            nome_pasta = os.path.basename(path)
            self.lbl_pasta.config(text=f"📁 {nome_pasta}", foreground="green")
            self.btn_iniciar.config(state="normal")
            logger.info("Pasta selecionada: %s", path)

    def iniciar_processo(self):
        if self.diretorio_selecionado:
            self.btn_iniciar.config(text="🔄 Processando...", state="disabled")
            self.update()
            
            try:
                encontrar_e_mesclar_similares(self.diretorio_selecionado, 
                                            float(self.limiar_var.get()))
            finally:
                self.btn_iniciar.config(text="🔄 Iniciar Mesclagem Inteligente", 
                                       state="normal")

    def atualizar_label_limiar(self, valor):
        try:
            self.lbl_limiar.config(text=f"{float(valor)*100:.0f}%")
        except Exception:
            self.lbl_limiar.config(text="0%")


if __name__ == "__main__":
    app = App()
    app.mainloop()