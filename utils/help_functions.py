def bold(text):
    return f'<b>{text}</b>'


def cursive(text):
    return f'<i>{text}</i>'


def get_structured_dialog(old_dialog: str, request_type: str = 'client') -> str:
    client_point = "$Ты: "

    if request_type == 'analysis':
        client_point = "$Клиент: "

    live_dialog = '\n\n'.join(
        ("$Брокер: " + value if index % 2 == 0 else client_point + value) for index, value in enumerate(
            old_dialog.split(';;'))
    )

    return live_dialog