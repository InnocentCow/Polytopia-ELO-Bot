import discord
from discord.ext import commands
from pbwrap import Pastebin
from models import db, Team, Game, Player, Lineup, Tribe, Squad, SquadGame, SquadMember
from bot import config, logger
import csv

try:
    pastebin_api = config['DEFAULT']['pastebin_key']
except KeyError:
    logger.warn('pastebin_key not found in config.ini - Pastebin functionality will be limited')
    pastebin_api = None


class GameIO_Cog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['gex', 'gameexport'])
    async def game_export(self, ctx):

        with open('games_export.csv', mode='w') as export_file:
            game_writer = csv.writer(export_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            header = ['ID', 'Winner', 'Home', 'Away', 'Date', 'Home1', 'Home2', 'Home3', 'Home4', 'Home5', 'Away1', 'Away2', 'Away3', 'Away4', 'Away5']
            game_writer.writerow(header)

            query = Game.select().where(Game.is_completed == 1)
            for q in query:
                row = [q.id, q.winner.name, q.home_team.name, q.away_team.name, str(q.date)]

                pquery = Lineup.select().where(Lineup.game == q.id)
                home_players = []
                away_players = []
                for lineup in pquery:
                    if lineup.team == q.home_team:
                        home_players.append(lineup.player.discord_name)
                    else:
                        away_players.append(lineup.player.discord_name)

                home_players.extend([''] * (5 - len(home_players)))
                away_players.extend([''] * (5 - len(away_players)))
                row += home_players + away_players
                print(row)
                game_writer.writerow(row)

        pb = Pastebin(pastebin_api)
        pb_url = pb.create_paste_from_file(filepath='games_export.csv', api_paste_private=1, api_paste_expire_date='2W', api_paste_name='Polytopia Game Data')
        await ctx.send(f'Game data has been export to the following URL: {pb_url}')


def setup(bot):
    bot.add_cog(GameIO_Cog(bot))
