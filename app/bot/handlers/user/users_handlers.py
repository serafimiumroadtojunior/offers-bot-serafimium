from typing import List

from redis.asyncio import Redis
from aiogram import Bot, F, Router
from aiogram_i18n import I18nContext
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message, User, 
    InlineKeyboardMarkup,
    SuccessfulPayment,
    PreCheckoutQuery,
    LabeledPrice,
    InaccessibleMessage,
    CallbackQuery
)

from app.bot.states import StateSend
from app.bot.settings import Settings
from app.bot.utils import answer_message, generate_special_code
from app.bot.database import (
    get_user_locale, add_user_check, 
    get_user_check, refund_delete_check,
    get_user_status
)
from app.bot.keyboards import (
    SendUserCallback, ButtonsCallbackInfos, 
    customed_keyboard
)

user_router: Router = Router()

@user_router.message(Command("send"))
async def command_send(
    message: Message,
    redis: Redis, 
    i18n: I18nContext,
    settings: Settings,
    command: CommandObject,
    bot: Bot
):
    if not message.from_user:
        return None
    
    if not command.args:
        return await answer_message(
            bot=bot,
            chat_id=message.chat.id,
            text=i18n.get(
                "error-args"
            )
        )

    message_text: str = command.args
    user: User = message.from_user
    user_id: int = user.id
    user_full_name: str = user.full_name
    status = await get_user_status(
        user_id=user_id,
        redis=redis
    )
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    if status == 'Banned':
        return await answer_message(
            bot=bot,
            chat_id=user_id,
            text=i18n.get(
                'error-send',
                locale
            )
        )

    buttons_callbacks: List[str] = [
        ButtonsCallbackInfos(
            action="ban",
            user_id=user_id
        ).pack(),
        ButtonsCallbackInfos(
            action="unban",
            user_id=user_id
        ).pack(),
        SendUserCallback(
            user_id=user_id,
            full_name=user_full_name
        ).pack()
    ]

    buttons_texts: List[str] = [
        i18n.get(
            "ban-button", 
            locale
        ),
        i18n.get(
            "unban-button", 
            locale
        ),
        i18n.get(
            "send-button", 
            locale
        )
    ]

    await answer_message(
        bot=bot,
        chat_id=settings.admin_id,
        buttons_level=2,
        callback_datas=buttons_callbacks,
        buttons_texts=buttons_texts,
        text=i18n.get(
            "send-text",
            user_full_name=user_full_name,
            user_id=user_id,
            message_text=message_text
        )
    )


@user_router.message(Command("donate"))
async def donate(
    command: CommandObject,
    redis: Redis,
    i18n: I18nContext,
    message: Message,
    settings: Settings,
    bot: Bot
) -> None:
    user_id: int = message.chat.id
    locale = await get_user_locale(
        user_id=user_id,
        redis=redis
    )
    provider_token: str = settings.provider_token.get_secret_value()
    reply_markup: InlineKeyboardMarkup = await customed_keyboard(
        pay=True,
        buttons_level=1,
        buttons_text=[
            i18n.get(
                "donate-button",
                locale
            )
        ]
    )

    if not provider_token:
        return await answer_message(
            bot=bot, 
            chat_id=user_id, 
            text=i18n.get(
                'error-provider-token',
                locale
            )
        )

    if not command.args or not command.args.isnumeric():
        return await answer_message(
            bot=bot, 
            chat_id=user_id, 
            text=i18n.get(
                'error-args',
                locale
            )
        )

    amount: int = int(command.args)
    title: str = i18n.get(
        "donate-title",
        locale
    )
    description: str = i18n.get(
        "donate-description",
        locale
    )
    payload: str = i18n.get(
        "donate-payload",
        locale
    )

    await message.answer_invoice(
        reply_markup=reply_markup,
        title=title,
        description=description,
        payload=payload,
        provider_token=provider_token,
        currency="XTR",
        prices=[
            LabeledPrice(
                label="XTR",
                amount=amount
            )
        ],
    )


@user_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
) -> None:
    await pre_checkout_query.answer(ok=True)


@user_router.message(F.successful_payment)
async def on_successful_payment(
    message: Message,
    redis: Redis,
    i18n: I18nContext,
    settings: Settings,
    bot: Bot
) -> None:
    assert message.successful_payment is not None

    if not message.from_user:
        return None
    
    user: User = message.from_user
    successful_payment: SuccessfulPayment = message.successful_payment
    user_id: int = user.id
    stars_amount: int = successful_payment.total_amount
    charge_id: str = successful_payment.provider_payment_charge_id
    special_code: str = generate_special_code()
    locale: str = await get_user_locale(
        user_id=user.id,
        redis=redis
    )

    await add_user_check(
        user_id=user_id,
        stars_amount=stars_amount,
        check_id=special_code,
        charge_id=charge_id
    )

    await answer_message(
        bot=bot, 
        chat_id=settings.admin_id, 
        text=i18n.get(
            'donate-admin',
            locale,
            stars_amount=stars_amount
        )
    )

    await answer_message(
        bot=bot, 
        chat_id=user_id, 
        text=i18n.get(
            'successful-payment',
            locale, 
            special_code=special_code
        )
    )


@user_router.message(Command("refund"))
async def refund(
    message: Message,
    redis: Redis,
    command: CommandObject,
    i18n: I18nContext,
    bot: Bot
) -> None:
    user_id: int = message.chat.id
    charge_id, stars_amount = await get_user_check(user_id=user_id)
    locale: str = get_user_locale(
        user_id=user_id,
        redis=redis
    )

    if not command.args:
        return await answer_message(
            bot=bot, 
            chat_id=user_id, 
            text=i18n.get(
                'error-args',
                locale
            )
        )

    if not charge_id or not stars_amount:
        return await answer_message(
            bot=bot, 
            chat_id=user_id, 
            text=i18n.get(
                'error-payment-check',
                locale
            )
        )

    await bot.refund_star_payment(
        user_id=user_id,
        telegram_payment_charge_id=charge_id
    )

    await refund_delete_check(
        charge_id=charge_id
    )

    await answer_message(
        bot=bot, 
        chat_id=user_id, 
        text=i18n.get(
            'successful-refund',
            locale,
            stars_amount=stars_amount
        )
    )


@user_router.callback_query(ButtonsCallbackInfos.filter(F.action == "user_send"))
async def user_send(
    callback: CallbackQuery,
    redis: Redis,
    fsm: FSMContext,
    i18n: I18nContext,
    bot: Bot
) -> None:
    if isinstance(callback.message, InaccessibleMessage):
        return None
    
    if not callback.message:
        return None

    message: Message = callback.message
    user_id: int = message.chat.id
    locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )

    await fsm.set_state(StateSend.text_send)
    await answer_message(
        bot=bot,
        chat_id=user_id,
        text=i18n.get(
            "fsm-send",
            locale
        )
    )


@user_router.message(StateSend.text_send)
async def message_send_text(
    message: Message,
    redis: Redis,
    fsm: FSMContext,
    settings: Settings,
    i18n: I18nContext,
    bot: Bot
) -> None:
    if not isinstance(message.from_user, User):
        return None
    
    if not message.text:
        return None
  
    user: User = message.from_user
    admin_id: int = settings.admin_id
    user_id: int = user.id
    user_full_name: str = user.full_name
    user_locale: str = await get_user_locale(
        user_id=user_id,
        redis=redis
    )
    admin_locale: str = await get_user_locale(
        user_id=admin_id,
        redis=redis
    )

    await answer_message(
        bot=bot,
        user_id=admin_id,
        text=message.text,
        buttons_level=1,
        button_texts=[
            i18n.get(
                'answer-button',
                admin_locale
            )
        ],
        callback_datas=[
            SendUserCallback(
                user_id=user_id,
                full_name=user_full_name
            ).pack()
        ]
    )

    await answer_message(
        bot=bot,
        chat_id=user_id,
        text=i18n.get(
            "fsm-send",
            user_locale
        )
    )

    await fsm.clear() 