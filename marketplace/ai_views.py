import json

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .ai_agent import get_agent_reply
from .models import Enquiry, Property, RealtorLead, SavedProperty


def _read_json(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _throttled(request):
    # Lightweight per-session/account throttle to reduce accidental or scripted abuse.
    identity = f"user-{request.user.pk}" if request.user.is_authenticated else f"session-{request.session.session_key or request.META.get('REMOTE_ADDR', 'unknown')}"
    key = f"urbisora-ai-chat:{identity}"
    current = cache.get(key, 0)
    if current >= 24:
        return True
    cache.set(key, current + 1, timeout=60)
    return False


@require_POST
def chat(request):
    if _throttled(request):
        return JsonResponse({
            "reply": "You're sending messages a little quickly. Please wait a minute and try again.",
            "links": [], "cards": [], "mode": "guided",
        }, status=429)
    data = _read_json(request)
    message = data.get("message", "")
    if not isinstance(message, str):
        return JsonResponse({"error": "Message must be text."}, status=400)
    message = message.strip()
    if not message or len(message) > 2000:
        return JsonResponse({"error": "Enter a message between 1 and 2000 characters."}, status=400)
    history = data.get("history", [])
    if not isinstance(history, list):
        history = []
    # Only short user/assistant text history is accepted; roles cannot inject system instructions.
    cleaned_history = []
    for item in history[-8:]:
        if isinstance(item, dict) and item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
            cleaned_history.append({"role": item["role"], "content": item["content"][:1200]})
    result = get_agent_reply(message, cleaned_history, request.user)
    return JsonResponse(result)


@login_required
@require_POST
def action(request):
    data = _read_json(request)
    if data.get("confirmed") is not True:
        return JsonResponse({"ok": False, "reply": "No action was taken. Confirm the proposed action first."}, status=400)
    action_type = data.get("type")
    object_id = data.get("object_id")
    try:
        object_id = int(object_id)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "reply": "That action did not contain a valid record."}, status=400)

    if action_type in ("archive_property", "restore_property"):
        prop = Property.objects.filter(pk=object_id, owner=request.user).first()
        if not prop:
            return JsonResponse({"ok": False, "reply": "I couldn't find that property in your own workspace. No changes were made."}, status=404)
        should_archive = action_type == "archive_property"
        if prop.is_archived == should_archive:
            return JsonResponse({"ok": True, "reply": f"“{prop.title}” is already {'archived' if should_archive else 'restored'}."})
        prop.is_archived = should_archive
        prop.save(update_fields=["is_archived", "updated_at"])
        return JsonResponse({"ok": True, "reply": f"Done. “{prop.title}” is now {'archived from public search' if should_archive else 'restored to your workspace'}. It remains subject to the usual approval status."})

    if action_type == "save_property":
        prop = Property.objects.filter(
            pk=object_id, review_status=Property.Review.APPROVED, is_archived=False
        ).first()
        if not prop:
            return JsonResponse({"ok": False, "reply": "That property is no longer publicly available to save. No changes were made."}, status=404)
        _, created = SavedProperty.objects.get_or_create(user=request.user, property=prop)
        return JsonResponse({"ok": True, "reply": f"“{prop.title}” has been added to your saved properties." if created else f"“{prop.title}” is already saved."})

    if action_type == "enquiry_status":
        enquiry = Enquiry.objects.filter(pk=object_id, property__owner=request.user).first()
        if not enquiry:
            return JsonResponse({"ok": False, "reply": "That enquiry is not part of your workspace. No changes were made."}, status=404)
        status = data.get("status")
        if status not in {choice[0] for choice in Enquiry.Status.choices}:
            return JsonResponse({"ok": False, "reply": "Choose a valid enquiry status."}, status=400)
        enquiry.status = status
        enquiry.save(update_fields=["status"])
        return JsonResponse({"ok": True, "reply": f"Enquiry #{enquiry.pk} was marked {enquiry.get_status_display().lower()}."})

    if action_type == "realtor_lead_status":
        lead = RealtorLead.objects.filter(pk=object_id, realtor=request.user).first()
        if not lead:
            return JsonResponse({"ok": False, "reply": "That realtor lead is not part of your workspace. No changes were made."}, status=404)
        status = data.get("status")
        if status not in {choice[0] for choice in RealtorLead.Status.choices}:
            return JsonResponse({"ok": False, "reply": "Choose a valid lead status."}, status=400)
        lead.status = status
        lead.save(update_fields=["status"])
        return JsonResponse({"ok": True, "reply": f"Realtor lead #{lead.pk} was marked {lead.get_status_display().lower()}."})

    return JsonResponse({"ok": False, "reply": "That operation is not available to the agent."}, status=400)
