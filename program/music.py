  Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import re
import asyncio
import requests
from config import ASSISTANT_NAME, BOT_TOKEN, BOT_USERNAME, UPDATES_CHANNEL, IMG_1, IMG_2
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from driver.utils import bash
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'youtube-dl -g -f "{format}" {link}')
    if stdout:
        return 1, stdout.split("\n")[0]
    return 0, stderr


@Client.on_message(command(["تشغيل","شغل","play","/play","ش", f"play@{BOT_USERNAME}"]) & other_filters)
async def play(c: Client, m: Message):
    await m.delete()
    do = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{UPDATES_CHANNEL}&user_id={m.from_user.id}").text
    if do.count("left") or do.count("Bad Request: user not found"):
        await m.reply_text(f" ** ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉**\n@{UPDATES_CHANNEL}\n» **اشتࢪك بقناة البوت لتستطيع تشغيل الاغاني**")
    else:
        replied = m.reply_to_message
        chat_id = m.chat.id
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="• القائمه", callback_data="cbmenu"),
                    InlineKeyboardButton(text="•اغلاق", callback_data="cls"),
                ]
            ]
        )
        if m.sender_chat:
            return await m.reply_text("أنت مسؤول __المجهول__ !\n\n»العودة إلى حساب المستخدم من حقوق المسؤول.")
        try:
            aing = await c.get_me()
        except Exception as e:
            return await m.reply_text(f"error:\n\n{e}")
        a = await c.get_chat_member(chat_id, aing.id)
        if a.status != "administrator":
            await m.reply_text(
                f"💡 لاستخدامي ، أحتاج إلى أن أكون ** مسؤول ** مع الأذونات ** التالية**:\n\n» ❌ __حذف الرسائل__\n» ❌__إضافة مستخدمين__\n» ❌ __إدارة دردشة الفيديو__\n\nيتم تحديث البيانات ** تلقائيًا بعد ترقيتك ****"
            )
            return
        if not a.can_manage_voice_chats:
            await m.reply_text(
                "أّلَصٌلَأّحٌيِّهِ مَفِّقِوِدِهِد:" + "\n\n» ❌ __إدارة دردشة الفيديو__"
            )
            return
        if not a.can_delete_messages:
            await m.reply_text(
                "أّلَصٌلَأّحٌيِّهِ مَفِّقِوِدِهِ:" + "\n\n» ❌ __حذف الرسائل__"
            )
            return
        if not a.can_invite_users:
            await m.reply_text("أّلَصٌلَأّحٌيِّهِ مَفِّقِوِدِهِ:" + "\n\n» ❌__إضافة مستخدمين__")
            return
        try:
            ubot = (await user.get_me()).id
            b = await c.get_chat_member(chat_id, ubot)
            if b.status == "kicked":
                await m.reply_text(
                    f"@{ASSISTANT_NAME} **ﻣ̝حّـظَّوٌر فّـې ﺂ̣̐ﻟ̣̣ﻣ̝جّـﻣ̝وٌﻋ̝̚ة** {m.chat.title}\n\n» **قِمَ بِفِّګ حٌظّڒٍ أّلَمَ ستّخَدِمَ أوِلَأًّ إوِ تّأّګدِ مَنِ تّقِيِّدِ حٌ سأّبِ أّلَمَ سأّعٌد.**"
                )
                return
        except UserNotParticipant:
            if m.chat.username:
                try:
                    await user.join_chat(m.chat.username)
                except Exception as e:
                    await m.reply_text(f"❌ **فشل في الأنضمام𖠉**\n\n**السبب**: `{e}`")
                    return
            else:
                try:
                    invitelink = await c.export_chat_invite_link(
                        m.chat.id
                    )
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace(
                            "https://t.me/+", "https://t.me/joinchat/"
                        )
                    await user.join_chat(invitelink)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await m.reply_text(
                        f"❌ **فشل في الانضمام𖠉**\n\n**السبب**: `{e}`"
                    )
        if replied:
            if replied.audio or replied.voice:
                suhu = await replied.reply("**اެبشࢪ ثواެني بس اެبحث 🌵.**")
                dl = await replied.download()
                link = replied.link
                if replied.audio:
                    if replied.audio.title:
                        songname = replied.audio.title[:70]
                    else:
                        if replied.audio.file_name:
                            songname = replied.audio.file_name[:70]
                        else:
                            songname = "Audio"
                elif replied.voice:
                    songname = "Voice Note"
                if chat_id in QUEUE:
                    pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                    await suhu.delete()
                    await m.reply_photo(
                        photo=f"{IMG_1}",
                        caption=f"💡 ***-› اެبشࢪ ضفتهاެ ݪلانتضاࢪ** `{pos}`\n\n🏷 **-› اެݪاެسم:** [{songname}]({link})| موسيقى`\n💭**-› اެيدي اެݪمحاެدثةه:** `{chat_id}`\n🎧 **-› طݪب اެݪحݪۅٛ:** {m.from_user.mention()}",
                        reply_markup=keyboard,
                    )
                else:
                    try:
                        await suhu.edit("🔄 ** الانضمام إلى vc...**")
                        await call_py.join_group_call(
                            chat_id,
                            AudioPiped(
                                dl,
                            ),
                            stream_type=StreamType().local_stream,
                        )
                        add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        await m.reply_photo(
                            photo=f"{IMG_2}",
                            caption=f"-› اެݪحِاެݪةِ : تَمِ اެݪتَشِغِيَݪ بَنِجَاެحِ\n🏷 -› اެݪاެسم: [{songname}]({link})\n💭-› اެيدي اެݪمحاެدثةه: {chat_id}`\n💡 ** الحالة:**ݪ بَنِجَاެحِ`\n🎧 **-› طݪب اެݪحݪۅٛ:** {requester}\n📹 ** نِوِعٌ أّلَبِثّ:** `موسيقى",
                            reply_markup=keyboard,
                        )
                    except Exception as e:
                        await suhu.delete()
                        await m.reply_text(f"🚫 حدث خطأ تأڪد من المكالمه مفتوحه اولا:\n\n» {e}")
            else:
                if len(m.command) < 2:
                    await m.reply(
                        "»لو تࢪد ؏ــلئ ملف صوتي لو تنطيني شيئ للبحث **"
                    )
                else:
                    suhu = await c.send_message(chat_id, "🔍**جاࢪي البحث...**")
                    query = m.text.split(None, 1)[1]
                    search = ytsearch(query)
                    if search == 0:
                        await suhu.edit("❌ **لـم يتم العثوࢪ ؏ـلى نتائج.**")
                    else:
                        songname = search[0]
                        url = search[1]
                        duration = search[2]
                        thumbnail = search[3]
                        format = "bestaudio[ext=m4a]"
                        veez, ytlink = await ytdl(format, url)
                        if veez == 0:
                            await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                        else:
                            if chat_id in QUEUE:
                                pos = add_to_queue(
                                    chat_id, songname, ytlink, url, "Audio", 0
                                )
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=thumbnail,
                                    caption=f"💡 ***-› اެبشࢪ ضفتهاެ ݪلانتضاࢪ** `{pos}`\n\n🏷 **-› اެݪاެسم:** [{songname}]({url})| موسيقى`\n**⏱ أّلَمَدِ ةّ:** `{duration}`\n🎧 **-› طݪب اެݪحݪۅٛ:** {requester}",
                                    reply_markup=keyboard,
                                )
                            else:
                                try:
                                    await suhu.edit("🔄 ** تم الأنضمام للمڪالمه والتشغيل...**")
                                    await call_py.join_group_call(
                                        chat_id,
                                        AudioPiped(
                                            ytlink,
                                        ),
                                        stream_type=StreamType().local_stream,
                                    )
                                    add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                    await suhu.delete()
                                    requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                    await m.reply_photo(
                                        photo=thumbnail,
                                        caption=f"🏷 **اسم:** [{songname}]({url})\n**⏱ المدة:** `{duration}`\n💡 ** الحالة:** `يشغل`\n🎧 **بواسطه:** {requester}\n📹 ** نوع البث:** `موسيقى`",
                                        reply_markup=keyboard,
                                    )
                                except Exception as ep:
                                    await suhu.delete()
                                    await m.reply_text(f"🚫 حدث خطأ تاڪد من المڪالمه مفتوحه اولا: `{ep}`")

        else:
            if len(m.command) < 2:
                await m.reply(
                    "• ألـࢪد ** مـلف صوتي  ** أو ** أعطي شيأ للبحث.**"
                )
            else:
                suhu = await c.send_message(chat_id, "🔍**جـاࢪي البحث...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **لـم يتم العـثوࢪ ؏ـلى نتائج.**")
                else:
                    songname = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    format = "bestaudio[ext=m4a]"
                    veez, ytlink = await ytdl(format, url)
                    if veez == 0:
                        await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = (
                                f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            )
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"💡 ***-› اެبشࢪ ضفتهاެ ݪلانتضاࢪ** `{pos}`\n\n🏷 **-› اެݪاެسم:** [{songname}]({url})| موسيقى`\n**⏱ أّلَمَدِ ةّ:** `{duration}`\n🎧 **-› طݪب اެݪحݪۅٛ:** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await suhu.edit("🔄 **ﻟ̣̣ﺂ̣̐نّضّـﻣ̝ﺂ̣̐ﻣ̝ إﻟ̣̣ى ﺂ̣̐ﻟ̣̣ﻣ̝ﮗﺂ̣̐ﻟ̣̣ﻣ̝ﮪ...**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=thumbnail,
                                    caption=f"🏷 **-› اެݪاެسم:** [{songname}]({url})\n**⏱ أّلَمَدِ ةّ𖠈:** `{duration}`\n💡 ** الحالة:** `يشغل`\n🎧 **-› طݪب اެݪحݪۅٛ:** {requester}\n📹 ** نِوِعٌ أّلَبِثّ:** `موسيقى`",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫حّـدّثّـ خـّطِّأ تٌئﮗدّ ﻣ̝نّ ﺂ̣̐ﻟ̣̣ﻣ̝ﮗﺂ̣̐ﻟ̣̣ﻣ̝ﮪ ﻣ̝فّـتٌوٌحّـﮪ  ﺂ̣̐وٌﻟ̣̣آ`{ep}`")
