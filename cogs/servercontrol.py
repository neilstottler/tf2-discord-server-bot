# Std Lib Imports
import socket
import os
import sys

# 3rd Party Imports
import discord
from discord.ext.commands import Cog, slash_command
import asyncssh
import asyncio

# Local Imports
from utils import load_config


global_config = load_config()
config = global_config.sftp

class Server(Cog):

    #/server <server to do> <command>
    #start, stop, restart
    @discord.slash_command(guild_ids=[global_config.bot_guild_ids])
    async def server(self, ctx, 
                     server: discord.Option(str, 'Select which server to interact with.', choices=global_config.servers, required=True), 
                     command: discord.Option(str, 'The command to send to the server.', choices=["start", "stop", "restart", "status"], required=True)):
        
        servers = global_config.servers
        commands = ["start", "stop", "restart"]

        #inputs
        # server, command
        #                            \/ needs to define the service name since they are different
        # systemctl --user <command> tf2-casual.service
        username = config[str(server)].username
        hostname = config[str(server)].hostname
        password = config[str(server)].password
        homedir = config[str(server)].homedir
        servicename = config[str(server)].servicename

        await ctx.respond(f":satellite: Sending {command} to {server} please wait. :satellite:")
        await ctx.edit(content=await server_command(username, hostname, password, command, servicename, homedir))
    
    @discord.slash_command(guild_ids=[global_config.bot_guild_ids])
    async def testing(self, ctx):
        print(type(global_config.servers))
        await ctx.respond(global_config.servers)
    
#server connecting
async def server_command(user, hostname, password, command, servicename, homedir):

    commands = ["start", "stop", "restart", "update", "ping"]

    async with asyncssh.connect(
        hostname,
        port=22, 
        username=user, 
        password=password,
        known_hosts=None
    ) as conn:
        
        #:white_check_mark: :x: :satellite: :octagonal_sign:
        #function for checking servive
        async def serverStatusChecker(servicename, hostname):
            service_status_raw = await conn.run(f'systemctl --user show {servicename} --property=ActiveState')
            service_status = service_status_raw.stdout.split('=')
            return f"The {servicename} on {hostname} is reporting a status of: " + service_status[1]

        #boolean version
        async def serverStatusCheckerBool(servicename):
            service_status_raw = await conn.run(f'systemctl --user show {servicename} --property=ActiveState')
            service_status = service_status_raw.stdout.split('=')
            print(service_status)
            #needs to be done this way otherwise it returns incorrectly...
            if service_status[1] == 'activating':
                return False
            elif service_status[1] == 'deactivating\n':
                return True
            elif service_status[1] == 'active':
                return True
            else:
                return False

        #start server
        async def serverStartService(servicename, hostname):
            #check if it's running first
            print(await serverStatusCheckerBool(servicename))
            if await serverStatusCheckerBool(servicename) is True:
                return f":warning: The {servicename} on {hostname} is already running! :warning:"
            else:
                #starting the service
                await conn.run(f'systemctl --user start {servicename}')
                return f":white_check_mark: The {servicename} on {hostname} has been started. :white_check_mark:"
            
        #stop server
        async def serverStopService(servicename, hostname):
            if await serverStatusCheckerBool(servicename) is False:
                return f":warning: The {servicename} on {hostname} is already stopped! :warning:"
            else:
                #stopping the service
                await conn.run(f'systemctl --user stop {servicename}')
                return f":octagonal_sign: The {servicename} on {hostname} has been stopped. :octagonal_sign:"
        
        #restart server
        async def serverRestartService(servicename, hostname):
            #is the service even there?
            if await serverStatusCheckerBool(servicename) is False:
                return f":warning: The {servicename} on {hostname} is not running! :warning:"
            else:
                #restart the service
                await conn.run(f'systemctl --user restart {servicename}')
                return f":white_check_mark: The {servicename} on {hostname} has been restarted. :white_check_mark:"
            

        #status - check status of service
        #start - check if service is running first, if not start server, check if server is actually up
        #stop - check if service is running, if it is, stop server, check that it actually stopped
        #restart - check if servive is running, restart accordingly
        if command =='status':
            return await serverStatusChecker(servicename, hostname)
        if command == 'start':
            return await serverStartService(servicename, hostname)
        if command == 'stop':
            return await serverStopService(servicename, hostname)
        if command =='restart':
            return await serverRestartService(servicename, hostname)
