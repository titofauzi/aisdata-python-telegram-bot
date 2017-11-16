from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from configparser import ConfigParser
from data import VesselInfo
import signal
import sys
import logging

# Bot Configuration
config = ConfigParser()
config.read_file(open('config.ini'))

# Connecting the telegram API
# Updater will take the information and dispatcher connect the message to
# the bot
updater = Updater(token=config['DEFAULT']['token'])

#updater.start_webhook(listen='127.0.0.1', port=5500, url_path='aisbot')
#updater.bot.set_webhook(webhook_url='https://ais.gemilang-ananta.co.id/aisbot', certificate=open('/etc/httpd/ssl/ais.crt', 'rb'))

def start(bot, updates, args):
	print(args)
	updates.message.reply_text('Hello World!')

def hello(bot, update):
	print('Hello triggered')
	update.message.reply_text(
		'Hello {}'.format(update.message.from_user.first_name)
	)

def sig_handler(signal, frame):
    print('Cleaning Up')
    sys.exit(0)

def vesselinfo(bot, update, args):
	v = VesselInfo(args[0])
	cursor = v.get_vessel_info()
	res = cursor.fetchall()
	print(res[0])

	for value in res :
		update.message.reply_text(value[0] + value[1])

	
def main() :
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
	print('bot start')
	updater.dispatcher.add_handler(CommandHandler('start', start, None, False, True))
	updater.dispatcher.add_handler(CommandHandler('hello', hello))
	updater.dispatcher.add_handler(CommandHandler('mmsi', vesselinfo,  None, False, True))
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()