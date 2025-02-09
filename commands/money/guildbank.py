import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice, randint
from resources.utility import ERRORS


class GuildBank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.money = 0
        self.gold = 0
        self.silver = 0
        self.bronze = 0

        self.money_ = 0
        self.gold_ = 0
        self.silver_ = 0
        self.bronze_ = 0

        self.st = []

        self.items_events = {
                             "Wrath of Nature Capsule": ["WrathofNatureCapsule", 100],
                             "Ultimate Spirit Capsule": ["UltimateSpiritCapsule", 200],
                             "Sudden Death Capsule": ["SuddenDeathCapsule", 400],
                             "Inner Peaces Capsule": ["InnerPeacesCapsule", 600],
                             "Eternal Winter Capsule": ["EternalWinterCapsule", 800],
                             "Essence of Asura Capsule": ["EssenceofAsuraCapsule", 1000],
                             "Divine Caldera Capsule": ["DivineCalderaCapsule", 1250],
                             "Demoniac Essence Capsule": ["DemoniacEssenceCapsule", 1500]
                             }

    def status(self):
        for v in self.bot.data_cog.values():
            self.st.append(v)

    @staticmethod
    def format_num(num):
        a = '{:,.0f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return d

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='treasure', aliases=['tesouro'])
    async def treasure(self, ctx):
        """Comando usado pra ver a quantia de dinheiro de um server
        Use ash treasure"""
        data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")

        self.money = data['treasure']['total_money'] + data['data']['total_money']
        self.gold = data['treasure']['total_gold'] + data['data']['total_gold']
        self.silver = data['treasure']['total_silver'] + data['data']['total_silver']
        self.bronze = data['treasure']['total_bronze'] + data['data']['total_bronze']

        self.money_ = data['treasure']['total_money']
        self.gold_ = data['treasure']['total_gold']
        self.silver_ = data['treasure']['total_silver']
        self.bronze_ = data['treasure']['total_bronze']

        a = '{:,.2f}'.format(float(self.money))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        a_ = '{:,.2f}'.format(float(self.money_))
        b_ = a_.replace(',', 'v')
        c_ = b_.replace('.', ',')
        d_ = c_.replace('v', '.')

        msg = f"<:coins:519896825365528596>│ **{ctx.author}** No total há **R$ {d}** de `ETHERNYAS` dentro desse " \
              f"servidor!\n {self.bot.money[2]} **{self.format_num(self.gold)}** | " \
              f"{self.bot.money[1]} **{self.format_num(self.silver)}** | " \
              f"{self.bot.money[0]} **{self.format_num(self.bronze)}**\n\n" \
              f"`SENDO` **{d_}** `DISPONIVEL PARA COMANDOS DO` **ASH GUILD** `AINDA TEM AS PEDRAS`\n" \
              f"{self.bot.money[2]} **{self.format_num(self.gold_)}** | " \
              f"{self.bot.money[1]} **{self.format_num(self.silver_)}** | " \
              f"{self.bot.money[0]} **{self.format_num(self.bronze_)}**"

        await ctx.send(msg)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.group(name='guild', aliases=['guilda', 'servidor'])
    async def guild(self, ctx):
        """Comando usado pra retornar uma lista de todos os subcomandos de guild
                Use ash guild"""
        if ctx.invoked_subcommand is None:
            self.status()
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(name="Guilds Commands:",
                            value=f"{self.st[29]} `guild reward` Receba suas recompenças a cada hora.\n"
                                  f"{self.st[29]} `guild convert` Converta as pedras da guilda em ETHERNYAS.\n"
                                  f"{self.st[29]} `guild warehouse` Mande seus itens de evento para a GUILDA.")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text="Ashley ® Todos os direitos reservados.")
            await ctx.send(embed=embed)

    @check_it(no_pm=True)
    @commands.cooldown(1, 60.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, g_vip=True, cooldown=True, time=3600))
    @guild.group(name='reward', aliases=['recompensa'])
    async def _reward(self, ctx):
        """Comando que entrega sua recompença do servidor de cadastro."""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data
        if ctx.guild.id != data['guild_id'] and ctx.guild.id != 519894833783898112:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown']["guild reward"]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send("<:alert:739251822920728708>│`VOCE NAO É REGISTRADO NESSA GUILDA, ESSE COMANDO SO"
                                  " PODE SER EXECUTADO NA SUA GUILDA DE REGISTRO.`\n**Obs:** `Se sua guilda de "
                                  "registro nao existe mais, use o comando` **ash transfer** `e entre em outra"
                                  " guilda para que voce possa usufluir desses serviços`")

        amount = 0
        response = '`Caiu pra você:` \n'

        coins = randint(50, 150)
        energy = randint(25, 50)
        try:
            update['inventory']['coins'] += coins
        except KeyError:
            update['inventory']['coins'] = coins
        response += f"{self.bot.items['coins'][0]} `{coins}` `{self.bot.items['coins'][1]}`\n"
        try:
            update['inventory']['Energy'] += energy
        except KeyError:
            update['inventory']['Energy'] = energy
        response += f"{self.bot.items['Energy'][0]} `{energy}` `{self.bot.items['Energy'][1]}`\n"

        amount += (coins + energy)

        items = {
            'crystal_fragment_light': randint(10, 25),
            'crystal_fragment_energy': randint(10, 25),
            'crystal_fragment_dark': randint(10, 25)
        }

        chance = randint(1, 100)
        k_energy = 0
        if chance < 51:
            k_energy = randint(1, 3)
            response += f"{self.bot.items['Crystal_of_Energy'][0]} `{k_energy}` " \
                        f"`{self.bot.items['Crystal_of_Energy'][1]}`\n"

        amount += k_energy

        try:
            update['inventory']['Crystal_of_Energy'] += k_energy
        except KeyError:
            update['inventory']['Crystal_of_Energy'] = k_energy

        for k, v in items.items():
            try:
                update['inventory'][k] += v
                response += f"{self.bot.items[k][0]} `{v}` `{self.bot.items[k][1]}`\n"
                amount += v
            except KeyError:
                update['inventory'][k] = v
                response += f"{self.bot.items[k][0]} `{v}` `{self.bot.items[k][1]}`\n"
                amount += v

        amount = amount * 100
        response += '```dê uma olhada no seu inventario com o comando: "ash i"```'

        a = '{:,.2f}'.format(float(amount))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        # DATA DO SERVIDOR ATUAL
        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild
        if update_guild['treasure']['total_money'] > amount:
            update_guild['treasure']['total_money'] -= amount
            await self.bot.db.update_data(data_guild, update_guild, 'guilds')
        else:
            data_ = await self.bot.db.get_data("user_id", ctx.author.id, "users")
            update_ = data_
            del update_['cooldown']["guild reward"]
            await self.bot.db.update_data(data_, update_, 'users')
            return await ctx.send(f"<:negate:721581573396496464>│`SUA GUILDA NAO TEM DINHEIRO PARA BANCAR ESSE "
                                  f"COMANDO ELE IRIA RETIRAR DO TESOURO` **R${d}** `DE ETHERNYAS, MAS NAO"
                                  f"DESANIME USE O COMANDO` **ASH TESOURO** `E FIQUE TENTE NOVAMENTE!`")

        await self.bot.db.update_data(data, update, 'users')
        msg = "POR SER REGISTRADO NESSE SERVIDOR " if ctx.author.id != 519894833783898112 else ""
        await ctx.send(f"<a:fofo:524950742487007233>│`{msg}VOCÊ GANHOU` "
                       f"✨ **MUITOS ITENS** ✨\n{response}\n`Que custou para os cofres do servidor a quantia de` "
                       f"**R${d} ETHERNYAS**, `Para saber quanto ainda tem no saldo do servidor use o comando` "
                       f"**ash tesouro**")
        await self.bot.data.add_sts(ctx.author, "guild_reward", 1)

    @check_it(no_pm=True, manage_messages=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx, g_vip=True, cooldown=True, time=86400))
    @guild.group(name='convert', aliases=["converter"])
    async def _convert(self, ctx):
        """Comando que converte o money disponivel para recompensar os membros do servidor."""

        # DATA DO SERVIDOR ATUAL
        data_guild = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
        update_guild = data_guild
        tot = 0
        for k in ['total_bronze', 'total_silver', 'total_gold']:

            if k == "total_bronze":
                tot += update_guild['treasure'][k]

            if k == "total_silver":
                tot += update_guild['treasure'][k] * 10

            if k == "total_gold":
                tot += update_guild['treasure'][k] * 100

            update_guild['treasure'][k] = 0

        update_guild['treasure']['total_money'] += tot
        await self.bot.db.update_data(data_guild, update_guild, 'guilds')

        a = '{:,.2f}'.format(float(tot))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')

        await ctx.send(f'<:confirmed:721581574461587496>│🎊 **PARABENS** 🎉 {ctx.author.mention} `Seu pedido foi'
                       f' aceito com sucesso, voce converteu todas as pedras do seu servidor em` '
                       f'**RS{d}** `ETHERNYAS`')
        await self.bot.data.add_sts(ctx.author, "guild_convert", 1)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @guild.group(name='warehouse', aliases=["w", "armazem"])
    async def _warehouse(self, ctx, *, item=None):
        if not self.bot.event_special:
            return await ctx.send(f"<:negate:721581573396496464>│`ATUALMENTE NAO TEM NENHUM EVENTO ESPECIAL!`")

        if item is None:
            return await ctx.send(f"<:negate:721581573396496464>│`VOCE PRECISA DIZER UM NOME DE UM ITEM!`")

        item_name = None
        for i in self.items_events.keys():
            if i.lower() == item.lower():
                item_name = i

        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        if item_name is not None:
            if self.items_events[item_name][0] in update['inventory'].keys():
                update['inventory'][self.items_events[item_name][0]] -= 1
                if update['inventory'][self.items_events[item_name][0]] < 1:
                    del update['inventory'][self.items_events[item_name][0]]
                await self.bot.db.update_data(data, update, 'users')

                g_data = await self.bot.db.get_data("guild_id", ctx.guild.id, "guilds")
                g_update = g_data

                try:
                    g_update['event']['Capsule'][self.items_events[item_name][0]] += 1
                except KeyError:
                    g_update['event']['Capsule'][self.items_events[item_name][0]] = 1

                try:
                    g_update['event']['points'] += self.items_events[item_name][1]
                except KeyError:
                    g_update['event']['points'] = self.items_events[item_name][1]

                await self.bot.db.update_data(g_data, g_update, 'guilds')

                return await ctx.send(f"<a:fofo:524950742487007233>│`VOCÊ ENVIOU UM` ✨ **ITEM DE EVENTO** ✨ "
                                      f"`COM SUCESSO`\n `Aproveite e olhe:` **ash top event** "
                                      f"`para saber se sua guilda esta indo bem!`")

            else:
                return await ctx.send(f"<:negate:721581573396496464>│`VOCE NAO TEM ESSE ITEM NO SEU INVENTARIO!`")
        else:
            return await ctx.send(f"<:negate:721581573396496464>│`VOCE PRECISA DIZER UM NOME DE UM ITEM DE EVENTO!`")

    @_convert.error
    async def _convert_error(self, ctx, error):
        if error.__str__() in ERRORS[11]:
            await ctx.send('<:negate:721581573396496464>│`Você não tem permissão para usar esse comando!`')

        if isinstance(error, commands.CheckFailure):
            if error.__str__() not in ERRORS:
                perms = ctx.channel.permissions_for(ctx.me)
                if perms.send_messages and perms.read_messages:
                    return await ctx.send(f"{error}")


def setup(bot):
    bot.add_cog(GuildBank(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mGUILDBANK\033[1;32m foi carregado com sucesso!\33[m')
