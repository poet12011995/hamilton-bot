# -*- coding: utf-8 -*-
import logging
import os
import tempfile
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8125667758:AAF5BLCijyFhApp_PoKLaPKHB47OLkXTzdU"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def create_main_keyboard():
    keyboard = [
        [KeyboardButton("1 — 3D картинки")],
        [KeyboardButton("2 — карточки товара реалистичные")],
        [KeyboardButton("3 — объединить картинки")],
        [KeyboardButton("4 — улучшить качество картинки")],
        [KeyboardButton("5 — анимация")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logging.info(f"User {user.id} started the bot")
    await update.message.reply_text(
        "Привет! Я бот для работы с изображениями. Выбери одну из функций:",
        reply_markup=create_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/help - показать справку\n\n"
        "Выбери функцию из меню и отправь нужное количество фото!"
    )
    await update.message.reply_text(help_text, reply_markup=create_main_keyboard())

async def download_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивает фото и возвращает путь к файлу"""
    photo = update.message.photo[-1]  # Берем фото наибольшего качества
    photo_file = await photo.get_file()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        temp_path = temp_file.name
    
    await photo_file.download_to_drive(temp_path)
    return temp_path

async def process_images(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Обрабатывает изображения в зависимости от выбранной функции"""
    action = user_data.get('waiting_for_images')
    
    try:
        if action in ['merge', 'animate']:
            # Обработка двух изображений
            if 'first_image_path' in user_data and 'second_image_path' in user_data:
                # Здесь должна быть реальная обработка двух изображений
                await update.message.reply_text(
                    f"✅ Обработка завершена! Функция: {action}\n"
                    f"Обработано 2 изображения"
                )
                
                # Удаляем временные файлы
                if os.path.exists(user_data['first_image_path']):
                    os.unlink(user_data['first_image_path'])
                if os.path.exists(user_data['second_image_path']):
                    os.unlink(user_data['second_image_path'])
                    
        else:
            # Обработка одного изображения
            if 'image_path' in user_data:
                # Здесь должна быть реальная обработка одного изображения
                await update.message.reply_text(
                    f"✅ Обработка завершена! Функция: {action}"
                )
                
                # Удаляем временный файл
                if os.path.exists(user_data['image_path']):
                    os.unlink(user_data['image_path'])
                    
    except Exception as e:
        logging.error(f"Error processing images: {e}")
        await update.message.reply_text("❌ Ошибка при обработке изображений")
    finally:
        # Всегда очищаем user_data после обработки
        user_data.clear()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        context.user_data.clear()  # Очищаем предыдущее состояние
        
        if text == "1 — 3D картинки":
            context.user_data['waiting_for_images'] = '3d'
            await update.message.reply_text("🎨 Функция: 3D картинки\nОтправь картинку!")
        elif text == "2 — карточки товара реалистичные":
            context.user_data['waiting_for_images'] = 'product_card'
            await update.message.reply_text("🛍️ Функция: Карточки товара\nОтправь фото товара!")
        elif text == "3 — объединить картинки":
            context.user_data['waiting_for_images'] = 'merge'
            await update.message.reply_text("🖼️ Функция: Объединение\nОтправь ДВЕ картинки по очереди")
        elif text == "4 — улучшить качество картинки":
            context.user_data['waiting_for_images'] = 'enhance'
            await update.message.reply_text("🔍 Функция: Улучшение качества\nОтправь картинку!")
        elif text == "5 — анимация":
            context.user_data['waiting_for_images'] = 'animate'
            await update.message.reply_text("🎬 Функция: Анимация\nОтправь ДВЕ картинки по очереди")
        else:
            await update.message.reply_text(
                "Пожалуйста, используй кнопки для выбора функции.",
                reply_markup=create_main_keyboard()
            )
    except Exception as e:
        logging.error(f"Error in handle_message: {e}")
        await update.message.reply_text("❌ Произошла ошибка.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data = context.user_data
        
        if not user_data.get('waiting_for_images'):
            await update.message.reply_text(
                "Сначала выбери функцию из меню.",
                reply_markup=create_main_keyboard()
            )
            return
            
        action = user_data['waiting_for_images']
        
        if action in ['merge', 'animate']:
            # Обработка двух изображений
            if 'first_image' not in user_data:
                # Сохраняем первое изображение
                first_image_path = await download_photo(update, context)
                user_data['first_image'] = True
                user_data['first_image_path'] = first_image_path
                await update.message.reply_text("✅ Первое фото получено! Отправь второе.")
            else:
                # Сохраняем второе изображение и обрабатываем
                second_image_path = await download_photo(update, context)
                user_data['second_image_path'] = second_image_path
                await update.message.reply_text("✅ Второе фото получено! Обрабатываю...")
                await process_images(update, context, user_data)
                
        else:
            # Обработка одного изображения
            image_path = await download_photo(update, context)
            user_data['image_path'] = image_path
            await update.message.reply_text("✅ Фото получено! Обрабатываю...")
            await process_images(update, context, user_data)
            
    except Exception as e:
        logging.error(f"Error in handle_photo: {e}")
        await update.message.reply_text("❌ Ошибка при обработке фото")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
