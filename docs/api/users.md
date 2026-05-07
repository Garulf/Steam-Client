# Users

Provides access to previously logged-in Steam accounts read from `loginusers.vdf`.

```python
for user in steam.users:
    print(user.user.data.PersonaName, user.is_most_recent)
```

::: steam_client.login_users
