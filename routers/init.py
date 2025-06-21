from aiogram import Router

from routers.broker import broker_router

router = Router(name=__name__)

router.include_router(broker_router)
