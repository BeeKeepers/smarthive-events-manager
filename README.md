# SmartHive - Event Manager

Smarthive events managing service. Receives events from AMQP broker (configured)
in *settings.json* and manages them. This includes:

  - Storing for later analysis.
  - Publishing "attack" events, for visualization on control panel.

## Development

### Dependencies

  - pika

### Installation

Just configure *settings.json* according to environment.

### Run

Run main app

```bash
python main.py
```

## Deployment

TBD
