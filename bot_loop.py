import os
import discord
from discord.ext.commands import Bot
import json
from subprocess import call

import functools

# TODO: Refactor so people don't accidentally check in or share their bot token...
TOKEN = r''  # TODO: Add your bot token! DO NOT CHECK IN OR SHARE YOUR BOT TOKEN
INTENTS = discord.Intents.all()

DISCORD_IMG_DIRECTORY = r'DiscordImages/'
bot = Bot(intents=INTENTS, command_prefix='!')


@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


def start_image_gen():
    return call([r"venv_37_64b\Scripts\python.exe", "image_gen.py"])


async def run_blocking(fun_to_call, *args, **kwargs):
    func = functools.partial(fun_to_call, *args, **kwargs)
    return await bot.loop.run_in_executor(None, func)


@bot.command()
async def upload_images(ctx):
    for img in [os.path.join(DISCORD_IMG_DIRECTORY, f) for f in os.listdir(DISCORD_IMG_DIRECTORY)]:
        if img.endswith(".png"):
            await ctx.send(file=discord.File(img))
            await ctx.send(img.split(r"/")[-1].split(r"\\")[-1])


@bot.command()
async def rand_img(ctx):
    args = str(ctx.message.content)[len("!rand_img"):]
    if ctx.guild.get_member(bot.user.id).status == discord.Status.do_not_disturb:
        await ctx.send('Bot is busy... Please try again when status is Online (green)!')
        return
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name='Generating images...'))
    channel = ctx.channel
    if str(channel) == "dummy-short-name":  # TODO: Can add frequently used models here...
        model_name = "dummy-username/dummy-full-name"  # TODO: ^ add model name
    else:
        model_name = ""

    num_images = 1
    prompts = ""
    opt_prompts = ""
    negative_prompts = ""
    inference_steps = -1
    guidance_scale = -1

    for arg in args.split(';'):
        arg = arg.lower()
        if "num" in arg:
            num_images = arg.split('=')[-1]
        elif "neg_prompt" in arg or "negative_prompt" in arg:
            temp_neg_prompts = arg.split('=')[-1]
            for neg_prompt in temp_neg_prompts.split(","):
                if len(negative_prompts) == 0:
                    negative_prompts = neg_prompt.replace("_", " ")
                else:
                    negative_prompts += ", " + neg_prompt.replace("_", " ")
        elif "prompt" in arg:
            temp_prompts = arg.split('=')[-1]
            for prompt in temp_prompts.split(","):
                if len(prompts) == 0:
                    prompts = prompt.replace("_", " ")
                else:
                    prompts += ", " + prompt.replace("_", " ")
        elif "optional" in arg:
            opt_temp_prompts = arg.split('=')[-1]
            for opt_prompt in opt_temp_prompts.split(","):
                if len(prompts) == 0:
                    opt_prompts = opt_prompt.replace("_", " ")
                else:
                    opt_prompts += ", " + opt_prompt.replace("_", " ")
        elif "model" in arg:
            model_name = arg.split('=')[-1]
        elif "steps" in arg:
            inference_steps = int(arg.split('=')[-1])
        elif "scale" in arg:
            guidance_scale = int(arg.split('=')[-1])

    img_settings = {
        "model_name": model_name,
        "num_images": num_images,
        "prompts": prompts,
        "optional_prompts": opt_prompts,
        "negative_prompts": negative_prompts,
        "inference_steps": inference_steps,
        "guidance_scale": guidance_scale
    }
    json_object = json.dumps(img_settings)

    if model_name == "":
        await ctx.send('Invalid model...')
        return

    with open("ig_settings.json", "w") as outfile:
        json.dump(json_object, outfile)

    await ctx.send('Prompts: ' + str(prompts))

    if "xl" in model_name.lower():
        await ctx.send('Creating images (~4 minutes per image)')  # TODO: Time estimate depends on lots of factors...
    else:
        await ctx.send('Creating images (~30 seconds per image)')

    r = await run_blocking(start_image_gen)  # Pass the args and kwargs here

    if r == 0:
        await upload_images(ctx)
        await ctx.send(ctx.message.author.mention + " Images done.")
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='Ready...'))
    else:
        await ctx.send('Crash... ' + str(r))
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='Ready...'))


# Run the bot
bot.run(TOKEN)
