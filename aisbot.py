from telegram.ext import Updater, CommandHandler, InlineQueryHandler, ChosenInlineResultHandler
from telegram import ParseMode, InlineQueryResultLocation, \
						 InputTextMessageContent, InlineQueryResultArticle
from telegram.utils.helpers import escape_markdown
from configparser import ConfigParser
from data import VesselInfo, LastPosdate
from uuid import uuid4
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

def sig_handler(signal, frame):
    print('Cleaning Up')
    sys.exit(0)

def vesselinfo(bot, update, args):
	# args become an argument when CommandHandler optional_args is set to True 
	v = VesselInfo(mmsi = args[0])
	cursor = v.get_vessel_info()
	res = cursor.fetchall()
	print(update)

	for value in res :
		text = '''
		MMSI : {}
		Name : {}
		Coordinate: {}, {}
		Destination : {}
		ETA : {}
		SOG : {}
		COG : {}
		Date : {}
		Country : {}'''.format(value[0], value[1], value[2] , value[3], value[4], value[5], value[6], value[7], value[10], value[12])

		update.message.reply_text(text = text)
		update.message.reply_location(latitude = value[2], longitude = value[3])

def globallastposdate(bot, update, args):
	lastposdate = LastPosdate()
	cursor = lastposdate.get_global_last_posdate()
	res = cursor.fetchone()

	text = '''<b>Now</b> : {} 
			  <b>Maria (192.168.20.52)</b>
			  <b>Max ID Maria</b> :  {}
			  <b>Last Posdate Maria</b> : {}
			  <b>Delay Maria</b> : {}'''.format(res[0],res[1],res[2],res[3])
	update.message.reply_text(text = text, parse_mode = 'HTML')

def inlinequery(bot, update):
	"""Handle the inline query."""
	print(update)
	query = update.inline_query.query
	v = VesselInfo()
	cursor = v.get_vessel_info_by_keyword(query)
	res = cursor.fetchall()
	arr = []

	for value in res :
		text = "{} ({})".format(value[1], value[0])
		arr.append(
			InlineQueryResultLocation(
				type = 'location',
				id = value[0],
				latitude = value[3],
				longitude = value[2],
				title = text
			)
		)

	update.inline_query.answer(arr)

def say_hello(bot, update, user_data, chat_data, update_queue):
	v = VesselInfo(mmsi = update.chosen_inline_result.result_id)
	cursor = v.get_vessel_info()
	res = cursor.fetchall()

	for value in res :
		text = '''
		MMSI : {}
		Name : {}
		Coordinate: {}, {}
		Destination : {}
		ETA : {}
		SOG : {}
		COG : {}
		Date : {}
		Country : {}'''.format(value[0], value[1], value[2] , value[3], value[4], value[5], value[6], value[7], value[10], value[12])

		#update.message.reply_text(text = text)
		print(bot)
		print(update)
		print(update_queue)
		bot.send_message(update._effective_user.id, text = text)
    	
def main() :
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
	print('bot start')
	updater.dispatcher.add_handler(CommandHandler('mmsi', vesselinfo,  None, False, True))
	updater.dispatcher.add_handler(CommandHandler('globallastposdate', globallastposdate,  None, False, pass_args = True))
	updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))
	updater.dispatcher.add_handler(ChosenInlineResultHandler(say_hello, pass_user_data = True, pass_chat_data = True, pass_update_queue = True))
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()