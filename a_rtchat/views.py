from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import ChatmessageCreateForm
from .models import ChatGroup, GroupMessage
from .rag import KnowledgeBaseEmpty, LocalRag, LocalRagConfigurationError, LocalRagError


CHAT_GROUP_NAME = "ai-chat"
BOT_USERNAME = "botty"


@login_required
def chat_view(request):
    chat_group = _get_user_chat_group(request.user)
    chat_messages = chat_group.chat_messages.all()[:40]
    form = ChatmessageCreateForm()

    if request.method == "POST":
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()

            message2 = _create_bot_message(chat_group, message.body)
            context = {
                "message": message,
                "message2": message2,
                "user": request.user,
            }
            # Si viene del widget flotante, el JS ya mostró la burbuja del usuario
            # → devolver SOLO la respuesta del bot para evitar el duplicado
            if request.POST.get("widget_mode"):
                return render(request, "a_rtchat/partials/chat_messages_p.html", {**context, "widget_mode": True})
            if request.htmx or request.headers.get("HX-Request"):
                return render(request, "a_rtchat/partials/chat_messages_p.html", context)
            return render(request, "a_rtchat/partials/chat_messages_p.html", context)

    return render(request, "a_rtchat/chat.html", {"chat_messages": chat_messages, "form": form})


@login_required
def limpiar_chat_view(request):
    """Vacía todos los mensajes del chat del usuario autenticado."""
    chat_group = _get_user_chat_group(request.user)
    chat_group.chat_messages.all().delete()
    if request.htmx:
        return render(request, "a_rtchat/partials/empty_chat.html")
    # Redirigir según de dónde vino la petición
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)


def _get_user_chat_group(user) -> ChatGroup:
    """Crea o recupera una sala de chat exclusiva y limpia para cada usuario."""
    group_name = f"chat-user-{user.username}"
    chat_group, _created = ChatGroup.objects.get_or_create(group_name=group_name)
    return chat_group


def _get_bot_user() -> User:
    bot_user, created = User.objects.get_or_create(
        username=BOT_USERNAME,
        defaults={"email": "botty@example.local", "is_active": False},
    )
    if created:
        bot_user.set_unusable_password()
        bot_user.save(update_fields=["password"])
    return bot_user


def _create_bot_message(chat_group: ChatGroup, question: str) -> GroupMessage:
    body = _answer_question(question)
    return GroupMessage.objects.create(
        body=body,
        author=_get_bot_user(),
        group=chat_group,
    )


def _answer_question(question: str) -> str:
    from django.conf import settings as django_settings
    from .openrouter_service import consultar_openrouter

    # Si está configurado OpenRouter (opción recomendada para VM / rapidez):
    provider = getattr(django_settings, 'AI_PROVIDER', 'openrouter')
    if provider == 'openrouter' and getattr(django_settings, 'OPENROUTER_API_KEY', ''):
        return consultar_openrouter(question)

    # Si se selecciona Ollama local o falta clave OpenRouter:
    try:
        answer = LocalRag.from_settings().answer(question)
    except KnowledgeBaseEmpty:
        # Responder con Ollama / datos de inventario
        return _answer_with_ollama_directly(question)
    except LocalRagConfigurationError as exc:
        return str(exc)
    except LocalRagError:
        return (
            "No pude procesar tu consulta. "
            "Verifica que Ollama este en ejecucion o configura tu clave OPENROUTER_API_KEY en .env."
        )

    if not answer.sources:
        return answer.text

    sources = ", ".join(answer.sources)
    return f"{answer.text}\n\nFuentes: {sources}"


def _answer_with_ollama_directly(question: str) -> str:
    """Responde usando Ollama local enviando el inventario estructurado como exige el requerimiento RF-08 / RF-09."""
    from django.conf import settings as django_settings
    from .openrouter_service import _obtener_inventario_json, SYSTEM_PROMPT_INVENTARIO

    try:
        from llama_index.llms.ollama import Ollama

        inventario_json = _obtener_inventario_json()
        prompt_completo = f"INVENTARIO:\n{inventario_json}\n\nPREGUNTA DEL USUARIO:\n{question}"

        llm = Ollama(
            model=django_settings.OLLAMA_CHAT_MODEL,
            base_url=django_settings.OLLAMA_BASE_URL,
            request_timeout=django_settings.OLLAMA_REQUEST_TIMEOUT,
            system_prompt=SYSTEM_PROMPT_INVENTARIO,
            context_window=django_settings.OLLAMA_NUM_CTX,
            additional_kwargs={
                "num_ctx": django_settings.OLLAMA_NUM_CTX,
                "num_predict": django_settings.OLLAMA_NUM_PREDICT,
                "temperature": 0.0,
            },
        )
        response = llm.complete(prompt_completo)
        return str(response)
    except ImportError:
        return (
            "Las dependencias de la IA no estan instaladas. "
            "Ejecuta: pip install -r requirements.txt"
        )
    except Exception as exc:
        return (
            f"No pude conectarme a Ollama local. "
            f"Verifica que Ollama este en ejecucion (puerto 11434) o usa OpenRouter. "
            f"Detalle: {exc}"
        )
