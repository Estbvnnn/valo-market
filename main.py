import os
import discord
from discord.ext import commands
import asyncio

# Intents et initialisation du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Variable d'environnement pour le token
my_secret = os.environ['TOKEN']

# Dictionnaire pour stocker les annonces (simple exemple en mémoire)
annonces = {}

# Fonction utilitaire pour envoyer un message privé à un utilisateur
async def send_dm(user, message):
    try:
        dm_channel = await user.create_dm()
        await dm_channel.send(message)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un message à {user.name}")

# Vérifie si l'utilisateur est un administrateur
def is_admin(ctx):
    return any(role.permissions.administrator for role in ctx.author.roles)

# Commande pour ajouter une annonce
@bot.command(name='ajouter')
async def ajouter(ctx, titre: str, prix: str, *, description: str):
    user = ctx.author
    annonce_id = len(annonces) + 1
    annonces[annonce_id] = {
        'user_id': str(user.id),
        'titre': titre,
        'prix': prix,
        'description': description
    }
    message = (f"Annonce ajoutée !\n**ID de l'annonce**: {annonce_id}\n**Titre**: {titre}\n**Prix**: {prix}\n**Description**: {description}")
    await send_dm(user, message)

# Commande pour afficher les annonces
@bot.command(name='annonces')
async def afficher_annonces(ctx):
    user = ctx.author
    if not annonces:
        message = "Aucune annonce disponible."
    else:
        annonces_message = "Annonces en cours:\n"
        for annonce_id, annonce in annonces.items():
            annonces_message += (f"**Annonce {annonce_id}**\n"
                                 f"**Titre**: {annonce['titre']}\n"
                                 f"**Prix**: {annonce['prix']}\n"
                                 f"**Description**: {annonce['description']}\n\n")
        message = annonces_message

    await send_dm(user, message)

# Commande pour supprimer une annonce
@bot.command(name='supprimer')
async def supprimer(ctx, annonce_id: int):
    user = ctx.author
    annonce = annonces.get(annonce_id)

    # Debug: Vérifiez les valeurs
    print(f"Utilisateur ID: {user.id}")
    print(f"Annonce ID: {annonce_id}")
    print(f"Annonce: {annonce}")

    if annonce and annonce['user_id'] == str(user.id):
        # Confirmer la suppression
        confirmation_message = (f"Êtes-vous sûr de vouloir supprimer l'annonce {annonce_id} ?\n"
                                f"Répondez par `oui` pour confirmer ou `non` pour annuler.")
        def check(msg):
            return msg.author == user and msg.channel.type == discord.ChannelType.private

        await send_dm(user, confirmation_message)

        try:
            # Attendre la réponse de l'utilisateur
            response = await bot.wait_for('message', timeout=60.0, check=check)
            if response.content.lower() == 'oui':
                annonces.pop(annonce_id)
                confirmation = f"Annonce {annonce_id} supprimée avec succès."
            else:
                confirmation = "Suppression annulée."
        except asyncio.TimeoutError:
            confirmation = "Temps écoulé pour la confirmation. Suppression annulée."

        await send_dm(user, confirmation)
    else:
        await send_dm(user, "Vous n'avez pas le droit de supprimer cette annonce.")

# Commande pour supprimer tous les messages dans un salon
@bot.command(name='purger')
@commands.has_permissions(administrator=True)
async def purger(ctx):
    if ctx.channel.type == discord.ChannelType.text:
        # Confirmation de la purge
        confirmation_message = ("Êtes-vous sûr de vouloir supprimer tous les messages dans ce salon ?\n"
                                "Répondez par `oui` pour confirmer ou `non` pour annuler.")
        def check(msg):
            return msg.author == ctx.author and msg.channel.type == discord.ChannelType.private

        await send_dm(ctx.author, confirmation_message)

        try:
            response = await bot.wait_for('message', timeout=60.0, check=check)
            if response.content.lower() == 'oui':
                # Supprimer tous les messages dans le salon
                await ctx.send("Suppression en cours...")
                await ctx.channel.purge()
                confirmation = "Tous les messages ont été supprimés."
            else:
                confirmation = "Purge annulée."
        except asyncio.TimeoutError:
            confirmation = "Temps écoulé pour la confirmation. Purge annulée."

        await send_dm(ctx.author, confirmation)
    else:
        await send_dm(ctx.author, "Cette commande ne peut être utilisée que dans un salon textuel.")

# Lancer le bot
bot.run(my_secret)
