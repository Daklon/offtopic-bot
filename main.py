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
        self.antibot_keywords = cfg['parser']['antibot']
        self.accept = cfg['parser']['accept']
        self.deny = cfg['parser']['deny']
        self.user_request_id = []
        self.waiting_reponse = False
        self.warmode = True
        self.management_commands={
                self.cfg['commands']['enable_war_mode']:self.enable_war_mode,
                self.cfg['commands']['disable_war_mode']:self.disable_war_mode,
                }

    async def on_chat_message(self, msg):
        print(msg)
        # get the type of content (photo, text, new_chat_member,etc)
        content_type,_,_ = telepot.glance(msg)
        print(content_type)
        if content_type == "text":
            # translate the received message to lower case
            msg['text'] = msg['text'].lower()
            #if the message contains sudo its a management command
            if 'sudo' in msg['text'] and self.cfg['bot']['name'] in msg['text']:
                await self.management_processor(msg)
            #process normal messages
            else:
                await self.generic_processor(msg)

        # This will detect when the bot is added to a new group
        # and then he will introduce himself git the message 'group_intro'
        elif content_type == "new_chat_member":
            me = await self.bot.getMe()
            if msg['new_chat_participant']['id'] == me['id']:
                await self.sender.sendMessage(self.cfg['messages']['group_intro'],parse_mode="Markdown")
                
    
    # checks if ri returns an image, if not, then request another one until one is received
    def request_image(self):
        link = self.ri.get_image()
        while link is None:
            link = self.ri.get_image()
        return link

    #commands that configure the bot
    async def management_processor(self,msg):
        #check if the user has privileges and if there is the bot name
        if msg['from']['id'] in self.cfg['bot']['ownerids']: 
            #ignores the two first words (first is sudo, the second the bot name)
            func = self.management_commands.get(msg['text'].split(" ",2)[2])
            await func()
        else:
            #user has no privileges
             await self.sender.sendSticker(self.cfg['messages']['not_allowed_url'])

    async def enable_war_mode(self):
        self.warmode = True
        await self.sender.sendMessage(self.cfg['messages']['enable_war_mode'])
    
    async def disable_war_mode(self):
        self.warmode = False
        await self.sender.sendMessage(self.cfg['messages']['disable_war_mode'])

    async def generic_processor(self,msg):
        # if the message contains any keyword
        if any(word in msg['text'] for word in self.keywords) and not self.waiting_reponse:
            self.user_request_id.append(msg['from']['id'])
            self.waiting_reponse = True
            await self.sender.sendMessage(self.cfg['messages']['request'],parse_mode="Markdown")
        #if the bot has ben called by other user and receives a afirmative response
        elif msg['text'] in self.accept and self.waiting_reponse:
            if msg['from']['id'] in self.user_request_id:# if this user already has called the bot
                await self.sender.sendMessage(self.cfg['messages']['deny_retry'].format(msg['from']['username']),parse_mode="Markdown")
            else:#sends a message and a photo
                await self.sender.sendMessage(self.cfg['messages']['accept'],parse_mode="Markdown")
                await self.sender.sendPhoto(self.request_image())
                self.waiting_reponse = False
        #if the bot has been called by other user and receives a negative response
        elif msg['text'] in self.deny and self.waiting_reponse:
            await self.sender.sendMessage(self.cfg['messages']['deny'],parse_mode="Markdown")
            self.waiting_reponse = False
        
        #if detect any command from other bot answer with a custom message and return a photo
        elif any(word in msg['text'] for word in self.antibot_keywords) and self.warmode:
            await self.sender.sendMessage(self.cfg['messages']['antibot'])
            await self.sender.sendPhoto(self.request_image())
        

#This should be improved TODO
with open(sys.argv[1]+"/config.yaml", 'r') as yamlfile:
    cfg = yaml.safe_load(yamlfile)

TOKEN = cfg['bot']['token'] #read the telegram bot token from the config file

# create a handler for each telegram chat with a lifespan of "timeout"
# if timeout is reached without any new messages it will be destroyed
bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, OfftopicBotHandler, timeout=cfg['bot']['timeout']),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
