# To Run:
    Setup cuda (if available)
    Setup your discord bot (see other guides online)
    Add your bot token to bot_loop TOKEN=r'[your_bot_token_here]'
    Add your directory path to pip_installs.py
    Run pip_installs.py (likely can update versions/etc of things first)
    Test run with playground.py

# Parameters:
    num= [number of images]
    prompts= [positive prompts]
    opt_prompts= [optional positive prompts, chance of appearing = #opt prompts/2]
    neg_prompts= [negative prompts]
    steps= [number of steps, 30 - 100 good for most cases)
    scale= [how much should it follow the prompts vs being creative, 3 - 12 good range, 3 being abstract/creative, 12 trying hard to match the prompts exactly)]
    model= [full model name (from model list above)]

# To use:
    example command: !rand_img num=5;model=stablediffusionapi/albedobase-xl;prompt=male,orc,battle_axe,black_hair;neg_prompts:shield,armor
