"""The entire ping-only bot feature, using only the public core contract."""

from botcore.api import Command, Registration, Response


def register(settings):
    reply = settings.get("reply", "🏓PONG")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("ping settings.reply must be nonempty text")

    async def ping(context):
        count = context.services.get("requests", 0)
        context.services.set("requests", count + 1)
        return Response(reply)

    return Registration(commands=(Command("ping", ping, help="Check bot responsiveness."),))
