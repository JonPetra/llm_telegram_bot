import html
import requests
import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
URI = os.getenv("API_URI")


async def start_command(update: Update, context):
    await update.message.reply_text("Startup successful")


history = {"internal": [], "visible": []}


async def handle_message(update: Update, context):
    global history
    response = None
    message = update.message.text
    history["visible"].append([message, ""])
    history["internal"].append([message, ""])
    request_payload = {
        "user_input": message,
        "history": history,
        "max_new_tokens": 250,
        "auto_max_new_tokens": False,
        "max_tokens_second": 0,
        "mode": "chat",
        "character": "Example",
        "instruction_template": "Vicuna-v1.1",
        "your_name": "You",
        "regenerate": False,
        "_continue": False,
        "chat_instruct_command": 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',
        "preset": "None",
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.1,
        "typical_p": 1,
        "epsilon_cutoff": 0,
        "eta_cutoff": 0,
        "tfs": 1,
        "top_a": 0,
        "repetition_penalty": 1.18,
        "repetition_penalty_range": 0,
        "top_k": 40,
        "min_length": 0,
        "no_repeat_ngram_size": 0,
        "num_beams": 1,
        "penalty_alpha": 0,
        "length_penalty": 1,
        "early_stopping": False,
        "mirostat_mode": 0,
        "mirostat_tau": 5,
        "mirostat_eta": 0.1,
        "grammar_string": "",
        "guidance_scale": 1,
        "negative_prompt": "",
        "seed": -1,
        "add_bos_token": True,
        "truncation_length": 2048,
        "ban_eos_token": False,
        "custom_token_bans": "",
        "skip_special_tokens": True,
        "stopping_strings": [],
    }
    try:
        response = requests.post(URI, json=request_payload)
        response.raise_for_status()

        result = response.json()["results"][0]["history"]
        generated_text = result["visible"][-1][1]

        if not generated_text.strip():
            generated_text = "I'm not sure how to respond to that."

        history["visible"][-1][1] = generated_text
        history["internal"][-1][1] = generated_text
        await update.message.reply_text(html.unescape(generated_text))

    except requests.exceptions.HTTPError as http_err:
        status_code = response.status_code if response is not None else "N/A"
        error_msg = f"HTTP error occurred: {http_err} - Status Code: {status_code}"
        if response and response.status_code == 503:
            error_msg += " - Service Unavailable. Please try again later."
        await update.message.reply_text(error_msg)
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            "Failed to connect to the service. Please check your connection."
        )
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "The request to the service timed out. Please try again."
        )
    except requests.exceptions.RequestException as err:
        await update.message.reply_text(f"An unexpected error occurred: {err}")


bot = Bot(TOKEN)
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
