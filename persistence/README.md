# Persistence

## Подготовка

```bash
cp default_workspace/config.example.yaml default_workspace/config.user.yaml
# Отредактируйте config.user.yaml и укажите API-ключ
```

## Запуск

```bash
cd persistence
uv run persistence

# Каждый запуск — новая сессия
# Сообщения пишутся в каталог .history/
```
