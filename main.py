import discord
from discord.ext import commands
import requests
from googletrans import Translator
import os
from dotenv import load_dotenv

# 디스코드 봇 토큰

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 번역기
translator = Translator()

# 언어 코드와 Webhook URL 매핑
LANG_WEBHOOK_MAP = {
    "ko":
    "https://discord.com/api/webhooks/1399321208482299985/PEv6-VMIbNQEdJ3zpLsKcndduMniD4-ND3VgMDi2WL6acUiroJisRtsYm67-7eXH1fEB",
    "en":
    "https://discord.com/api/webhooks/1399334030092009472/U2vZVbNXN9UqTyvRHfMPmwamkNCac0wveqnN_krF8WIFBoGX3gOounys4uz2QDF02XEh",
    "ja":
    "https://discord.com/api/webhooks/1399334192545792130/psyPo8eZ9InszbOVCPdi3X9Bkrr79efdkAc_U6-N85-CdYfDO_3K4c9WeCpyn2ox6c2V",
    "vi":
    "https://discord.com/api/webhooks/1399334306068828280/DrWL2AZ8xg-XXseR3CiSG3Ujz3kagHVzXSWtxKdFhK60T_2Si9FOM43XUAnBUAG2yBrh",
    "zh-cn":
    "https://discord.com/api/webhooks/1399334406920867921/TDQ9dGqBWlZfnmkvl7MjoLW41S0bqsWJhMf7njRGpYz_WgzgFnridxGoPYZBeM0ZOxxU"
}

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

EXCLUDED_CHANNEL_IDS = [
    1399390287188725791,  # 번역 제외할 채널 call-bot-music
    1399298062379389043,  # 번역 제외할 채널 voice-chat
    1399358174842060982,  # 번역 제외할 채널 Guild-notice
    1399384775369949337   # 번역 제외할 채널 free-chat
]


@bot.event
async def on_ready():
    print(f"✅ 봇 로그인 완료: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    original_text = message.content
    sender = message.author.display_name

    # ✅ 제외된 채널이라면 번역하지 않음
    if message.channel.id in EXCLUDED_CHANNEL_IDS:
        print(f"[INFO] 제외된 채널이므로 번역 안함: {message.channel.name}")
        return

    # 언어 감지
    try:
        detected_lang = translator.detect(original_text).lang
        print(f"[INFO] '{sender}'의 메시지 언어 감지됨: {detected_lang}")
    except Exception as e:
        print(f"[ERROR] 언어 감지 실패: {e}")
        return

    # 각 타겟 언어로 번역 및 Webhook 전송
    for target_lang, webhook_url in LANG_WEBHOOK_MAP.items():
        # 동일 언어는 번역 생략
        if target_lang == detected_lang:
            continue

        try:
            translated = translator.translate(original_text,
                                              src=detected_lang,
                                              dest=target_lang)
            translated_text = translated.text
        except Exception as e:
            print(f"[ERROR] {target_lang} 번역 실패: {e}")
            continue

        # Webhook 전송
        data = {
            "username": f"{sender} ({detected_lang}→{target_lang})",
            "content": translated_text
        }

        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code != 204:
                print(
                    f"[ERROR] {target_lang} 전송 실패: {response.status_code} - {response.text}"
                )
            else:
                print(f"[INFO] {target_lang} 전송 성공")
        except Exception as e:
            print(f"[ERROR] {target_lang} Webhook 전송 실패: {e}")

    await bot.process_commands(message)


# from keep_alive import keep_alive

# keep_alive()
bot.run(TOKEN)
