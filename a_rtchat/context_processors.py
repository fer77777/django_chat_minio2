from .views import _get_user_chat_group

def chat_context(request):
    """Provee los mensajes del chat del usuario para el widget flotante en todas las páginas."""
    if request.user.is_authenticated:
        try:
            chat_group = _get_user_chat_group(request.user)
            messages = chat_group.chat_messages.all()[:40]
            return {"widget_chat_messages": messages}
        except Exception:
            return {"widget_chat_messages": []}
    return {"widget_chat_messages": []}
