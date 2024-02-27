import asyncio
from datetime import date

from celery import shared_task

from telegram import Bot

from borrowing_service.models import Borrowing
from library import settings
from payment_service.models import PaymentRequired


@shared_task
def new_borrowing_created(borrowing_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=settings.TELEGRAM_BOT_API)
    loop.run_until_complete(
        bot.sendMessage(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"New borrowing by id {borrowing_id} was created",
        )
    )


@shared_task
def successful_payment(session_id):
    payment = PaymentRequired.objects.get(session_id=session_id)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=settings.TELEGRAM_BOT_API)
    loop.run_until_complete(
        bot.sendMessage(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"Payment by id {payment.pk} was successful",
        )
    )


@shared_task
def borrowing_overdue():
    print("this task sended and recieved")
    borrowing = Borrowing.objects.all()
    overdue = []
    for borrowing in borrowing:
        if borrowing.expected_return_date < date.today():
            overdue.append(borrowing.pk)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=settings.TELEGRAM_BOT_API)
    if overdue:
        loop.run_until_complete(
            bot.sendMessage(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=f"List of overdue borrows {overdue}",
            )
        )
    else:
        loop.run_until_complete(
            bot.sendMessage(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=f"No overdue borrows",
            )
        )
