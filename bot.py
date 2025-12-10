import logging
import os
import re
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# O token do bot será lido de uma variável de ambiente para segurança no deploy
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"

# Garante que o diretório de downloads exista
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem quando o comando /start é emitido."""
    await update.message.reply_text(
        "Olá! Eu sou o seu bot de música. Use o comando /music seguido do nome da música que você deseja baixar e converter para MP3.\n\n"
        "Exemplo: /music Queen Bohemian Rhapsody"
    )

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Baixa e envia a música solicitada como MP3."""
    
    # 1. Extrair a query do usuário
    query = " ".join(context.args)
    
    if not query:
        await update.message.reply_text(
            "Por favor, forneça o nome da música que você deseja. Exemplo: /music Queen Bohemian Rhapsody"
        )
        return

    await update.message.reply_text(f"🤖 Buscando e processando a música: **{query}**...", parse_mode='Markdown')

    # A lógica de download e conversão
    
    # Define um nome de arquivo temporário e único
    temp_filename_base = os.path.join(DOWNLOAD_DIR, f"{update.message.chat_id}_{update.message.message_id}")
    final_mp3_path = None
    
    try:
        # 1. Configuração do yt-dlp para buscar, baixar o melhor áudio e converter para mp3
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
    # O outtmpl será um nome de arquivo temporário fixo. O yt-dlp adicionará a extensão (.mp3)
    'outtmpl': f"{temp_filename_base}.%(ext)s",
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch', # Busca no YouTube
        }

        await update.message.reply_text("🔎 Buscando e baixando o áudio...")
        
        with YoutubeDL(ydl_opts) as ydl:
            # O yt-dlp não é nativamente assíncrono, mas pode ser executado em um executor
            # para não bloquear o loop de eventos do Telegram.
            # No entanto, a biblioteca python-telegram-bot já lida com isso ao chamar o handler.
            # Vamos manter a chamada síncrona por enquanto, mas garantir que o yt-dlp não use o nome do arquivo final
            # com o título, pois isso complica a limpeza. O ajuste anterior já resolveu isso.
            # O problema real é que o yt-dlp pode demorar, então vamos adicionar uma mensagem de "aguarde".
            # O yt-dlp faz a busca, download e conversão
            info = ydl.extract_info(query, download=True)
            
            # Tenta encontrar o caminho do arquivo final
            if 'entries' in info and info['entries']:
                # Se for uma busca, pega o primeiro resultado
                entry = info['entries'][0]
            else:
                entry = info
            
            # O yt-dlp não retorna o nome exato do arquivo convertido.
            # Precisamos procurá-lo no diretório de downloads.
            # O nome do arquivo final será algo como: {temp_filename_base}_{title}.mp3
            
            # Vamos usar o título para tentar encontrar o arquivo
            title = entry.get('title', 'audio')
            
            # O nome do arquivo final deve ser o outtmpl com a extensão .mp3
            final_mp3_path = f"{temp_filename_base}.mp3"
            
            if not os.path.exists(final_mp3_path):
                # Se o arquivo não existir, pode ter ocorrido um erro ou o yt-dlp usou um nome diferente.
                # Vamos tentar a busca mais genérica como fallback.
                for filename in os.listdir(DOWNLOAD_DIR):
                    if filename.startswith(os.path.basename(temp_filename_base)) and filename.endswith('.mp3'):
                        final_mp3_path = os.path.join(DOWNLOAD_DIR, filename)
                        break
            
            if not final_mp3_path:
                raise FileNotFoundError("Não foi possível encontrar o arquivo MP3 final após o download e conversão.")

            await update.message.reply_text(f"✅ Download e conversão concluídos. Enviando **{title}**...", parse_mode='Markdown')

            # 2. Enviar o arquivo MP3
            with open(final_mp3_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=title,
                    caption=f"Música solicitada: {query}"
                )

            await update.message.reply_text("🎶 Música enviada com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao processar a música: {e}")
        await update.message.reply_text(f"❌ Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente. Detalhes: {e}")

    finally:
        # 3. Limpeza: Deletar o arquivo local
        if final_mp3_path and os.path.exists(final_mp3_path):
            os.remove(final_mp3_path)
            logger.info(f"Arquivo temporário deletado: {final_mp3_path}")


def main() -> None:
    """Inicia o bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN não encontrado. Defina a variável de ambiente.")
        return
        
    # Cria o Application e passa o token do bot.
    application = Application.builder().token(BOT_TOKEN).build()

    # Adiciona os handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("music", music))

    # Inicia o bot
    logger.info("Bot iniciado. Pressione Ctrl+C para parar.")
    # Usamos run_polling para que o bot possa receber atualizações
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
