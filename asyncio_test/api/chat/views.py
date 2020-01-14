from foxy_framework.server_global import g


async def chat(player, data):
    """
    群聊
    :param data:
        {
            "msg":"聊天内容"
        }
    """
    for p in g.clients:
        await p.send({
            'protocol_name': 'chat',
            'data': data
        })
