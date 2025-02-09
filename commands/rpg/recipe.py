import copy
import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from resources.utility import paginator
from asyncio import TimeoutError

quant = 0


class RecipeClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color
        self.i = self.bot.items

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='craft', aliases=['construir'])
    async def craft(self, ctx, *, item=None):
        """Comando para criar itens de receitas, para fabricar suas armaduras."""
        global quant
        query = {"_id": 0, "user_id": 1, "inventory": 1, "recipes": 1}
        data_user = await (await self.bot.db.cd("users")).find_one({"user_id": ctx.author.id}, query)
        query_user = {"$inc": {}}

        recipes = copy.deepcopy(self.bot.config['recipes'])
        for k, v in self.bot.config['especial_recipes'].items():
            if k in data_user["recipes"]:
                recipes[k] = v

        if ctx.author.id in self.bot.comprando:
            return await ctx.send('<:alert:739251822920728708>│`VOCE JA ESTA EM PROCESSO DE COMPRA...`')

        self.bot.comprando.append(ctx.author.id)

        if item is not None:

            item = item.lower().replace(" ", "_")
            if item in recipes.keys():

                recipe = recipes[item]
                description = '**Custo:**'
                maximo = None

                for c in recipe['cost']:
                    try:
                        quant = data_user['inventory'][c[0]]
                    except KeyError:
                        quant = 0
                    description += f'\n{self.i[c[0]][0]} **{c[1]}**/`{quant}` `{self.i[c[0]][1]}`'

                description += '\n\n**Recompensa:**'

                for c in recipe['reward']:
                    try:
                        quant = data_user['inventory'][c[0]]
                    except KeyError:
                        quant = 0
                    description += f'\n{self.i[c[0]][0]} **{c[1]}**/`{quant}` `{self.i[c[0]][1]}`'

                _msg = "`Itens faltantes:`\n"
                for c in recipe['cost']:
                    try:
                        tempmax = data_user['inventory'][c[0]] // c[1]
                        if tempmax == 0:
                            _msg += f'<:alert:739251822920728708>|`Você não tem o item` **{c[0]}** ' \
                                    f'`suficiente no seu inventario.`\n'

                    except KeyError:
                        tempmax = 0
                        _msg += f'<:alert:739251822920728708>|`Você não tem o item` **{c[0]}** ' \
                                f'`suficiente no seu inventario.`\n'
                    if maximo is None or maximo > tempmax:
                        maximo = tempmax
                if _msg != "`Itens faltantes:`\n":
                    await ctx.send(_msg)

                description += '\n\n**Maximo que você pode craftar:** `{}`' \
                               '\n▶ **Craftar** `1`\n⏩ **Craftar** `2+`' \
                               '\n⏭ **Craftar o Maximo**\n❌ **Fechar**'.format(maximo)

                embed = discord.Embed(
                    title='Craft\n(Custo/Quantidade no inventario)',
                    color=self.bot.color,
                    description=description)

                msg = await ctx.send(embed=embed)
                emojis = ['▶', '⏩', '⏭', '❌']

                for c in emojis:
                    await msg.add_reaction(c)

                def check_reaction(react, member):
                    try:
                        if react.message.id == msg.id:
                            if member.id == ctx.author.id:
                                return True
                        return False
                    except AttributeError:
                        return False

                try:
                    reaction = await self.bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)
                except TimeoutError:
                    self.bot.comprando.remove(ctx.author.id)
                    return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito! Comando '
                                          'cancelado.`', delete_after=5.0)

                if reaction[0].emoji == '▶' and reaction[0].message.id == msg.id:
                    try:
                        for c in recipe['cost']:
                            if data_user['inventory'][c[0]] >= c[1]:
                                data_user['inventory'][c[0]] -= c[1]
                                if data_user['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1]
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1]

                elif reaction[0].emoji == '⏩' and reaction[0].message.id == msg.id:

                    def check_recipe(m):
                        if m.author.id == ctx.author.id and m.channel.id == ctx.channel.id:
                            if m.content.isdigit():
                                if int(m.content) > 0:
                                    return True
                        return False

                    msg_num = await ctx.send('<:alert:739251822920728708>│`Quantas receitas você quer fazer?`')
                    try:
                        resp = await self.bot.wait_for('message', check=check_recipe, timeout=60.0)
                    except TimeoutError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito:` **COMANDO'
                                              ' CANCELADO**')

                    while not self.bot.is_closed():
                        if int(resp.content) <= maximo:
                            break
                        await msg_num.delete()
                        msg_num = await ctx.send('<:alert:739251822920728708>│`Você nao consegue craftar essa '
                                                 'quantidade!`\n**Digite outro valor:**')
                        try:
                            resp = await self.bot.wait_for('message', check=check_recipe, timeout=60.0)
                        except TimeoutError:
                            self.bot.comprando.remove(ctx.author.id)
                            return await ctx.send('<:negate:721581573396496464>│`Desculpe, você demorou muito:` '
                                                  '**COMANDO CANCELADO**')

                    quant = int(resp.content)

                    try:
                        for c in recipe['cost']:
                            if data_user['inventory'][c[0]] >= c[1]:
                                data_user['inventory'][c[0]] -= c[1] * quant
                                if data_user['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1] * quant
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1] * quant

                elif reaction[0].emoji == '⏭' and reaction[0].message.id == msg.id:
                    if maximo < 1:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    try:
                        for c in recipe['cost']:
                            if data_user['inventory'][c[0]] >= c[1]:
                                data_user['inventory'][c[0]] -= c[1] * maximo
                                if data_user['inventory'][c[0]] < 1:
                                    if "$unset" not in query_user.keys():
                                        query_user["$unset"] = dict()
                                    query_user["$unset"][f"inventory.{c[0]}"] = ""
                                    if f"inventory.{c[0]}" in query_user["$inc"].keys():
                                        del query_user["$inc"][f"inventory.{c[0]}"]
                                else:
                                    query_user["$inc"][f"inventory.{c[0]}"] = -c[1] * maximo
                            else:
                                self.bot.comprando.remove(ctx.author.id)
                                return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                                      'necessarios.`')
                    except KeyError:
                        self.bot.comprando.remove(ctx.author.id)
                        return await ctx.send('<:alert:739251822920728708>|`Você não tem todos os itens '
                                              'necessarios.`')

                    for c in recipe['reward']:
                        query_user["$inc"][f"inventory.{c[0]}"] = c[1] * maximo

                if reaction[0].emoji == "❌" and reaction[0].message.id == msg.id:
                    await msg.delete()
                    self.bot.comprando.remove(ctx.author.id)
                    return

                quantidade = 1
                if reaction[0].emoji == '⏩' and reaction[0].message.id == msg.id:
                    quantidade = quant
                if reaction[0].emoji == '⏭' and reaction[0].message.id == msg.id:
                    quantidade = maximo

                await msg.delete()
                cl = await self.bot.db.cd("users")
                await cl.update_one({"user_id": data_user["user_id"]}, query_user, upsert=False)
                await ctx.send(f"<a:fofo:524950742487007233>│🎊 **PARABENS** 🎉 `O ITEM` ✨ **{item.upper()}** ✨ "
                               f"`FOI CRAFTADO` **{quantidade}X** `COM SUCESSO!`")
                await self.bot.data.add_sts(ctx.author, "craft", 1)
            else:
                await ctx.send('<:negate:721581573396496464>|`Esse item não existe ou nao é craftavel.`')
        else:
            await ctx.send('<:negate:721581573396496464>|`DIGITE UM NOME DE UM ITEM. CASO NAO SAIBA USE O COMANDO:`'
                           ' **ASH RECIPE** `PARA VER A LISTA DE ITENS CRAFTAVEIS!`')
        self.bot.comprando.remove(ctx.author.id)

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='recipe', aliases=['receita', 'recipes'])
    async def recipe(self, ctx, page: int = 0):
        """Lista de receitas disponiveis."""
        recipes = copy.deepcopy(self.bot.config['recipes'])
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        for k, v in self.bot.config['especial_recipes'].items():
            if k in data["recipes"]:
                recipes[k] = v
        embed = ['Recipes', self.color, '`Para craftar um item use:`\n**ash craft nome_do_item**\n\n']
        num = page - 1 if page > 0 else None
        await paginator(self.bot, self.bot.items, recipes, embed, ctx, num)


def setup(bot):
    bot.add_cog(RecipeClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mRECIPE_SYSTEM\033[1;32m foi carregado com sucesso!\33[m')
