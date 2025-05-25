import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.markdown import hlink

from loader import dp, db, bot, admin, lock
import asyncio
from keybords import *
from func import *
from config import *
from States import *
import pytz
from datetime import datetime, timedelta
import datetime as dt
from middleware import *

admin.message.filter(IsAdmin())


@dp.message(CommandStart())
async def cmd_start(message:Message, state:FSMContext):
    db.db_start()
    db.db_settings()
    db.db_stats()
    db.db_urls()


    word = random.choice(list(captcha_dict))
    if not db.user_exists(message.from_user.id):
        start_cmd = message.text
        referi_id = str(start_cmd[7:])
        if str(referi_id) != '':
            if str(referi_id) != str(message.from_user.id):
                db.add_users(message.from_user.id, referi_id)
                await message.answer(
                    f'👋🏻 Привет {message.from_user.first_name}, чтобы убедиться что вы не робот 🤖 - пройдите капчу\n\n'
                    f'Нажми на 👉 <b>{word}</b>', reply_markup=await captcha_keybord(word))
                try:
                    await bot.send_message(referi_id,
                                           f'<b>По вашей ссылке зарегистрировался новый пользователь с id <code>{message.from_user.id}</code> @{message.from_user.username}</b>')

                except:
                    pass
            else:
                db.add_users(message.from_user.id)
                await bot.send_message(message.from_user.id, "Нельзя регистрироваться по своей ссылке")
        else:
            db.add_users(message.from_user.id)
            await message.answer(
                f'👋🏻 Привет {message.from_user.first_name}, чтобы убедиться что вы не робот 🤖 - пройдите капчу\n\n'
                f'Нажми на 👉 <b>{word}</b>', reply_markup=await captcha_keybord(word))
        await state.set_state(Captcha_users.status)
        return

    await message.answer(
        f'👋🏻 Привет {message.from_user.first_name}, чтобы убедиться что вы не робот 🤖 - пройдите капчу\n\n'
        f'Нажми на 👉 <b>{word}</b>', reply_markup=await captcha_keybord(word))
    await state.set_state(Captcha_users.status)


@dp.callback_query(F.data.startswith('Captcha'), Captcha_users.status)
async def chek_captcha(callback: CallbackQuery, state: FSMContext):
    keys = callback.data.split('|')[1]
    word = callback.data.split('|')[2]
    users_link = hlink(callback.from_user.full_name, callback.from_user.url)
    game_link = hlink(NAME_CASINO, db.get_URL().get('channals'))
    word_new = random.choice(list(captcha_dict))
    if keys == word:
        await callback.message.delete()
        await callback.message.answer(f'<b>👋 Добро пожаловать {users_link} в {game_link} 🎲</b>',
                                      reply_markup=kb_menu(callback.from_user.id), disable_web_page_preview=True)
        await state.clear()

    else:
        await callback.answer('⚠️ Вы не прошли проверку!', show_alert=True)
        await callback.message.edit_text(text=
            f'👋🏻 Привет {callback.from_user.first_name}, чтобы убедиться что вы не робот 🤖 - пройдите капчу\n\n'
            f'Нажми на 👉 <b>{word_new}</b>', reply_markup=await captcha_keybord(word_new))


@dp.message(F.text == '📎 Реферальная программа')
async def stats_adm(message: Message):
    await message.answer(f'<b>📎 Ваша реферальная ссылка:\n'
                         f'https://t.me/{NICNAME}?start={message.from_user.id}\n\n'
                         f'👥 Количество рефералов: <code>{db.count_ref(message.from_user.id)}</code>\n'
                         f'💵 Заработано с рефералов: <code>{db.refka_cheks_money(message.from_user.id)}</code>$\n\n'
                         f'❓ Как работает реферальная программа:\n'
                         f'Вы будете получать {lose_withdraw}% с каждого проигрыша своего реферала.\n'
                         f'Начисление происходит автоматически на ваш кошелек CryptoBot\n\n'
                         f'⚠️ Минимальная ставка реферала должна составлять: {min_stavka_referal}$</b>',
                         reply_markup=kb_url_Channel())


@dp.message(F.text == '💭 Информация')
async def info_func(message:Message):
    await message.answer(f'<b>💭 Информация о проекте {hlink(title=NAME_CASINO, url=db.get_URL().get("channals"))}</b>', reply_markup=kb_info(), disable_web_page_preview=True)



@admin.message(F.text == '👑 Админка')
async def stats_adm(message: Message):
    balance = await crypto.get_balance()
    balance = balance[0].available
    await message.answer(text='<b>Вы в админ меню\n'
                                          f'Баланс казино: <code>{round(float(balance), 2)}$</code></b>',
                                     reply_markup=kb_admin())


@admin.callback_query(F.data == 'back_admin')
async def stats_adm(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    balance = await crypto.get_balance()
    balance = balance[0].available
    await callback.message.edit_text(text='<b>Вы в админ меню\n'
                                          f'Баланс казино: <code>{round(float(balance), 2)}$</code></b>', reply_markup=kb_admin())


@admin.callback_query(F.data == 'stats_project')
async def stats_adm(callback: CallbackQuery):
    stats = db.all_stats()
    balance = await crypto.get_balance()
    balance = balance[0].available
    info_day = db.all_stats_day()
    procent_all = 0.0
    update_balance_all = 0.0
    try:
        procent_all = float(stats[1]) / float(stats[0]) * 100
        update_balance_all = float(stats[4]) - float(stats[3])
    except Exception:
        pass
    procent_day = 0.0
    update_balance_day = 0.0
    try:

        procent_day = float(info_day[1]) / float(info_day[0]) * 100
        update_balance_day = float(info_day[4]) - float(info_day[3])
    except Exception:
        pass

    await callback.message.edit_text(text=f'<b>📊 Статистика Казино за все время</b>\n'
                         f'<b>┠ Всего игроков:</b> <code>{stats[5]} шт</code>\n'
                         f'<b>┠ Всего игр:</b> <code>{stats[0]} шт</code>\n'
                         f'<b>┠ Побед:</b> <code>{stats[1]} шт</code>\n'
                         f'<b>┠ Поражений:</b> <code>{stats[2]} шт</code>\n'
                         f'<b>┠ Выплачено:</b> <code>{round(float(stats[3]), 2)}$</code>\n'
                         f'<b>┠ Проиграно:</b> <code>{round(float(stats[4]), 2)}$</code>\n'
                         f'<b>┠ Заработано за все время:</b> <code>{round(float(update_balance_all), 2)}$</code>\n'
                         f'<b>┠ Процент побед за все время:</b> <code>{int(procent_all)}%</code>\n\n\n'
                         f'<b>📊 Статистика Казино за сегодня</b>\n'
                         f'<b>┠ Игр сегодня:</b> <code>{info_day[0]} шт</code>\n'
                         f'<b>┠ Побед сегодня:</b> <code>{info_day[1]} шт</code>\n'
                         f'<b>┠ Поражений сегодня:</b> <code>{info_day[2]} шт</code>\n'
                         f'<b>┠ Выплачено сегодня:</b> <code>{round(float(info_day[3]), 2)}$</code>\n'
                         f'<b>┠ Проиграно сегодня:</b> <code>{round(float(info_day[4]), 2)}$</code>\n'
                         f'<b>┠ Заработано за сегодня:</b> <code>{round(float(update_balance_day), 2)}$</code>\n'
                         f'<b>┠ Процент побед за день:</b> <code>{int(procent_day)}%</code>\n\n\n'
                         f'<b>💸 Баланс Казино</b>\n'
                         f'<b>┖ Доступный баланс казино:</b> <code>{balance}$</code>', reply_markup=kb_back_admin())


@admin.callback_query(F.data == 'send_db')
async def add_card(callback: CallbackQuery):
    document = FSInputFile('database.db')
    await bot.send_document(chat_id=callback.from_user.id, document=document)
    await callback.answer()





@admin.callback_query(F.data == 'stats_user')
async def stats_adm(callback: CallbackQuery, state:FSMContext):
    await callback.message.edit_text('<b>Введите id игрока</b>', reply_markup=kb_back_admin())
    await state.set_state(UserStats.user_id)


@admin.message(UserStats.user_id)
async def stats_user(message: Message, state: FSMContext):
    user_id = message.text
    info = db.all_stats_users(user_id)
    sum_profit = 0.0

    try:
        procent = int(info[1]) / int(info[0]) * 100
    except ZeroDivisionError:
        procent = 0

    try:
        sum_profit = round(float(info[4]), 2) - round(float(info[3]), 2)
    except ZeroDivisionError:
        pass
    await message.answer(f'<b>📊 Статистика игрока</b>\n\n'
                         f'<b>┠ Всего игр:</b> <code>{info[0]} шт</code>\n'
                         f'<b>┠ Побед:</b> <code>{info[1]} шт</code>\n'
                         f'<b>┠ Поражений:</b> <code>{info[2]} шт</code>\n'
                         f'<b>┠ Выплачено:</b> <code>{round(float(info[3]), 2)}$</code>\n'
                         f'<b>┠ Проиграно:</b> <code>{round(float(info[4]), 2)}$</code>\n'
                         f'<b>┠ Заработано с реф.Программы:</b> <code>{round(float(info[5]), 2)}$</code>\n'
                         f'<b>┠ Рефералов:</b> <code>{db.count_ref(user_id)}</code>\n'
                         f'<b>┠ Заработало казино:</b> <code>{round(float(sum_profit), 2)}$</code>\n'
                         f'<b>┖ Процент побед:</b> <code>{round(float(procent), 2)}%</code>', reply_markup=kb_back_admin())
    await state.clear()



@admin.callback_query(F.data == 'add_balance')
async def stats_adm(callback: CallbackQuery, state:FSMContext):
    await callback.message.edit_text(text='<b>Введите сумму в $</b>', reply_markup=kb_back_admin())
    await state.set_state(AddBalanceCasino.amount)


@admin.message(AddBalanceCasino.amount)
async def add_balance(message: Message, state: FSMContext):
    amount = message.text

    invoce = await crypto.create_invoice(asset='USDT',
                                         amount=float(amount),
                                         description='Пополнение баланса Casino')
    await message.answer('<b>🔗 Держи ссылку на оплату</b>', reply_markup=keybord_add_balance(invoce.bot_invoice_url))
    await state.clear()


@admin.callback_query(F.data == 'settings_fake')
async def fake_game_adm(callback: CallbackQuery):
    values_fake = db.get_fake_values()
    await callback.message.edit_text(text='<b>👀 Здесь вы можете включить или отключить фейк ставки:\n'
                         f'Текущий интервал игр: ⌛️ <code>{TIMER}</code> сек.</b>', reply_markup=kb_fake_switch(values_fake))


@admin.callback_query(F.data.startswith('fake'))
async def fake_switch_func(callback:CallbackQuery):
    values_fake = callback.data.split('|')[1]
    if int(values_fake):
        db.update_fake(0)
    if int(values_fake) == 0:
        db.update_fake(1)

    values_fake = db.get_fake_values()
    await callback.message.edit_text(text='<b>👀 Здесь вы можете включить или отключить фейк ставки:\n'
                                          f'Текущий интервал игр: ⌛️ <code>{TIMER}</code> сек.</b>',
                                     reply_markup=kb_fake_switch(int(values_fake)))
    await callback.answer()



@admin.callback_query(F.data == 'kef_edit')
async def kef_edit_adm(callback: CallbackQuery):
    all_kef = db.get_all_KEF()
    text = await kef_all_text(all_kef)
    await callback.message.edit_text(text=text, reply_markup=kb_edit_kef(all_kef))



@admin.callback_query(F.data.startswith('new_kef'))
async def new_kef_func(callback:CallbackQuery, state:FSMContext):
    column = callback.data.split('|')[1]
    cur_kef = callback.data.split('|')[2]
    res = await callback.message.edit_text(text=f"<b>Текущий коэффициент: [<code>{cur_kef}</code>]\n\n"
                                                f"Введите новое значение:</b>", reply_markup=ikb_stop())
    await state.update_data(column=column, message_id=res.message_id)
    await state.set_state(NewKefGame.value)


@admin.message(NewKefGame.value)
async def fsm_new_kef(message:Message, state:FSMContext):
    await message.delete()

    data = await state.get_data()
    db.update_kef(column=data['column'], values=float(message.text))
    all_kef = db.get_all_KEF()
    text = await kef_all_text(all_kef)
    await bot.edit_message_text(chat_id=message.from_user.id, text=text, message_id=data['message_id'], reply_markup=kb_edit_kef(all_kef))
    await state.clear()


@admin.callback_query(F.data == 'knb')
async def knb_settings_func(callback:CallbackQuery):
    cur_procent = db.get_cur_KEF('KNB')
    await callback.message.edit_text(text='<b>⚙️ Подкрутка на камень,ножницы,бумага (берется рандомное число от 0-100, если рандомное число больше или равно указанному числу то юзер проиграет)\n\n'
                                          '<code>1</code> - всегда проигрыш\n'
                                          '<code>100</code> - без накрутки</b>', reply_markup=kb_KNB_twist(cur_procent))


@admin.callback_query(F.data.startswith('Twist_knb'))
async def knb_settings_func(callback:CallbackQuery):
    cur_procent = callback.data.split('|')[1]
    new_procent = await procent_knb_twist(int(cur_procent))
    db.update_kef(column='KNB', values=new_procent)
    await callback.message.edit_reply_markup(reply_markup=kb_KNB_twist(new_procent))
    await callback.answer()

@admin.callback_query(F.data == 'all_message_send')
async def all_message_send_func(callback:CallbackQuery):
    await callback.message.edit_text(text='Выберите тип рассылки', reply_markup=ikb_tip_rassilka())



@admin.callback_query(F.data == ('Texts'))
async def tip_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('<b>Отправьте текст рассылки</b>', reply_markup=ikb_stop())
    await state.set_state(AdminText.text)


@admin.message(AdminText.text)
async def rasl_text(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await message.answer(message.html_text, reply_markup=ikb_send_post())
    await state.set_state(AdminText.send)


@admin.callback_query(F.data == ('post_go'), AdminText.send)
async def rasl_text(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data['text']

    user = db.all_user()
    count = 0
    await callback.message.edit_text('Рассылка:\n'
                                     f'{text} \n\n'
                                     f'✅ Успешно запущена для <code>{len(user)}</code> человек')


    for i in range(len(user)):
        try:
            await bot.send_message(user[i][0], f'{text}', parse_mode='HTML', disable_web_page_preview=True)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            continue
    for i in ADMIN:
        await bot.send_message(i, '✅ Рассылка успешно отправлена\n'
                                  f'Сообщение получили: {count} человек')
    await state.clear()




@admin.callback_query(F.data == ('photo'))
async def tip_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('<b>[1] Отправьте текст рассылки</b>', reply_markup=ikb_stop())
    await state.set_state(AdminPhotoText.text)


@admin.message(AdminPhotoText.text)
async def rasl_text(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    await message.answer('<b>[2] Отправьте фото</b>', reply_markup=ikb_stop())
    await state.set_state(AdminPhotoText.photo)


@admin.message(F.photo, AdminPhotoText.photo)
async def rasl_text(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)

    data = await state.get_data()
    await bot.send_photo(chat_id=message.chat.id, photo=data['photo'], caption=data['text'],
                         reply_markup=ikb_send_post_photo())

    await state.set_state(AdminPhotoText.send_photo)


@admin.callback_query(F.data == ('post_photo_go'), AdminPhotoText.send_photo)
async def rasl_text_photo(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = db.all_user()
    count = 0
    await callback.message.edit_caption(caption='Рассылка:\n'
                                                f'{data["text"]} \n\n'
                                                f'✅ Успешно запущена для <code>{len(user)}</code> человек')
    try:
        for i in range(len(user)):

            try:
                await bot.send_photo(chat_id=user[i][0], photo=data['photo'], caption=data['text'], parse_mode='HTML')
                count += 1
                await asyncio.sleep(0.05)

            except Exception as e:
                continue
        for i in ADMIN:
            await bot.send_message(chat_id=i, text='✅ Рассылка успешно отправлена\n'
                                                   f'Сообщение получили: {count} человек')
            await state.clear()
    except Exception as e:
        await state.clear()


@admin.callback_query(F.data == 'urls')
async def urls_func(callback:CallbackQuery):
    url = db.get_URL()
    await callback.message.edit_text(await urls_admin_text(url), reply_markup=kb_urls(), disable_web_page_preview=True)


@admin.callback_query(F.data.startswith('UrlEdit'))
async def new_url_func(callback:CallbackQuery, state:FSMContext):
    column = callback.data.split('|')[1]
    name = callback.data.split('|')[2]
    res = await callback.message.edit_text(text=f'<b>Выбран: {name}\n\n'
                                                f'Введите новую ссылку:</b>', reply_markup=ikb_stop())
    await state.update_data(message_id=res.message_id, column=column)
    await state.set_state(NewUrlAdmin.url)


@admin.message(NewUrlAdmin.url)
async def new_url_fsm(message:Message, state:FSMContext):
    await message.delete()
    data = await state.get_data()
    db.update_url(column=data.get('column'), values=message.text)
    url = db.get_URL()
    await bot.edit_message_text(chat_id=message.from_user.id, text=await urls_admin_text(url), message_id=data.get('message_id'), disable_web_page_preview=True, reply_markup=kb_urls())
    await state.clear()


@admin.callback_query(F.data == 'deleted_checks')
async def deleted_checks_func(callback:CallbackQuery):
    await callback.message.edit_text(text='<b>Вы уверены что хотите удалить все активные чеки?</b>', reply_markup=kb_answer_delete())

@admin.callback_query(F.data == 'YesDel')
async def YesDel_func(callback:CallbackQuery):
    all_cheks = await crypto.get_checks(asset='USDT', status='active')
    try:
        for i in all_cheks:
            await crypto.delete_check(i.check_id)
    except TypeError:
        return await callback.answer('Активных чеков нет', show_alert=True)
    await callback.answer('✅ Чеки удалены', show_alert=True)
    balance = await crypto.get_balance()
    balance = balance[0].available
    await callback.message.edit_text(text='<b>Вы в админ меню\n'
                                          f'Баланс казино: <code>{round(float(balance), 2)}$</code></b>',
                                     reply_markup=kb_admin())


@dp.channel_post()
async def start_game_post_func(message: Message):
    text = message.text
    if 'отправил(а)' in message.text:
        await message.delete()
        async with lock:
            user_id = message.entities[0].user.id
            username = message.entities[0].user.username
            first_name = message.entities[0].user.first_name
            amount = text.split('($')[1].split(').')[0]
            order = ''.join(random.choice(digits) for i in range(10))

            if '@' in first_name:
                first_name = f'*******'
            if not db.user_exists(user_id):
                db.add_users(user_id)
            exodus = ''
            try:
                exodus = text.split('💬')[1].strip().title()
            except IndexError:
                return await not_game_func(amount=float(amount), user_id=user_id, status='Comments', first_name=first_name, order=order, username=username)
            if float(amount) > LIMIT_STAVKA:
                return await not_game_func(amount=float(amount), user_id=user_id, status='LIMIT', first_name=first_name, order=order, username=username)
            if not exodus in all_text:
                return await not_game_func(amount=float(amount), user_id=user_id, status='Command', first_name=first_name,
                                    order=order, username=username)

            await bot.send_message(chat_id=URL_LOG_CHANNAL, text=f"{text}\n\n"
                                                                 f"id: <code>{user_id}</code>\n"
                                                                 f"username: @{username}\n"
                                                                 f"name: {first_name}")
            url = db.get_URL()
            help_stavka = hlink('Как сделать ставку', url.get('info_stavka'))
            info_channal = hlink('Новостной канал', url.get('news'))
            url_viplata = hlink('Выплаты', url.get('transfer'))
            url_referal_programm = hlink(f'Реферальная программа [{lose_withdraw}%]', URL_BOT)
            name_game = await get_name_game(text=exodus)

            res = await bot.send_message(chat_id=channal_id, text=f'<b>🤵🏻‍♂️ Крупье принял новую ставку.</b>\n\n'
                                                                  f'👤 Игрок: <b>{first_name}</b>\n'
                                                                  f'💸 Ставка: <b>{amount}$</b>\n'
                                                                  f'☁️ Исход: <b>{exodus}</b>\n'
                                                                  f'🕹 Игра: <b>({name_game})</b>\n\n'
                                                                  f'<b>{help_stavka} | {info_channal} | {url_viplata}\n'
                                                                  f'[ {url_referal_programm} ]</b>',
                                         reply_markup=send_stavka(), disable_web_page_preview=True)

            echange = await crypto.get_exchange_rates()
            rubs_price = echange[0].rate
            KEF = db.get_all_KEF()
            if exodus in Bones:
                game = await bot.send_dice(chat_id=channal_id, emoji='🎲', reply_to_message_id=res.message_id)
                result_game = game.dice.value
                if exodus == 'Меньше' and result_game <= 3:
                    await transfer_wins(KEF=KEF.get('KEF1'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if exodus == 'Меньше' and result_game > 3:
                    await referal_send_money(user_id, amount)
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name, message_id=res.message_id)

                if exodus == 'Больше' and result_game >= 4:
                    await transfer_wins(KEF=KEF.get('KEF1'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return

                if exodus == 'Больше' and result_game < 4:
                    await referal_send_money(user_id, amount)
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name, message_id=res.message_id)

                if exodus == '1' and result_game == 1 or exodus == '2' and result_game == 2 or exodus == '3' and result_game == 3 or exodus == '4' and result_game == 4 or exodus == '5' and result_game == 5 or exodus == '6' and result_game == 6:
                    await transfer_wins(KEF=KEF.get('KEF2'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return

                if exodus == '1' and result_game != 1 or exodus == '2' and result_game != 2 or exodus == '3' and result_game != 3 or exodus == '4' and result_game != 4 or exodus == '5' and result_game != 5 or exodus == '6' and result_game != 6:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Пвп' or exodus == 'Дуэль':
                    game_bot = await bot.send_dice(chat_id=channal_id, emoji='🎲', reply_to_message_id=res.message_id)
                    result_user = game.dice.value
                    result_bot = game_bot.dice.value
                    if result_user == result_bot:
                        await draw_message(message_id=res.message_id, username=username, user_id=user_id,
                                           amount=amount, order=order)

                        return
                    if result_user > result_bot:
                        await transfer_wins(KEF=KEF.get('KEF3'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return
                    if result_user < result_bot:
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)

                if exodus == 'Ничья' or exodus == 'Равно':
                    game_bot = await bot.send_dice(chat_id=channal_id, emoji='🎲', reply_to_message_id=res.message_id)
                    result_user = game.dice.value
                    result_bot = game_bot.dice.value
                    if result_user == result_bot:
                        await transfer_wins(KEF=KEF.get('KEF14'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return
                    if result_user != result_bot:
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)

                if exodus == '2М' or exodus == '2 Меньше':
                    game_bot = await bot.send_dice(chat_id=channal_id, emoji='🎲',
                                                   reply_to_message_id=res.message_id)
                    result_user = game.dice.value
                    result_bot = game_bot.dice.value
                    if result_user <= 3 and result_bot <= 3:
                        await transfer_wins(KEF=KEF.get('KEF4'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return
                    else:
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)

                if exodus == '2Б' or exodus == '2 Больше':
                    game_bot = await bot.send_dice(chat_id=channal_id, emoji='🎲',
                                                   reply_to_message_id=res.message_id)
                    result_user = game.dice.value
                    result_bot = game_bot.dice.value
                    if result_user >= 4 and result_bot >= 4:
                        await transfer_wins(KEF=KEF.get('KEF4'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return
                    else:
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)

                if exodus == 'Чет' and result_game % 2 == 0:
                    await transfer_wins(KEF=KEF.get('KEF5'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return

                if exodus == 'Чет' and result_game % 2 != 0:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Нечет' and result_game % 2 != 0:
                    await transfer_wins(KEF=KEF.get('KEF5'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return

                if exodus == 'Нечет' and result_game % 2 == 0:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

            if exodus in Slots:
                game = await bot.send_dice(chat_id=channal_id, emoji='🎰', reply_to_message_id=res.message_id)
                result_game = game.dice.value
                if result_game == 43:
                    await transfer_wins(KEF=KEF.get('KEF6'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if result_game == 1:
                    await transfer_wins(KEF=KEF.get('KEF7'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if result_game == 22:
                    await transfer_wins(KEF=KEF.get('KEF8'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if result_game == 64:
                    await transfer_wins(KEF=KEF.get('KEF9'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                else:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

            if exodus in Basketball:
                game = await bot.send_dice(chat_id=channal_id, emoji='🏀', reply_to_message_id=res.message_id)
                result_game = game.dice.value
                if exodus == 'Баскетбол Гол' and result_game >= 4 or exodus == 'Баскет Гол' and result_game >= 4:
                    await transfer_wins(KEF=KEF.get('KEF10'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if exodus == 'Баскетбол Гол' and result_game < 4 or exodus == 'Баскет Гол' and result_game < 4:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Баскетбол Мимо' and result_game <= 3 or exodus == 'Баскет Мимо' and result_game <= 3:
                    await transfer_wins(KEF=KEF.get('KEF11'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if exodus == 'Баскетбол Мимо' and result_game > 3 or exodus == 'Баскет Мимо' and result_game > 3:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

            if exodus in Fotbool:
                game = await bot.send_dice(chat_id=channal_id, emoji='⚽️', reply_to_message_id=res.message_id)
                result_game = game.dice.value
                if exodus == 'Футбол Гол' and result_game >= 3 or exodus == 'Фут Гол' and result_game >= 3:
                    await transfer_wins(KEF=KEF.get('KEF12'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if exodus == 'Футбол Гол' and result_game < 3 or exodus == 'Фут Гол' and result_game < 3:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Футбол Мимо' and result_game <= 2 or exodus == 'Фут Мимо' and result_game <= 2:
                    await transfer_wins(KEF=KEF.get('KEF13'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)
                    return
                if exodus == 'Футбол Мимо' and result_game > 2 or exodus == 'Фут Мимо' and result_game > 2:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)
            if exodus in SU_E_FA:
                SU_E_FA_Procent = db.get_KNB_procent()
                if exodus == 'Ножницы':
                    await bot.send_message(chat_id=channal_id, text='✌️', reply_to_message_id=res.message_id)  # User
                    number = random.randint(1, 101)
                    emoji_bot = random.choice(['✌️', '✋', '✊'])
                    if number >= SU_E_FA_Procent:
                        emoji_bot = '✊'
                    await bot.send_message(chat_id=channal_id, text=emoji_bot, reply_to_message_id=res.message_id)
                    # прописываем логику побед и проигрышей
                    if emoji_bot == '✊':
                        await asyncio.sleep(3.5)
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)
                    if emoji_bot == '✌️':
                        return await draw_message(message_id=res.message_id, username=username, user_id=user_id,
                                           amount=amount, order=order)
                    if emoji_bot == '✋':
                        await transfer_wins(KEF=KEF.get('KEF15'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return

                if exodus == 'Камень':
                    await bot.send_message(chat_id=channal_id, text='✊', reply_to_message_id=res.message_id)  # User
                    number = random.randint(1, 101)
                    emoji_bot = random.choice(['✌️', '✋', '✊'])
                    if number >= SU_E_FA_Procent:
                        emoji_bot = '✋'
                    await bot.send_message(chat_id=channal_id, text=emoji_bot, reply_to_message_id=res.message_id)
                    # прописываем логику побед и проигрышей
                    if emoji_bot == '✋':
                        await asyncio.sleep(3.5)
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)
                    if emoji_bot == '✊':
                        return await draw_message(message_id=res.message_id, username=username, user_id=user_id,
                                           amount=amount, order=order)
                    if emoji_bot == '✌️':
                        await transfer_wins(KEF=KEF.get('KEF15'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return

                if exodus == 'Бумага':
                    await bot.send_message(chat_id=channal_id, text='✋', reply_to_message_id=res.message_id)  # User
                    number = random.randint(1, 101)
                    emoji_bot = random.choice(['✌️', '✋', '✊'])
                    if number >= SU_E_FA_Procent:
                        emoji_bot = '✌️'
                    await bot.send_message(chat_id=channal_id, text=emoji_bot, reply_to_message_id=res.message_id)
                    # прописываем логику побед и проигрышей
                    if emoji_bot == '✌️':
                        await asyncio.sleep(3.5)
                        await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                          message_id=res.message_id)
                        await referal_send_money(user_id, amount)
                    if emoji_bot == '✋':
                        return await draw_message(message_id=res.message_id, username=username, user_id=user_id,
                                           amount=amount, order=order)
                    if emoji_bot == '✊':
                        await transfer_wins(KEF=KEF.get('KEF15'), username=username, amount=amount, user_id=user_id,
                                            message_id=res.message_id,
                                            rubs_price=rubs_price, order=order)
                        return
            if exodus in WHEEL:

                number_random = random.randint(0, 14)
                if number_random == 0 and exodus == 'Зеленое':
                    number_random = random.randint(0, 14)
                await bot.send_animation(chat_id=channal_id, animation=FSInputFile(f'video/{number_random}.mp4'))

                if exodus == 'Красное' and str(number_random) in RED:
                    return await transfer_wins(KEF=KEF.get('KEF16'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)

                if exodus == 'Красное' and str(
                        number_random) in BLACK or number_random == 0 and exodus == 'Красное':
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Черное' and str(number_random) in BLACK:
                    return await transfer_wins(KEF=KEF.get('KEF16'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)

                if exodus == 'Черное' and str(number_random) in RED or number_random == 0 and exodus == 'Черное':
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

                if exodus == 'Зеленое' and number_random == 0:
                    return await transfer_wins(KEF=KEF.get('KEF17'), username=username, amount=amount, user_id=user_id,
                                        message_id=res.message_id,
                                        rubs_price=rubs_price, order=order)

                if exodus == 'Зеленое' and number_random != 0:
                    await go_cashback(amount=amount, user_id=user_id, first_name=first_name,
                                      message_id=res.message_id)
                    await referal_send_money(user_id, amount)

            db.add_count_pay(user_id=user_id, text='lose', amount=round(float(amount), 2))
            db.add_count_pay_stats_day(text='lose', amount=round(float(amount), 2))
            await send_message_lose_users(message_id=res.message_id)
            await asyncio.sleep(5)





async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await set_default_commands()
    dp.update.outer_middleware(LoggingUsers())
    dp.include_router(admin)
    await scheduler_jobs()
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())