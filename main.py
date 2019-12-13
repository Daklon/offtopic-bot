import sys
import yaml
import asyncio
import telepot
from reddit import Reddit_Interface
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space, per_application

class OfftopicBotHandler(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(OfftopicBotHandler, self).__init__(*args, **kwargs)
        self.request_user_id = None
        self.ri = Reddit_Interface(sys.argv[2],sys.argv[3])
        with open(sys.argv[1]+"/config.yaml", 'r') as yamlfile:
            self.cfg = yaml.safe_load(yamlfile)
        self.keywords = cfg['parser']['keywords']
        self.accept = cfg['parser']['accept']
        self.deny = cfg['parser']['deny']
        self.user_request_id = []
        self.waiting_reponse = False

    async def on_chat_message(self, msg):
        print(msg)
        content_type,_,_ = telepot.glance(msg)
        if content_type == "text":
            if any(word in msg['text'] for word in self.keywords) and not self.waiting_reponse:
                self.user_request_id.append(msg['from']['id'])
                self.waiting_reponse = True
                await self.sender.sendMessage(self.cfg['messages']['request'],parse_mode="Markdown")

            elif msg['text'] in self.accept and self.waiting_reponse:
                link = self.ri.get_image()
                while link is None:
                    link = self.ri.get_image()
                if msg['from']['id'] in self.user_request_id:
                    await self.sender.sendMessage(self.cfg['messages']['deny_retry'].format(msg['from']['username']),parse_mode="Markdown")
                else:
                    await self.sender.sendMessage(self.cfg['messages']['accept'],parse_mode="Markdown")
                    await self.sender.sendPhoto(self.ri.get_image())
                    self.waiting_reponse = False
            
            elif msg['text'] in self.deny and self.waiting_reponse:
                await self.sender.sendMessage(self.cfg['messages']['deny'],parse_mode="Markdown")
                self.waiting_reponse = False
        elif content_type == "new_chat_member":
            me = await self.bot.getMe()
            if msg['new_chat_participant']['id'] == me['id']:
                await self.sender.sendMessage(self.cfg['messages']['group_intro'],parse_mode="Markdown")


#Initialization
with open(sys.argv[1]+"/config.yaml", 'r') as yamlfile:
    cfg = yaml.safe_load(yamlfile)

TOKEN = cfg['bot']['token']

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, OfftopicBotHandler, timeout=cfg['bot']['timeout']),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
