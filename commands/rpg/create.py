import discord

from discord.ext import commands
from resources.check import check_it
from resources.db import Database
from random import choice
from asyncio import sleep, TimeoutError


git = ["https://media1.tenor.com/images/adda1e4a118be9fcff6e82148b51cade/tenor.gif?itemid=5613535",
       "https://media1.tenor.com/images/daf94e676837b6f46c0ab3881345c1a3/tenor.gif?itemid=9582062",
       "https://media1.tenor.com/images/0d8ed44c3d748aed455703272e2095a8/tenor.gif?itemid=3567970",
       "https://media1.tenor.com/images/17e1414f1dc91bc1f76159d7c3fa03ea/tenor.gif?itemid=15744166",
       "https://media1.tenor.com/images/39c363015f2ae22f212f9cd8df2a1063/tenor.gif?itemid=15894886"]


class CreateClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.i = self.bot.items
        self.w_s = self.bot.config['attribute']['chance_enchant']
        self.cost = {
            "stone_of_crystal_wind": 1,
            "stone_of_crystal_water": 1,
            "stone_of_crystal_fire": 1
        }

    @check_it(no_pm=True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    @commands.check(lambda ctx: Database.is_registered(ctx, ctx))
    @commands.command(name='create', aliases=['criar'])
    async def create(self, ctx):
        """Comando especial usado para craftar joias para seu personagem"""
        data = await self.bot.db.get_data("user_id", ctx.author.id, "users")
        update = data

        msg = f"\n".join([f"{self.i[k][0]} `{v}` `{self.i[k][1]}`" for k, v in self.cost.items()])
        msg += "\n\n**OBS:** `PARA CONSEGUIR OS ITENS VOCE DEVE USAR OS COMANDOS` **ASH RECIPE** `E` **ASH CRAFT**"

        Embed = discord.Embed(
            title="O CUSTO PARA VOCE CRIAR UM ENCANTAMENTO:",
            color=self.bot.color,
            description=msg)
        Embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        Embed.set_thumbnail(url="{}".format(ctx.author.avatar_url))
        Embed.set_footer(text="Ashley ® Todos os direitos reservados.")
        await ctx.send(embed=Embed)

        cost = {}
        for i_, amount in self.cost.items():
            if i_ in data['inventory']:
                if data['inventory'][i_] < self.cost[i_]:
                    cost[i_] = self.cost[i_]
            else:
                cost[i_] = self.cost[i_]

        if len(cost) > 0:
            msg = f"\n".join([f"{self.i[key][0]} **{key.upper()}**" for key in cost.keys()])
            return await ctx.send(f"<:alert:739251822920728708>│`Lhe faltam esses itens para criar um encantamento:`"
                                  f"\n{msg}\n`OLHE SEU INVENTARIO E VEJA A QUANTIDADE QUE ESTÁ FALTANDO.`")

        def check_option(m):
            return m.author == ctx.author and m.content == '0' or m.author == ctx.author and m.content == '1'

        msg = await ctx.send(f"<:alert:739251822920728708>│`VOCE JA TEM TODOS OS ITEM NECESSARIOS, DESEJA CRIAR "
                             f"SUA JOIA AGORA?`\n**1** para `SIM` ou **0** para `NÃO`")
        try:
            answer = await self.bot.wait_for('message', check=check_option, timeout=30.0)
        except TimeoutError:
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")
        if answer.content == "0":
            await msg.delete()
            return await ctx.send("<:negate:721581573396496464>│`COMANDO CANCELADO!`")

        await msg.edit(content=f"<a:loading:520418506567843860>│`removendo os itens de custo da sua conta...`")
        for i_, amount in self.cost.items():
            update['inventory'][i_] -= amount
            if update['inventory'][i_] < 1:
                del update['inventory'][i_]

        await msg.edit(content=f"<:confirmed:721581574461587496>│`itens retirados com sucesso...`")
        await sleep(2)

        await msg.edit(content=f"<a:loading:520418506567843860>│`Sorteando qual encantamento vai ser criado...`")
        await sleep(2)

        equips_list = list()
        for ky in self.bot.config['equips'].keys():
            for k, v in self.bot.config['equips'][ky].items():
                equips_list.append((k, v))

        list_items = []
        for i_, amount in self.w_s.items():
            list_items += [i_] * amount
        enchant = choice(list_items)

        await msg.edit(content=f"<:confirmed:721581574461587496>│`encantamento sorteado com sucesso...`")
        await sleep(2)

        await msg.edit(content=f"<a:loading:520418506567843860>│`Adicionando` {self.i[enchant][0]} "
                               f"**1 {self.i[enchant][1]}** `para sua conta...`")

        try:
            update['inventory'][enchant] += 1
        except KeyError:
            update['inventory'][enchant] = 1

        await sleep(2)
        await msg.edit(content=f"<:confirmed:721581574461587496>│{self.i[enchant][0]} `1` **{self.i[enchant][1]}** "
                               f"`adicionado ao seu inventario de equipamentos com sucesso...`")

        img = choice(git)
        embed = discord.Embed(color=self.bot.color)
        embed.set_image(url=img)
        await ctx.send(embed=embed)
        await self.bot.db.update_data(data, update, 'users')
        await self.bot.data.add_sts(ctx.author, "create", 1)


def setup(bot):
    bot.add_cog(CreateClass(bot))
    print('\033[1;32m( 🔶 ) | O comando \033[1;34mCREATE\033[1;32m foi carregado com sucesso!\33[m')
