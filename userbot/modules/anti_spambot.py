# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# Asena UserBot - Yusuf Usta
#

''' Gruba katılan spamcıları banlamada yardımcı olan modüldür. '''

from asyncio import sleep
from requests import get

from telethon.events import ChatAction
from telethon.tl.types import ChannelParticipantsAdmins, Message

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, ANTI_SPAMBOT, ANTI_SPAMBOT_SHOUT, bot


@bot.on(ChatAction)
async def anti_spambot(welcm):
    try:
        ''' Eğer bir kullanıcı spam algoritmasıyla eşleşiyorsa
           onu gruptan yasaklar. '''
        if not ANTI_SPAMBOT:
            return
        if welcm.user_joined or welcm.user_added:
            adder = None
            ignore = False
            users = None

            if welcm.user_added:
                ignore = False
                try:
                    adder = welcm.action_message.from_id
                except AttributeError:
                    return

            async for admin in bot.iter_participants(
                    welcm.chat_id, filter=ChannelParticipantsAdmins):
                if admin.id == adder:
                    ignore = True
                    break

            if ignore:
                return

            elif welcm.user_joined:
                users_list = hasattr(welcm.action_message.action, "users")
                if users_list:
                    users = welcm.action_message.action.users
                else:
                    users = [welcm.action_message.from_id]

            await sleep(5)
            spambot = False

            if not users:
                return

            for user_id in users:
                async for message in bot.iter_messages(welcm.chat_id,
                                                       from_user=user_id):

                    correct_type = isinstance(message, Message)
                    if not message or not correct_type:
                        break

                    join_time = welcm.action_message.date
                    message_date = message.date

                    if message_date < join_time:
                        # Eğer mesaj kullanıcı katılma tarihinden daha önce ise yoksayılır.
                        continue

                    check_user = await welcm.client.get_entity(user_id)

                    # Hata ayıklama. İlerideki durumlar için bırakıldı. ###
                    print(
                        f"Người dùng tham gia: {check_user.first_name} [ID: {check_user.id}]"
                    )
                    print(f"Trò chuyện: {welcm.chat.title}")
                    print(f"Thời gian: {join_time}")
                    print(
                        f"Đã gửi tin nhắn: {message.text}\n\n[Thời gian: {message_date}]"
                    )
                    ##############################################

                    try:
                        cas_url = f"https://combot.org/api/cas/check?user_id={check_user.id}"
                        r = get(cas_url, timeout=3)
                        data = r.json()
                    except BaseException:
                        print(
                            "Kiểm tra CAS không thành công, hoàn nguyên về kiểm tra anti_spambot cũ."
                        )
                        data = None
                        pass

                    if data and data['ok']:
                        reason = f"[Combot Anti Spam tarafından banlandı.](https://combot.org/cas/query?u={check_user.id})"
                        spambot = True
                    elif "t.cn/" in message.text:
                        reason = "`t.cn` đã phát hiện các URL."
                        spambot = True
                    elif "t.me/joinchat" in message.text:
                        reason = "Thông điệp quảng cáo tiềm năng"
                        spambot = True
                    elif message.fwd_from:
                        reason = "Tin nhắn từ người khác"
                        spambot = True
                    elif "?start=" in message.text:
                        reason = "Liên kết bắt đầu từ bot Telegram"
                        spambot = True
                    elif "bit.ly/" in message.text:
                        reason = "`bit.ly` URL được phát hiện."
                        spambot = True
                    else:
                        if check_user.first_name in ("Bitmex", "Promotion",
                                                     "Information", "Dex",
                                                     "Announcements", "Info",
                                                     "Duyuru", "Duyurular"
                                                     "Bilgilendirme", "Bilgilendirmeler"):
                            if check_user.last_name == "Bot":
                                reason = "SpamBot đã biết"
                                spambot = True

                    if spambot:
                        print(f"Thư rác tiềm ẩn: {message.text}")
                        await message.delete()
                        break

                    continue  # Bir sonraki mesajı kontrol et

            if spambot:
                chat = await welcm.get_chat()
                admin = chat.admin_rights
                creator = chat.creator
                if not admin and not creator:
                    if ANTI_SPAMBOT_SHOUT:
                        await welcm.reply(
                            "@admins\n"
                            "`ANTI SPAMBOT ĐÃ PHÁT HIỆN!\n"
                            "NGƯỜI DÙNG NÀY PHÙ HỢP VỚI THUẬT TOÁN SPAMBOT CỦA TÔI!`"
                            f"LÝ DO: {reason}")
                        kicked = False
                        reported = True
                else:
                    try:

                        await welcm.reply(
                            "`Đã phát hiện ra Spambot tiềm năng!!`\n"
                            f"`LÝ DO:` {reason}\n"
                            "Bắt đầu từ nhóm bây giờ, ID này sẽ được lưu cho các trường hợp trong tương lai.\n"
                            f"`NGƯỜI DÙNG:` [{check_user.first_name}](tg://user?id={check_user.id})"
                        )

                        await welcm.client.kick_participant(
                            welcm.chat_id, check_user.id)
                        kicked = True
                        reported = False

                    except BaseException:
                        if ANTI_SPAMBOT_SHOUT:
                            await welcm.reply(
                                "@admins\n"
                                "`ANTI SPAMBOT TESPİT EDİLDİ!\n"
                                "BU KULLANICI BENİM SPAMBOT ALGORİTMALARIMLA EŞLEŞİYOR!`"
                                f"SEBEP: {reason}")
                            kicked = False
                            reported = True

                if BOTLOG:
                    if kicked or reported:
                        await welcm.client.send_message(
                            BOTLOG_CHATID, "#ANTI_SPAMBOT RAPORU\n"
                            f"Kullanıcı: [{check_user.first_name}](tg://user?id={check_user.id})\n"
                            f"Kullanıcı IDsi: `{check_user.id}`\n"
                            f"Sohbet: {welcm.chat.title}\n"
                            f"Sohbet IDsi: `{welcm.chat_id}`\n"
                            f"Sebep: {reason}\n"
                            f"Mesaj:\n\n{message.text}")
    except ValueError:
        pass


CMD_HELP.update({
    'anti_spambot':
    "Cách sử dụng: Nếu mô-đun này được bật trong tệp config.env hoặc với giá trị env,\
        \nnếu những người gửi thư rác này phù hợp với thuật toán chống thư rác của UserBot, \
        \nmô-đun này cấm những người gửi thư rác khỏi nhóm (hoặc thông báo cho quản trị viên)."
})
