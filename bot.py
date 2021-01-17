import discord
import asyncio
import module
from os import environ
from sys import stderr
from discord.ext import commands
from traceback import print_exception
from math import floor
from random import shuffle



intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$lg', intents=intents)

bot.remove_command('help')
# ▬


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="Loup dans la Bergerie"))


@bot.command(name='create', help="Debut de jeu")
async def create(ctx, *to_invit: discord.Member):
	"""
		créer une partie de jeu et gérer le jeu.
	"""
	
	# Commande à executer uniquement sur un serveur, pas de messages privés
	if ctx.guild == None:
		raise commands.NoPrivateMessage()
	
	# l'invitation s'étend sur tout le serveur si les participants ne sont pas initialisés
	to_invit = list(to_invit)
	if (to_invit == []):
		async for client in ctx.guild.fetch_members(limit=None):
			to_invit.append(client)
	to_invit = tuple(to_invit)
		
	###			MESSAGE D'INVITATION 		###
	invit_message = f"{ctx.author.name} vous invite pour une partie à Gravenviille.\n {module.emoji_yes} pour accepter\n {module.emoji_no} pour refuser\n {module.emoji_close} pour stoper l'ajout de participant (uniquement {ctx.author.name}#{ctx.author.discriminator})"
		#	============================	#
	embed = discord.Embed(title="Invitation", color=0x9e9210)
	embed.add_field(name="\uFEFF", value=invit_message, inline=False)
	message = await ctx.send(embed=embed)
	
	await message.add_reaction(module.emoji_yes)
	await message.add_reaction(module.emoji_no)
	await message.add_reaction(module.emoji_close)
		#	==========================	#
	
	###		GET PLAYERS		###
		#	===variables===	#
	looking_for_react = True			# Espérer une nouvelle reaction
	Timeout = module.timedelta(seconds=30)	 # le temps total d'attente
	start = module.delta_time(*(module.current_time())) # heures de debut
	player_list = {}					# joueur : rôle
		#	--------------	#
		
	def check(reaction, user):
		"""booleen de recherche de reaction"""
		return ((str(reaction.emoji) == module.emoji_yes) or (str(reaction.emoji) == module.emoji_no) or str(reaction.emoji) == module.emoji_close)
		#	--------------	#
	
	while looking_for_react:
		# timeout, la partie seconds
		timeout = str(module.get_timeout(start))[-2::]
		try:
			reaction, reactor = await bot.wait_for('reaction_add', timeout=float(timeout), check=check)
		except asyncio.TimeoutError:
			looking_for_react = False
		else:
			if (reaction.message.id == message.id and reactor in to_invit):
				if reactor.guild_permissions.administrator:
					await ctx.send(f"Désolé {reactor.name}, les membres avec la permission administrateur activée ne peuvent pas jouer car leur rôle permet de voir les salons privés. {module.emoji_sad}")
				elif reaction.emoji == module.emoji_yes:
					if reactor not in player_list:
						player_list[reactor] = ""
				elif reaction.emoji == module.emoji_no:
					if reactor in player_list:
						player_list.pop(reactor)
				elif (reaction.emoji == module.emoji_close and reactor.id == ctx.author.id):
					looking_for_react = False
	
		#	---------------------	#
	if len(players) < min_player:
		return await ctx.send(f"Il faut au minimum {min_player} joueurs. Reviens une prochaine fois avec plus de joueur")
		# message de rôle à envoyer en DM
	
	await ctx.send(f"Liste des participants : {', '.join(map(str, [player.name for player in player_list.keys()]))}")
	
	###		ASSIGNER DES RÔLES		###
		#	======variables======	#
	players = list(player_list.keys())
	begin_limit = 0
	min_player = 4
	limit = floor(len(players[::])/2)
	shuffle(players)
	role_message = lambda player, role, server, invite : f"{player.name}, vous avez obtenu le rôle du renard\n$lginfo {role} pour plus d'information.\n\nDans 20 secondes les votes commancent sur le serveur {ctx.guild.name}"
	
	if len(players) > 6:
		begin_limit = 1
		player_list[players[0]] = "entrainé"
		
		embed = discord.Embed(title="Information", color=0x35874f)
		embed.add_field(name="\uFEFF", value=role_message(player=player_list[0], role="entrainé", server=ctx.guild.name, invite=villager_channel.create_invite()))
		await player[0].send(embed=embed)
	
	villagers = players[begin_limit:limit]
	for villager in villagers:
		player_list[villager] = "villageois"
		
		embed = discord.Embed(title="Information", color=0x35874f)
		embed.add_field(name="\uFEFF", value=role_message(player=villager, role="villageois", serveur=ctx.guild.name, invite=villager_channel.create_invite()))
		await villager.send(embed=embed)
	
	impostors = players[limit::]
	for impostor in impostors:
		player_list[impostor] = "impostor"
		role_message = f"{impostor.name}, vous avez obtenue le rôle imposteur\n -> $lginfo imposteur pour plus d'information.\n\nDans 20 secondes les votes commencent sur le serveur {ctx.guild.name}"
		
		embed = discord.Embed(title="Information", color=0x35874f)
		embed.add_field(name="\uFEFF", value=role_message)
		await impostor.send(embed=embed)
	###	imformation joueur imposteur : rôle à envoyer à la fin du jeu	###
	role_embed = discord.Embed(title="Information", color=0x9A106D)
	role_embed.add_field(name="Imposteurs", value=', '.join([str(impostor.name) for impostor in impostors]))

	###		CREATION DES DEUX SALONS VILLAGEOIS ET IMPOSTEUR		###
	villager_channel = await channel_creation(ctx=ctx, name="Villageois", members=villagers)
	impostor_channel = await channel_creation(ctx=ctx, name="Imposteurs", members=players)
	
	# le temps pour verifier son rôle et revenir sur le serveur
	await asyncio.sleep(20)
	###		PARTIE VOTE		###
	night_or_day = -1		# nuit == 0 et jour == 1
		
	while (villagers != [] and impostors != []):
		night_or_day += 1
			### ===la nuit=== ###
		if (night_or_day % 2) == 0:
			await villager_channel.send(f"Il fait nuit ...{module.emoji_night}")
			await impostor_channel.send(f"Il fait nuit. Il est l'heure de proceder au vote pour sacrifier un villageois {module.emoji_devil}")
			messages = await module.vote_message(channel=impostor_channel, players=villagers)
			vote = await module.to_vote(bot=bot, messages=messages, channel=ctx, players=impostors)
			
			if vote != {}:
				killed = max(list(vote.values()), key=list(vote.values()).count)
				if (((night_or_day/2)%2) == 0 and players[0] == killed): # au nuit paire
					first_match_killer = list(vote.keys()[list(vote.values()).index(players[0])])
					revenge = await player[0].send("{players[0].name}, {first_match_killer.name} a voter pour votre mort. Que feras-tu?\n{module.emoji_yes} : pour le laiser en vie\n{module.emoji_no} : pour l'éliminer.\nVous avez 10 secondes")
					await revenge.add_reaction(module.emoji_yes)
					await revenge.add_reaction(module.emoji_no)
					try:
						reaction, reactor = await bot.wait_for('reaction_add', timeout=10.0, check=check)
					except asyncio.TimeoutError:
						pass
					else:
						if reaction.emoji == module.emoji_yes:
							impostors.remove(first_match_killer)
							module.kill_perm(channel=impostor_channel, member=first_match_killer)
							module.kill_perm(channel=villager_channel, member=first_match_killer)
							await villager_channel.send(f"RIP, {first_match_killer.name} a été éliminé(e)")
				villagers.remove(killed)
				module.kill_perm(channel=villager_channel, member=killed)
				await villager_channel.send(f"RIP, {killed.name} a été éliminé(e).")
			else:
				await villager_channel.send("Les imposteurs n'ont pas attaqué le village cette nuit.")
			
			### ===le jour=== ###
		else:
			await villager_channel.send(f"...Et le jour parvint {module.emoji_day}. Les imposteurs ne sont pas tous exterminés. Qui pensent-tu être le plus susceptible d'être imposteur? Place au vote.")
			players = villagers + impostors
			messages = await module.vote_message(channel=villager_channel, players=players)
			vote = await module.to_vote(bot=bot, messages=messages, channel=villager_channel, players=players)
			
			if vote != {}:
				killed = max(list(vote.values()), key=list(vote.values()).count)
				villagers.remove(killed)
				await villager_channel.send(f"{killed.name} a été eliminé(e)")
				players.remove(killed)
				module.kill_perm(channel=villager_channel, member=killed)
				if killed in villager:
					villager.remove(killed)
				else:
					impostor.remove(killed)
					module.kill_perm(channel=impostor_channel, member=killed)
			else:
				await villager_channel.send("Personne n'as été éliminé(e)")
	
	impostor_channel.send("Ça y est c'est la fin... {module.emoji_death}")
	wlist = []
	if impostors != []: wlist = impostors
	elif villagers != []: wlist = villagers
	s = "" if (len(wlist)<2) else "s"
	winners = []
	for winner in wlist:
		winners += [str(winner)]
	if winner != []:
		embed = discord.Embed(title=f"Gagnant{s}", color=0x9A0B4D)
		name = "Imposteur" if impostors != [] else "Villageois"
		embed.add_field(name=name, value=', '.join(winners))
		await villager_channel.send(embed=embed)
		await villager_channel.send(embed=role_embed)
	###	suppression des salons utilisés	###
	await impostor_channel.delete()
	await villager_channel.send("Le salon sera supprimé dans une minute")
	await asyncio.sleep(60)
	await villager_channel.delete()
	

@bot.command(name='info', help="Information sur un rôle")
async def info(ctx, role=""):
	"""
		Donner les informations sur un rôle donné
	"""
	rappel = "Les crochets tels que [] ou <> ne sont pas à utiliser lors de l'execution des commandes."
	embed = discord.Embed(title="Information", color=0x9A004D)
	if role != "":
		embed.add_field(name="Rappel : ", value=rappel, inline=True)
		embed.add_field(name="Utilisation : ", value="$lginfo [rôles]", inline=False)
		if role.lower() == "villageois" or role.lower() == "vil":
			embed.add_field(name="Villageois", value="Alias : vil")
			embed.add_field(name="But : ", value="Éliminer tous les imposteurs")
			embed.add_field(name="Description : ", value=" Il vote le jour pour eliminer un autres villageois suspect d'être un imposteur\nIl gagne la partie si tous les imposteurs sont éliminés")
		elif role.lower() == "imposteur" or role.lower() == "imp":
			embed.add_field(name="Imposteur", value="Alias : imp")
			embed.add_field(name="Description : ", value="Il est avant tout un villageois. Il peut voter la nuit pour éliminer un villageois et le jour pour en éliminer un autre. son rôle est de defendre ses semblables pour qu'il soit en vie jusqu'à la fin du jeu.\nIl gagne la partie si tous les villageois sont éliminés.")
		elif role.lower() == "entrainé" or role.lower() == "ent":
			embed.add_field(name="L'entrainé", value="Alias : ent")
			embed.add_field(name="Description : ", value="Description : Au nuit paire, si il obtient plus de vote pour mourir, il peut tuer un des imposteurs qui a voté pour sa mort.")
		else:
			embed.add_field(name="\uFEFF", value=f"Le rôle {role.capitalize()} n'exite pas")
		await ctx.reply(embed=embed)
	else:
		await help(ctx, "info")

	###		====================		###


@bot.command(name='bug')
async def bug(ctx, *, report):
	develloper_id = 698327021385941002
	develloper = await bot.fetch_user(develloper_id)
	await develloper.send(f"bug de {ctx.author.name} dans {ctx.guild.name} : {report}")
	await ctx.send(f"Merci {ctx.author.name}, le bug a été bien envoyé.")


@bot.command(name='help')
async def help(ctx, arg=""):
	"""
		Avoir de l'aide sur les commandes
	"""
	embed = discord.Embed(title="Help", color=0x7A5B10)
	embed.add_field(name="Rappel", value="Les crochets tels que [] ou <> ne sont pas à utiliser lors de l'execution des commandes.")
	if arg == "":
		pass
	elif arg == "create":
		embed.add_field(name="Commande Create", value="Description: permet de créer un nouveau jeu. Les membres avec la permission administratreur activé ne peuvent pas jouer.")
		embed.add_field(name="Utilisation: ", value="$lgcreate <@member...>")
	elif arg == "info":
		embed.add_field(name="Commande Info", value="Description : permet d'avoir des informations sur un rôle du jeu")
		embed.add_field(name="Utilisation : ", value="$lginfo [rôle...]")
	else:
		embed.add_field(name="\uFEFF", value="La commande {arg} n'est pas trouvée.")
	await ctx.send(embed=embed)


###		PARTIE DE MANIEMENT DES ERREURS		###

@bot.event
async def on_command_error(ctx, error):
	"""
		Intercepter les erreurs et envoyer les raisons ou mettre dans le terminal si l'erreur n'est pas definie au prealable parmis les eventuelles erreurs
	"""
	
	if isinstance(error, commands.NoPrivateMessage):
		await ctx.author.send(f"{ctx.author.name}, cette commande n'est pas disponible en messages privés")
	
	elif isinstance(error, commands.errors.CheckFailure):
		await ctx.send(f"{ctx.author.name}, tu n'as pas le droit de faire ça")
	
	elif isinstance(error, commands.errors.CommandNotFound):
		pass
	
	else:
		print_exception(type(error), error, error.__traceback__, file=stderr)

	###		=========================		###


bot.run(environ['TOKEN'])