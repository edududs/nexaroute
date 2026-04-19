# Neonize Integration Guide

This guide shows how to map a WhatsApp/Neonize style message stream into Nexaroute.

## Recommended Shape

1. Trigger receives raw Neonize event.
2. Parser normalizes it into a typed incoming message.
3. Trigger publishes `InboundEvent` (`whatsapp.message.received`).
4. Handler returns `OutboundCommand` (`target="whatsapp.send_text"`).
5. Action executes command via Neonize send API.

## Contracts

- Trigger boundary: `BaseTrigger`
- Parser boundary: custom parser port (project-specific)
- Outbound transport boundary: `BaseAction`

## Event Example

```python
InboundEvent(
    name="whatsapp.message.received",
    source="neonize",
    payload={
        "message_id": "abc",
        "chat_id": "5511...@s.whatsapp.net",
        "sender_display": "Alice",
        "text": "hello",
        "is_group": False,
    },
)
```

## Command Example

```python
OutboundCommand(
    name="whatsapp.send_text.command",
    target="whatsapp.send_text",
    payload={
        "chat_id": "5511...@s.whatsapp.net",
        "text": "Bot | Alice: hello",
        "reply_to_message_id": "abc",
    },
)
```

## Practical Reference

A validated reference implementation exists in the sibling project `projects/nexaroute_lab` under `src/nexaroute_lab/neonize_example/`.

Use it as a blueprint for:

- trigger lifecycle and thread-safe publishing
- parser adaptation
- action routing by command target
