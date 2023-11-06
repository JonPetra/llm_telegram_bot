import html
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN =  # Your bot token here
URI =  # Your API URI here


async def start_command(update: Update, context):
    await update.message.reply_text("Startup successful")


history = {"internal": [], "visible": []}


async def handle_message(update: Update, context):
    global history
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
        # 'name1': 'name of user', # Optional
        # 'name2': 'name of character', # Optional
        # 'context': 'character context', # Optional
        # 'greeting': 'greeting', # Optional
        # 'name1_instruct': 'You', # Optional
        # 'name2_instruct': 'Assistant', # Optional
        # 'context_instruct': 'context_instruct', # Optional
        # 'turn_template': 'turn_template', # Optional
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
    response = requests.post(URI, json=request_payload)
    if response.status_code == 200:
        result = response.json()["results"][0]["history"]
        generated_text = result["visible"][-1][1]
        history["visible"][-1][1] = generated_text
        history["internal"][-1][1] = generated_text
        await update.message.reply_text(html.unescape(generated_text))


bot = Bot(TOKEN)
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
