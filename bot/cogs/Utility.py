import os
import platform
import datetime
import discord
from discord.ext import commands
import aiosqlite
import inspect
import os
from dotenv import load_dotenv
import psutil
import time
from bot.cogs.Currency import Currency
import asyncio
import sys
from jishaku.codeblocks import codeblock_converter

obj_Disk = psutil.disk_usage('/')
start_time = time.time()

env = load_dotenv()

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    async def get_update_info(self, version=None):
        db = await aiosqlite.connect("./bot/db/updates.db")
        cursor = await db.cursor()

        if version is None:
            await cursor.execute("SELECT MAX(version) FROM updates")
            result = await cursor.fetchone()
            version = result[0]
        await cursor.execute(f"SELECT name FROM updates WHERE version = '{version}'")
        name = await cursor.fetchone()
        await cursor.execute(f"SELECT desc FROM updates WHERE version = '{version}'")
        desc = await cursor.fetchone()
        await cursor.execute(f"SELECT updates FROM updates WHERE version = '{version}'")
        updates = await cursor.fetchone()
        await cursor.execute(f"SELECT published FROM updates WHERE version = '{version}'")
        published = await cursor.fetchone()

        await cursor.close()
        await db.close()        

        return version, name[0], desc[0], updates[0], published[0]

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            colour=discord.Colour.dark_red(),
            title=f"Pong! **__{round(self.client.latency * 1000)}__**"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        servers = list(self.client.guilds)
        embed = discord.Embed(title="Guilds", colour=ctx.author.colour)
        for x in range(len(servers)):
            embed.add_field(name=servers[x-1].name, value=servers[x-1].member_count, inline=False)
        embed.add_field(name="Total Guilds:", value=len(self.client.guilds))
        embed.add_field(name="Total Members:", value=len(set(self.client.get_all_members())))
        await ctx.send(embed=embed)
        await ctx.send(f"Total Guilds: {len(self.client.guilds)}\nTotal Members: {len(set(self.client.get_all_members()))}")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        await ctx.send({len(self.client.guilds)})

    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        e = discord.Embed(title='Uptime,', color=discord.Color.green())
        e.add_field(name="Time:", value=f"{days}**d**, {hours}**h**, {minutes}**m**, {seconds}**s**", inline=True)
        e.add_field(name="Time Lapse:", value=text, inline=False)
        await ctx.send(embed=e)

    @commands.command(aliases=["purge"])
    @commands.cooldown(1, 5, commands.BucketType.user) 
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount:int):
        if amount < 1:
            await ctx.send("You can't clear a negative amount.")
        embed = discord.Embed(
            colour = discord.Colour.purple(),
        )
        embed.add_field(name="Messages Cleared", value=f"{amount} messages cleared.")

        await ctx.channel.purge(limit=amount+1)
        await ctx.send(embed=embed, delete_after=5)
    
    @commands.command(aliases=["statistics", "info", "information"])
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def stats(self, ctx):
        uname = platform.uname()
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(title=f'{self.client.user.name} Stats', colour=ctx.author.colour)
        embed.add_field(name="Bot Name:", value=self.client.user.name)
        embed.add_field(name="Bot Id:", value=self.client.user.id)
        embed.add_field(name="Bot Version:", value="1.3.4")
        embed.add_field(name="Python Version:", value=platform.python_version())
        embed.add_field(name="Discord.py Version:", value=discord.__version__)
        embed.add_field(name="Total Guilds:", value=len(self.client.guilds))
        embed.add_field(name="Total Users:", value=len(set(self.client.get_all_members())))
        embed.add_field(name="Total Commands:", value=len(set(self.client.commands)))
        embed.add_field(name="Total Cogs:", value=len(set(self.client.cogs)))
        embed.add_field(name="Uptime:", value=f"{days}**d**, {hours}**h**, {minutes}**m**, {seconds}**s**", inline=True)
        embed.add_field(name="Uptime Lapse:", value=text)
        embed.add_field(name="Bot Developers:", value="UnsoughtConch")
        embed.add_field(name="Bot Developers Ids:", value="UnsoughtConch - 579041484796461076")
        await ctx.send(embed=embed)


    @commands.command(aliases=["github", "code"])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def source(self, ctx, *, command_name=None):
        # Source code of ConchBot github page
        conchbot_source_code_url = os.getenv("GITHUB_REPO_LINK")

        # Branch of ConchBot github page
        branch = os.getenv("GITHUB_REPO_BRANCH")

        embed = discord.Embed(title="ConchBot Source Code")

        # If Command Parameter is None
        if command_name is None:
            embed.add_field(name="Source:", value=conchbot_source_code_url, inline=False)
        else:
            # Get the command
            obj = self.client.get_command(command_name.replace('.', ' '))

            # If command cannot be found
            if obj is None:
                await ctx.send('Could not find command in my github source code.')

            # Get the source of the code
            src = obj.callback.__code__

            # Check if its a module
            module = obj.callback.__module__

            # Get the file name
            filename = src.co_filename

            # Check if module doesn't start with discord
            location = (
                module.replace('.', '/') + '.py'
                if module.startswith('discord')
                else os.path.relpath(filename).replace('\\', '/')
            )

            # Get the line of code for the command
            end_line, start_line = inspect.getsourcelines(src)

            # Go to the command url. Note: It is a permalink
            final_url = (f'{conchbot_source_code_url}/blob/{branch}/{location}#L{start_line}-L'
                     f'{start_line + len(end_line) - 1}')

            embed.add_field(name="Command Source:", value=final_url, inline=False)

        embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested {ctx.author.name}#{ctx.author.discriminator}")
        await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        check = ctx.author.guild_permissions.kick_members
        if check is True or ctx.author.id == 579041484796461076:
            await ctx.send("Are you sure you want me to leave the server? `yes` or `no.`")
            msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if "yes" in msg.content.lower():
                await ctx.send("I'm sorry you don't want me here anymore. If there was a problem or annoyance, you"
                " can feel free to join my support server. (https://discord.gg/PyAcRfukvc)")
                await ctx.guild.leave()
            elif "no" in msg.content.lower():
                await ctx.send("Thanks for deciding to keep me!")
            else:
                await ctx.send("Incorrect value. Aborting...")
        else:
            await ctx.send("You don't have permissions to make me leave!")

    @commands.group(invoke_without_command=True, aliases=["update"])
    async def updates(self, ctx):
        version, name, desc, updates, published = await self.get_update_info()
        
        embed = discord.Embed(title=f"**__ConchBot Update {name}__**", colour=ctx.author.colour)
        embed.add_field(name="**Update Name:**", value=name, inline=False)
        embed.add_field(name="**Description:**", value=desc, inline=False)
        embed.add_field(name="**Updates:**", value=updates, inline=False)
        embed.set_footer(text=f"ConchBot Update {version} | Published {published}")
        await ctx.send(embed=embed)

    @updates.command()
    @commands.is_owner()
    async def publish(self, ctx, version, *, content):
        db = await aiosqlite.connect("./bot/db/updates.db")
        cursor = await db.cursor()
        now = datetime.datetime.now()
        td = datetime.datetime.now()
        currenttime = datetime.time(hour=now.hour, minute=now.minute).isoformat(timespec='minutes')
        name, desc, updates = content.split(", ")

        await ctx.send("This is how it will look. Good?")

        embed = discord.Embed(title=name, colour=ctx.author.colour)
        embed.add_field(name="**Update Name:**", value=name, inline=False)
        embed.add_field(name="**Description:**", value=desc, inline=False)
        embed.add_field(name="**Updates:**", value=updates, inline=False)
        embed.set_footer(text=f"ConchBot Update {version} | Published {td.month}/{td.day}/{td.year} at {currenttime}")
        await ctx.send(embed=embed)

        msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)

        if "yes" in msg.content.lower():
            await cursor.execute(f"INSERT INTO updates (version, name, desc, updates, published) VALUES "
            f"('{version}', '{name}', '{desc}', '{updates}', '{td.month}/{td.day}/{td.year} at {currenttime}')")
            await ctx.send("Update published!")
        else:
            await ctx.send("Aborting...")

        await db.commit()
        await cursor.close()
        await db.close()

    @updates.command()
    async def list(self, ctx):
        db = await aiosqlite.connect("./bot/db/updates.db")
        cursor = await db.cursor()

        await cursor.execute("SELECT version FROM updates")
        versions = await cursor.fetchall()

        await cursor.close()
        await db.close()        

        embed = discord.Embed(title="ConchBot Updates", color=ctx.author.color)

        for version in versions:
            name = await self.get_update_info(version[0])
            embed.add_field(name=name[1], value=f"Update {version[0]}")
        embed.set_footer(text="To view a certain update, use 'cb update {version}.'")

        await ctx.send(embed=embed)

    @updates.command()
    async def info(self, ctx, version: int):
        version, name, desc, updates, published = await self.get_update_info(version)

        embed = discord.Embed(title=f"**__ConchBot Update {name}__**", colour=ctx.author.colour)
        embed.add_field(name="**Update Name:**", value=name, inline=False)
        embed.add_field(name="**Description:**", value=desc, inline=False)
        embed.add_field(name="**Updates:**", value=updates, inline=False)
        embed.set_footer(text=f"ConchBot Update {version} | Published {published}")
        await ctx.send(embed=embed)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must specify an amount of messages to clear.")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions required to purge messages.")
            return
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Your amount must be an integer greater than one.")
            return
        

    @commands.command(aliases=["close"])
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Ending Python process ConchBot... Goodbye")
        await self.client.logout()

    @commands.command()
    @commands.is_owner()
    async def editmoners(self, ctx, user:discord.Member, amount:int):
        await Currency.open_account(self, user)
        await Currency.update_bank(self, user, amount)
        await ctx.send(f"Successfully given {user.name} {amount} moners.")

    @commands.command(aliases=["pull"])
    @commands.is_owner()
    async def refresh(self, ctx):
        cog = self.client.get_cog("Jishaku")
        await cog.jsk_git(ctx, argument=codeblock_converter('stash'))
        await asyncio.sleep(2)
        await cog.jsk_git(
            ctx,
            argument=codeblock_converter(
                'pull --ff-only --allow-unrelated-histories https://www.github.com/ConchDev/ConchBot master'
            ),
        )

        await asyncio.sleep(2)
        restart = self.client.get_command('restart')
        await ctx.invoke(restart)

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        def restarter():
            python = sys.executable
            os.execl(python, python, * sys.argv)

        embed = discord.Embed(title="Bot Restarting...")
        embed.add_field(name="I'll be back soon...", value="Don't worry", inline=True)
        await ctx.send(embed=embed)
        restarter()

    @commands.command(aliases=["close"])
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Ending Python process ConchBot... Goodbye")
        await self.client.close()
    
    @commands.command()
    @commands.is_owner()
    async def edititems(self, ctx, user:discord.Member, item, amount:int):
        await Currency.open_account(self, user)
        await Currency.item_func(self, user, item, amount)
        await ctx.send(f"Successfully given {user.name} {amount} {item}s.")
    
    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx, val=None):
        if val is not None:
            await ctx.invoke(self.client.get_command(f'blacklist add {val}'))
        else:
            return await ctx.send("You can add or remove")
    
    @blacklist.command()
    async def add(self, ctx, id=None):
        if id is None:
            await ctx.send("You need the id of that user")
        else:
            db = await aiosqlite.connect("./bot/db/config.db")
            cursor = await db.cursor()
            await cursor.execute(f"SELECT id FROM blacklist WHERE id = {id}")
            result = await cursor.fetchone()
            if result is None:
                await cursor.execute(f"INSERT INTO blacklist (id) VALUES ({id})")
                await ctx.send("Member blacklisted.")
            else:
                await ctx.send("That Member is already blacklisted.")
            await db.commit()
            await cursor.close()
            await db.close()

    @blacklist.command()
    async def remove(self, ctx, id):
        if id is None:
            await ctx.send("You need the id of that user")
        else:
            db = await aiosqlite.connect("./bot/db/config.db")
            cursor = await db.cursor()
            await cursor.execute(f"SELECT id FROM blacklist WHERE guild_id = {ctx.guild.id}")
            result = await cursor.fetchone()
            blacklisted = result[0]
            if id not in blacklisted:
                await ctx.send("That ID is not blacklisted.")
            else:
                await cursor.execute(f"DELETE FROM blacklist WHERE guild_id = {ctx.guild.id}")
                await ctx.send("ID removed from blacklist.")
            await db.commit()
            await cursor.close()
            await db.close()

def setup(client):
    client.add_cog(Utility(client))
