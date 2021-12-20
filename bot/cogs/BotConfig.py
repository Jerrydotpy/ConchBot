import discord
from discord.ext import commands
import aiosqlite

class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_blacklist(self, id):
        db = await aiosqlite.connect('./bot/db/config.db')
        cursor = await db.cursor()

        await cursor.execute(f"SELECT id FROM blacklist WHERE id = {id}")
        result = await cursor.fetchone()

        await db.close()
        await cursor.close()

        return result is not None

    async def check_ff(self, guild):
        db = await aiosqlite.connect('./bot/db/config.db')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT familyfriendly FROM config WHERE guild_id = {guild.id}")
        check = await cursor.fetchone()
        if check is None:
            await cursor.execute(f"SELECT guild_id FROM config WHERE guild_id = {guild.id}")
            check0 = await cursor.fetchone()
            if check0 is None:
                await cursor.execute(f"INSERT INTO config (guild_id, familyfriendly) VALUES ({guild.id}, 0)")
            else:
                await cursor.execute(f"UPDATE config SET familyfriendly = 0 WHERE guild_id = {guild.id}")
            await db.commit()
            await cursor.close()
            await db.close()  
            return "Inactive"
        if check[0] == 1:  
            return "Active"
        elif check[0] == 0:
            return "Inactive"      
        elif check[0] == 2:
            return "fuf"

    @commands.group(invoke_without_command=True, disabled=True)
    async def config(self, ctx):
        embed = discord.Embed(title="Configuration Settings", colour=discord.Colour.gold())
        embed.add_field(name="Family Friendly Mode", value=f"Status: {await self.check_ff(ctx.guild)}\n "
        "DISCLAIMER: Family friendly mode does not apply to the bot's AI function.")
        await ctx.send(embed=embed)
    
    @config.command(disabled=True)
    async def ff(self, ctx, mode):
        db = await aiosqlite.connect('./bot/db/config.db')
        cursor = await db.cursor()
        status = await self.check_ff(ctx.guild)
        if status == "Active":
            await ctx.send("Family friendly mode is already active!")
        else:
            await cursor.execute(f"UPDATE config SET familyfriendly = 1 WHERE guild_id = {ctx.guild.id}")
            await ctx.send("Family friendly mode now active!")
        await db.commit()
        await cursor.close()
        await db.close()

def setup(client):
    client.add_cog(Config(client))