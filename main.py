#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import config
import json
import random
import sqlite3
import os
import time

from aiogram import Bot, Dispatcher, executor, types

queries = {
    "create_table" : """
        CREATE TABLE `users`(
                id          INTEGER     PRIMARY KEY NOT NULL,
                username    VARCHAR(35)             NOT NULL,
                name        VARCHAR(255)            NOT NULL,
                length      INTEGER                 NOT NULL,
                endtime     INTEGER                 NOT NULL,
                spamcount   INTEGER                 NOT NULL,
                blacklisted BOOLEAN                 NOT NULL
            );
    """,
    "put_user" : """
        INSERT INTO `users`(id,username, name, length, endtime, spamcount, blacklisted)
        VALUES (?,?,?,?,?,?,?)
    """,
    "report_table" : """
        CREATE TABLE `reports` (
            id          INTEGER        NOT NULL,
            username    VARCHAR(35)    NOT NULL,
            name        VARCHAR(255)   NOT NULL,
            message     TEXT           NOT NULL
        )
    """
}

def ass_main(ass_info, db):
    if ass_info[4] > int(time.time()):
        output_message = ""

        last_time = ass_info[4] - int(time.time())
        hours = int(last_time / 3600)
        minutes = int((last_time / 60) - (hours * 60))

        if hours == 0:
            output_message = (
                "@{0}, ти вже грав! Зачекай {1} хв.".format(ass_info[1], minutes)
            )
        else:
            output_message = (
                "@{0}, ти вже грав! Зачекай {1} год., {2} хв.".format(ass_info[1], hours, minutes)
            )

        ass_info = list(ass_info)
        ass_info[5] += 1
        db.execute("""
            UPDATE `users` SET spamcount={0} WHERE id={1}
        """.format(ass_info[5], ass_info[0]))
    else:
        output_message = ""
        tmp_length = random.randint(-10, 15)
        output_message = "@{0}, твоя дупця ".format(ass_info[1])

        if tmp_length == 0:
            # message with no profit
            output_message += "не змінила розміру. "
        elif tmp_length > 0:
            # message with profit
            output_message += ("підросла на {0} см! Зараз твоя дупця прям бомбезна. ".format(tmp_length))
        elif tmp_length < 0:
            # message with bad profit
            if not ass_info[3] - tmp_length <= 0:
                output_message += ("зменшилась на {0} см! Зараз твоя дупця вже не файна. ".format(tmp_length * -1))

        ass_info = list(ass_info)
        ass_info[3] = ass_info[3] + tmp_length

        if ass_info[3] < 0:
            ass_info[3] = 0
            output_message += "Зараз ти не маєш заду. "
        else:
            output_message += "\nНаразі ваша дупенція становить: {0} см. ".format(ass_info[3])

        timeleft = random.randint(3600, 86400)
        end_time = int(time.time()) + timeleft

        last_time = end_time - int(time.time())

        if last_time < 0:
            minutes = ((last_time // 60) - (last_time // 3600) * 60) * -1
            hours = last_time // 3600 * -1
        else:
            minutes = (last_time // 60) - (last_time // 3600) * 60
            hours = last_time // 3600
        ass_info[5] = 0
        output_message += "Продовжуй грати через {0} год., {1} хв.".format(hours, minutes)
        db.execute("""
                UPDATE `users` SET length={0}, endtime={2}, spamcount=0 WHERE id={1}
            """.format(ass_info[3], ass_info[0], end_time))

    return output_message

# database initialization

if "list" in os.listdir("."):
    print("[+] Everything is fine!")
else:
    db = sqlite3.connect("list")
    db.execute(queries["create_table"])
    print("[+] Database and table 'users' are created successfully !\n")
    db.execute(queries["report_table"])
    print("[+] Report table is created successfully!")
    db.commit()
    db.close()

# initialization

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)

if config.DEBUG == True:
    print("[!] WARNING! DEBUG mode is on!")
    @dp.message_handler(commands=["ass"])
    async def ass(message: types.Message):
        await message.reply("ВКЛЮЧЕН РЕЖИМ ОТКЛАДКИ! БОТ НЕ РАБОТАЕТ!")

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)

# dialogs
content = json.loads( open("dialogs.json","r",encoding="utf8").read())

@dp.message_handler(lambda message: "/unban" in message.text )
async def unban(message : types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        id = message.text[7:].strip(" ")

        if not id:
            await message.reply("Ти забув уввести номер підора!")
        else:
            db = sqlite3.connect("list")
            db.execute("""
                UPDATE `users` SET blacklisted=0, spamcount=0 WHERE id={0}
            """.format( id ))

            db.commit()
            db.close()

            await message.reply("Користувач {0} може повернутися до гри!".format(id))

@dp.message_handler(commands=["blacklist"])
async def ass(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        db = sqlite3.connect("list")
        cursor = db.execute("""
            SELECT * FROM `users` WHERE blacklisted=1
        """)
        users_data = cursor.fetchall()
        db.close()

        if not users_data:
            await message.reply("Нема заблокованих користувачів!")
        else:
            output_message = "ID : USERNAME : NAME\n\n"

            for user_data in users_data:
                output_message += "{0} : {1} : {2}\n".format(user_data[0], user_data[1], user_data[2])

            await message.reply(output_message)

@dp.message_handler(commands=["start"])
async def ass(message: types.Message):
    await message.reply(content["start"])

@dp.message_handler(lambda message: "/report" in message.text)
async def report(message: types.Message):

    if len(message.text[8:]) < 15:
        if len(message.text[8:].strip()) == 0:
            await message.reply("Нічого не забув?")
        else:
            await message.reply("Звіт дуже малий!")
    else:
        data = ( message.from_user["id"], message.from_user["username"], message.from_user["first_name"], message.text[8:] )
        db = sqlite3.connect("list")
        db.execute("""
            INSERT INTO `reports` (id, username, name, message)
            VALUES (?, ?, ?, ?)
        """, data )
        db.commit()
        db.close()
        await message.reply("Дякуємо за звіт! 💛")
        print("[R] A report had sent!")

@dp.message_handler(commands=["show_reports"])
async def show_reports(message : types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        db = sqlite3.connect("list")
        cursor = db.execute("""
            SELECT * FROM `reports`
        """)

        reports = cursor.fetchall()

        if not reports:
            await message.reply("Ще не нема звітів!")
        else:
            output_message = "ID : USERNAME : NAME : MESSAGE\n\n"
            for report in reports:
                output_message += "⛔️{0} : {1} : {2}\n      {3}\n\n".format(*report)

            db.close()

            await message.reply(output_message)

@dp.message_handler(commands=["clear_reports"])
async def clear_reports(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        db = sqlite3.connect("list")
        db.execute("""
            DELETE FROM `reports`
        """)
        db.commit()
        db.close()

        await message.reply("Звіти повністю очищені!")

# ass script
@dp.message_handler(commands=["ass"])
async def ass(message: types.Message):
    if not message.chat["id"] != "495137368":
        await message.answer("Я працюю лише в деякій групі!")
    else:
        db = sqlite3.connect("list")
        # if user exists in database

        cursor = db.execute("""
        SELECT * FROM `users` WHERE id={0}
        """.format(message.from_user["id"]))
        ass_info = cursor.fetchone()

        if ass_info is None:
            userinfo = (message.from_user["id"], message.from_user["username"], message.from_user["first_name"], 0, 0, 0, 0)
            db.execute(queries["put_user"], userinfo)
            cursor = db.execute("""
            SELECT * FROM `users` WHERE id={0}
            """.format(message.from_user["id"]))
            ass_info = cursor.fetchone()
            await message.reply("@{0}, вітаю в нашій когорті, хлопче/дівчино".format(ass_info[1]))
            await message.reply(ass_main(ass_info, db))
        else:
            if int(time.time()) >= ass_info[4]:
                await message.reply(ass_main(ass_info, db))
            else:
                if not ass_info[6]:
                    if ass_info[5] != 6:
                        await message.reply(ass_main(ass_info, db))
                    else:
                        db.execute("""
                            UPDATE `users` SET blacklisted=1, length=0 WHERE id={0}
                        """.format(ass_info[0]))
                        await message.reply("{0}, я тобі попку збільшую, а ти мені спамиш. Мені взагалі-то теж не солодко постійно вам попу міряти. Все, дружок, тепер ти мене не будеш зайобувати — ти в муті.".format(ass_info[2]))

                else:
                    await message.reply("{0}, дружок, ти вже награвся, шуруй звідси.".format(ass_info[2]))


        db.commit()
        db.close()

# help

@dp.message_handler(commands=["statistic"])
async def statistic(message : types.Message):
    db = sqlite3.connect("list")
    try:
        cursor = db.execute("""
            SELECT * FROM `users` ORDER BY length DESC
        """)
        users_data = cursor.fetchall()
        db.close()
    except sqlite3.OperationalError:
        await message.reply("Нема гравців! Стань першим!")
        return


    if not users_data:
        await message.reply("Нема гравців! Стань першим!")
    else:
        i = 1
        output_message = "Рейтинг гравців:\n\n"

        emojis = ["👑 ", "🥇 ", "🥈 ", "🥉 ", "😈 ", "😇"]

        for user_data in users_data:
            try:
                output_message += emojis[i-1]
            except IndexError:
                pass
            if user_data[6]:
                output_message += "{0}. {1} залишився без дупи через спам\n".format(i, user_data[2])
            else:
                if not user_data[3]:
                    output_message += "{0}. {1} — не має сіднички\n".format(i, user_data[2], user_data[3])
                else:
                    output_message += "{0}. {1} — {2} см\n".format(i, user_data[2], user_data[3])
                i += 1

        await message.reply(output_message)

@dp.message_handler(commands=["leave"])
async def leave(message: types.Message):
    db = sqlite3.connect("list")

    cursor = db.execute("""
    SELECT * FROM `users` WHERE id={0}
    """.format(message.from_user["id"]))
    ass_info = cursor.fetchone()
    if not ass_info:
        await message.reply("Ти не зарегестрований у грі!")
    else:
        if not ass_info[6]:
            db.execute("""
                DELETE FROM `users` WHERE id={0}
            """.format(message.from_user["id"]))
            await message.reply("Ти покинув гру! Шкода такий гарний зад.")
        else:
            await message.reply("Ні, таке не проканає 😏")
    db.commit()
    db.close()

"""
@dp.message_handler(lambda message: "/slap" in message.text)
async def slap(message: types.Message):
    username = message.text[6:]

    db = sqlite3.connect("list")
    cursor = db.execute("SELECT * FROM `users` WHERE username={0}".format(username))

    await message.reply(cursor.fetchone())

    db.commit()
    db.close()
"""


@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(
        types.KeyboardButton(text="/ass"),
        types.KeyboardButton(text="/leave"),
    )

    keyboard.row(
        types.KeyboardButton(text="/help"),
        types.KeyboardButton(text="/statistic")
    )

    await message.reply("Звичайно, друже: ",reply_markup=keyboard)

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.reply(content["help"])

@dp.message_handler(commands=["admin_help"])
async def menu(message: types.Message):
    if message.from_user["id"] in config.SUPER_USERS:
        await message.reply(content["admin_help"])


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
