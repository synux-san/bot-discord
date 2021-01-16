import psycopg2
from os import environ
from datetime import datetime, timedelta
from math import ceil

"""
	variables utiles
"""

emoji_devil = '😈'
emoji_yes = '✅'
emoji_no = '❎'
emoji_close = '❌'
emoji_night = '🌃'
emoji_day = '🌄'
emoji_sad = '😞'
emoji_death = '☠'
emoji_vote = lambda : ['0⃣', '1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '8⃣', '9⃣', '🔟']



"""
	here will be function
"""


	# retourne [heures, minutes, secondes] de type int
current_time = lambda : map(int, datetime.now().strftime("%H:%M:%S").split(":"))

	
	# retourne un objet de type datetime
delta_time = lambda heures, minutes, seconds : timedelta(hours=heures, minutes=minutes, seconds=seconds)


def get_timeout(start, Timeout=timedelta(seconds=30)):
	""" retourne le timeout restant """
	current = delta_time(*current_time())
	return (Timeout - (current - start)) if ((current - start) < Timeout) else '01'


async def vote_message(channel, players):
	"""
		cette fonction envoie les messages de votes par nombre de 10 candidats par messages, ainsi on peut avoir autant de participants que voulus
	"""
	start_slice = 0
	end_slice = len(emoji_vote())
	messages = {}
	for page in range(ceil(len(players)/10)):
		text = []
		embed = discord.Embed(title="VOTE", color=0x093951)
		# assossiaciation cadidats et emoji(en nombre de candidat)
		for emoji_n, player in dict(zip(emoji_vote()[:len(players[start_slice:end_slice:])], players[start_slice:end_slice:])).items():
			text += [emoji_n + ' : ' + str(player)]
		test += ['🚮 : ennuler son vote']
		embed.add_field(name="liste des candidats : ", value='\n'.join(text))
		msg = await channel.send(embed=embed)
		for emoji_n in emoji_vote()[:len(players[start_slice:end_slice]):]:
			await msg.add_reaction(emoji_n)
		await msg.add_reaction('🚮')
		# sauvegarde message : liste des candidats associés
		messages[msg] = players[start_slice:end_slice:]
		start_slice += 10
		end_slice += 10
	return messages


async def to_vote(bot, messages, channel, players, Timeout=40):
	looking_for_react = True        # for waiting for reaction
	Timeout = timedelta(seconds=Timeout) # le temps total à attendre
	start = delta_time(*current_time())
	total_voted = 0
	vote = {}
		#	--------------	#
	def check(reaction, user):
		""" return True si un {player in players} vote """
		return (str(reaction.emoji) in emoji_vote())
	await channel.send("les votes peuvent à present commencer!!!") 
	while looking_for_react:
		timeout = str(module.get_timeout(start))[-2::]
		try:
			reaction, reactor = await bot.wait_for('reaction_add', timeout=float(timeout), check=check)
		except asyncio.TimeoutError:
			looking_for_react = False
		else:
			if (reaction.message.id in [msg.id for msg in messages.keys()] and reactor in players):
				if str(reaction.emoji) == '🚮' and reactor in list(vote.keys()):
					vote.pop(reactor)
				elif str(reaction.emoji) in emoji_vote():
					if reactor not in vote.keys():
						vote[reactor] = messages[reaction.message][emoji_vote().index(str(reaction.emoji))]
						total_voted += 1
					elif reactor in vote.keys():
						await channel.send(f"{reactor.name}, vous avez déjà voté pour {vote[reactor].name} ")
						await reaction.message.remove_reaction(reaction.emoji, reactor)
			if total_voted == len(players):
				await channel.send("Tous le monde a déjà voté")
				looking_for_react = False
	return vote


async def channel_creation(ctx, channel_name, members):
	channel = await ctx.guild.create_text_channel(name=channel_name)
	await channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False, embed_links=False, attach_files=False, read_message_history=False)
	await channel.set_permissions(ctx.guild.me, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
	for member in members:
		await channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
	return channel


