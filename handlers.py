import database
from decouple import config

from telegram import Chat, Update 
from telegram import ReplyKeyboardMarkup, KeyboardButton ,ReplyKeyboardRemove

from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

from telegram.ext import Application, CommandHandler, ContextTypes

tk = config('API_TOKEN')

TASK_TEXT, DUE_DATE, TASK_ID = range(3)  
TASK_ID_EDIT, NEW_TEXT = range(3, 5)

# ساخت کیبورد سفارشی
async def get_main_keyboard():
    keyboard = [
        [KeyboardButton("➕ افزودن تسک")],
        [KeyboardButton("📋 لیست تسک‌ها"), KeyboardButton("❌ حذف تسک")],
        [KeyboardButton("✏️ ویرایش تسک")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="خوش آمدید! از دکمه‌های زیر استفاده کن:",
        reply_to_message_id=update.effective_message.id,
        reply_markup=await get_main_keyboard())


async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text= "📝 عنوان تسک رو وارد کن:",
        reply_to_message_id=update.effective_message.id,
        reply_markup= ReplyKeyboardRemove()
    )
    return TASK_TEXT

async def receive_task_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_text = update.effective_message.text
    
    context.user_data['task_text'] = task_text
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📅  (11-12)زمان شروع و پایان را اعلام کن",
    )
    return DUE_DATE

async def receive_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    due_date = update.effective_message.text
    task_text = context.user_data.get('task_text')
    
    try:
        database.add_task(update.effective_chat.id, task_text, due_date)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ تسک با موفقیت اضافه شد!",
            reply_markup=await get_main_keyboard()
        )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ فرمت تاریخ اشتباهه! لطفاً دوباره تلاش کن.",
            reply_markup=await get_main_keyboard()
        )
    
    return ConversationHandler.END


async def list_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = database.get_tasks(update.effective_chat.id)

    if not tasks:
        update.message.reply_text("📭 لیست تسک‌ها خالیه!")
        return
    
    response = "📋 لیست تسک‌ها:\n\n"
    for task_id, task_text, due_date in tasks:
        response += f"🆔 {task_id}\n📝 {task_text}\n⏰ {due_date}\n\n"
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        reply_markup=await get_main_keyboard()
       )
    
async def delete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🆔 کد تسک مورد نظر رو وارد کن:",
        reply_to_message_id=update.effective_message.id,
        reply_markup=ReplyKeyboardRemove()
    )
    return TASK_ID

async def receive_task_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = update.effective_message.text
    user_id = update.effective_user.id

    try:
        if database.delete_task(user_id, task_id):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ تسک با موفقیت حذف شد!",
                reply_markup=await get_main_keyboard()      
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ کد تسک اشتباهه! لطفاً دوباره تلاش کن.",
                reply_markup=await get_main_keyboard()
            )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ کد تسک اشتباهه! لطفاً دوباره تلاش کن.",
            reply_markup=await get_main_keyboard()
        )
    
    return ConversationHandler.END



async def edit_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🆔 کد تسک مورد نظر برای ویرایش را وارد کن:",
        reply_markup=ReplyKeyboardRemove()
    )
    return TASK_ID_EDIT

async def receive_edit_task_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = update.message.text
    context.user_data['edit_task_id'] = task_id
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 متن جدید تسک را وارد کن:",
    )
    return NEW_TEXT

async def receive_new_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_text = update.message.text
    task_id = context.user_data.get('edit_task_id')
    user_id = update.effective_user.id 
    try:
        if database.edit_task(user_id, task_id, new_text):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ تسک با موفقیت ویرایش شد!",
                reply_markup=await get_main_keyboard()
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ تلاش ناموفق!",
                reply_markup=await get_main_keyboard()
            )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ خطا در ویرایش تسک!",
            reply_markup=await get_main_keyboard()
        )
    
    return ConversationHandler.END


def main():
    database.init_db()
    app = Application.builder().token(tk).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ افزودن تسک$'), add_task_command)],
        states={
            TASK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_task_text)],
            DUE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_due_date)]
        },
        fallbacks=[CommandHandler('cancel', start)]
    )
    
    delete_task_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^❌ حذف تسک$'), delete_task_command)],
        states={
            TASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_task_id)]
        },
        fallbacks=[CommandHandler('cancel', start)]
    )
    
    edit_task_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^✏️ ویرایش تسک$'), edit_task_command)],
        states={
            TASK_ID_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_edit_task_id)],
            NEW_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_text)]  
    }, 
        fallbacks=[CommandHandler('cancel', start)]
    )
    
    app.add_handlers([
        CommandHandler(['start', 'help'], start),
        MessageHandler(filters.Regex('^📋 لیست تسک‌ها$'), list_tasks_command),
        delete_task_conv,
        conv_handler,
        edit_task_conv
    ])
    
    app.run_polling()
    
if __name__== "__main__":
    main()
    