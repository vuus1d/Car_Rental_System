import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from managers.file_manager import FileManager
from managers.rental_manager import RentalManager


CHOOSING_CAR, ENTERING_NAME, ENTERING_DAYS = range(3)

manager = RentalManager()
manager.cars = FileManager.load_cars()


# ------------------------------------------------------------------
# Basic commands
# ------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Welcome to the Car Rental Bot!*\n\n"
        "Available commands:\n"
        "/cars — show available cars\n"
        "/all — show all cars\n"
        "/rent — rent a car\n"
        "/return — return a rented car\n"
        "/stats — show statistics\n"
        "/help — show this message\n"
        "/cancel — cancel current action"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cars_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available = [c for c in manager.cars if c.is_available]
    if not available:
        await update.message.reply_text("No available cars right now.")
        return

    lines = ["*Available Cars:*\n"]
    for car in available:
        lines.append(
            f"`#{car.car_id}`  *{car.brand} {car.model}* ({car.year})\n"
            f"      Price: ${car.price_per_day}/day"
        )
    await update.message.reply_text("\n\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def all_cars_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not manager.cars:
        await update.message.reply_text("No cars in the system.")
        return

    lines = ["*All Cars:*\n"]
    for car in manager.cars:
        status = "Available" if car.is_available else "Rented"
        lines.append(
            f"`#{car.car_id}`  *{car.brand} {car.model}* ({car.year})\n"
            f"      Price: ${car.price_per_day}/day  —  _{status}_"
        )
    await update.message.reply_text("\n\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(manager.cars)
    available = sum(1 for c in manager.cars if c.is_available)
    rented = total - available
    revenue = sum(b.total_price for b in manager.bookings)

    text = (
        "*Statistics*\n\n"
        f"Total cars: *{total}*\n"
        f"Available: *{available}*\n"
        f"Rented: *{rented}*\n"
        f"Active bookings: *{len(manager.bookings)}*\n"
        f"Revenue this session: *${revenue}*"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ------------------------------------------------------------------
# Rent flow (ConversationHandler)
# ------------------------------------------------------------------
async def rent_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available = [c for c in manager.cars if c.is_available]
    if not available:
        await update.message.reply_text("Sorry, no available cars to rent.")
        return ConversationHandler.END

    keyboard = [
        [
            InlineKeyboardButton(
                f"{c.brand} {c.model} — ${c.price_per_day}/day",
                callback_data=f"pick:{c.car_id}",
            )
        ]
        for c in available
    ]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="pick:cancel")])

    await update.message.reply_text(
        "Choose a car to rent:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSING_CAR


async def car_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "pick:cancel":
        await query.edit_message_text("Rental cancelled.")
        return ConversationHandler.END

    car_id = int(query.data.split(":")[1])
    car = next((c for c in manager.cars if c.car_id == car_id), None)
    if car is None or not car.is_available:
        await query.edit_message_text("This car is not available anymore.")
        return ConversationHandler.END

    context.user_data["car_id"] = car_id
    await query.edit_message_text(
        f"You picked *{car.brand} {car.model}*.\n\nPlease send your name:",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ENTERING_NAME


async def name_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Name cannot be empty. Try again:")
        return ENTERING_NAME

    context.user_data["client_name"] = name
    await update.message.reply_text(
        f"Got it, *{name}*.\n\nHow many days do you want to rent? (enter a number)",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ENTERING_DAYS


async def days_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a positive whole number:")
        return ENTERING_DAYS

    car_id = context.user_data.get("car_id")
    name = context.user_data.get("client_name")
    car = next((c for c in manager.cars if c.car_id == car_id), None)

    if car is None or not car.is_available:
        await update.message.reply_text("Car is no longer available.")
        return ConversationHandler.END

    manager.rent_car(car_id, name, days)
    FileManager.save_cars(manager.cars)

    total = days * car.price_per_day
    await update.message.reply_text(
        "*Booking confirmed*\n\n"
        f"Car:    {car.brand} {car.model}\n"
        f"Client: {name}\n"
        f"Days:   {days}\n"
        f"Total:  *${total}*",
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# ------------------------------------------------------------------
# Return flow (single callback step)
# ------------------------------------------------------------------
async def return_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rented = [c for c in manager.cars if not c.is_available]
    if not rented:
        await update.message.reply_text("There are no rented cars to return.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{c.brand} {c.model}",
                callback_data=f"ret:{c.car_id}",
            )
        ]
        for c in rented
    ]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="ret:cancel")])

    await update.message.reply_text(
        "Choose a car to return:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def return_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ret:cancel":
        await query.edit_message_text("Return cancelled.")
        return

    car_id = int(query.data.split(":")[1])
    car = next((c for c in manager.cars if c.car_id == car_id), None)
    if car is None:
        await query.edit_message_text("Car not found.")
        return

    manager.return_car(car_id)
    FileManager.save_cars(manager.cars)

    await query.edit_message_text(
        f"*{car.brand} {car.model}* returned successfully.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ------------------------------------------------------------------
# Token loading
# ------------------------------------------------------------------
def load_token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token.strip()

    token_file = os.path.join(os.path.dirname(__file__), "bot_token.txt")
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    return None


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
def main():
    token = load_token()
    if not token:
        print("ERROR: bot token not found.")
        print("Either set environment variable TELEGRAM_BOT_TOKEN")
        print('or create a file "bot_token.txt" in the project root with the token inside.')
        return

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    app = Application.builder().token(token).build()

    rent_handler = ConversationHandler(
        entry_points=[CommandHandler("rent", rent_start)],
        states={
            CHOOSING_CAR: [CallbackQueryHandler(car_chosen, pattern=r"^pick:")],
            ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_entered)],
            ENTERING_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, days_entered)],
        },
        fallbacks=[CommandHandler("cancel", cancel_cmd)],
    )

    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("cars", cars_cmd))
    app.add_handler(CommandHandler("all", all_cars_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("return", return_cmd))
    app.add_handler(rent_handler)
    app.add_handler(CallbackQueryHandler(return_callback, pattern=r"^ret:"))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
