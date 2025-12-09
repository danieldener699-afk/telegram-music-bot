# Bot de Música para Telegram

Este é um bot simples para Telegram que permite aos usuários buscar, baixar e converter músicas para o formato MP3 usando o comando `/music`.

## Funcionalidades

*   **`/start`**: Mensagem de boas-vindas e instruções.
*   **`/music <nome da música>`**: Busca a música, baixa o áudio, converte para MP3 e envia o arquivo para o usuário.

## Requisitos

*   Python 3.11+
*   `python-telegram-bot`
*   `yt-dlp`
*   `ffmpeg` (para conversão de áudio, já instalado no ambiente)

## Configuração e Execução

1.  **Token do Bot:** O token do bot fornecido por você (`8230622826:AAFnGY0YX01qXwTE_0L3LY06fltLAgZpIfI`) já está configurado no arquivo `bot.py`.

2.  **Ambiente Virtual:** Um ambiente virtual chamado `venv` foi criado e as dependências foram instaladas nele.

3.  **Execução:** Para iniciar o bot, execute os seguintes comandos no terminal:

    ```bash
    # Ativa o ambiente virtual
    source venv/bin/activate

    # Executa o bot
    python3 bot.py
    ```

    O bot começará a rodar e a escutar por comandos no Telegram.

## Uso no Telegram

1.  Abra o Telegram e inicie uma conversa com o seu bot.
2.  Envie o comando `/start` para ver a mensagem de boas-vindas.
3.  Para baixar uma música, use o comando `/music` seguido do nome da música:

    ```
    /music Queen Bohemian Rhapsody
    ```

    O bot responderá com mensagens de progresso e, finalmente, enviará o arquivo MP3.

## Estrutura do Projeto

*   `bot.py`: O código-fonte principal do bot.
*   `venv/`: Diretório do ambiente virtual com as dependências.
*   `downloads/`: Diretório temporário para armazenar os arquivos de áudio durante o processamento.

**Observação:** O bot usa o `yt-dlp` com a opção `ytsearch` para buscar no YouTube. A qualidade do áudio é definida para 192kbps MP3. O arquivo baixado é automaticamente deletado após o envio para o Telegram.
