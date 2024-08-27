from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
import torch
import os
import random
import json

# TODO: Set params from discord... (inf steps / etc).
IMAGE_SCALE = 48  # 48

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = 'max_split_size_mb:512'

DISCORD_IMAGE_PATH = r'DiscordImages/'
DISCORD_IMAGE_BACKUP_PATH = r'DiscordImages/Backup/'

DEFAULT_SETTINGS_FILE = "ig_settings.json"

# TODO: Setup your defaults!
DEFAULT_STYLES = ""
DEFAULT_SET_PROMPTS = ""
DEFAULT_OPTIONAL_PROMPTS = ""
DEFAULT_SET_NEG_PROMPTS = ""
DEFAULT_OPTIONAL_NEG_PROMPTS = ""


def move_files_to_backup_directory(img_dir, backup_dir):
    for img in [os.path.join(img_dir, f) for f in os.listdir(img_dir)]:
        if img.endswith('.png'):
            try:
                os.rename(img, backup_dir + img.split(r"/")[-1])
            except FileExistsError:
                name = get_unique_name(backup_dir + img.split(r"/")[-1][0:-4])
                os.rename(img, name)


def generate_img_dimensions():
    aspect_ratio_w = 16
    aspect_ratio_h = 9
    size_multiplier = IMAGE_SCALE

    if (size_multiplier * aspect_ratio_h) % 8 == 0:
        extra_h = 0
    else:
        extra_h = (8 - (size_multiplier * aspect_ratio_h) % 8)

    if (size_multiplier * aspect_ratio_w) % 8 == 0:
        extra_w = 0
    else:
        extra_w = (8 - (size_multiplier * aspect_ratio_w) % 8)

    image_width = (aspect_ratio_w * size_multiplier) + extra_w
    image_height = (aspect_ratio_h * size_multiplier) + extra_h  # add extra height pixels to make divisible by 8

    return image_width, image_height


def generate_prompts(styles, set_prompts, optional_prompts, set_negative_prompts, negative_prompts):
    # style
    if len(styles) > 0:
        if random.randint(0, 1) == 0:
            temp_styles = styles.split(", ")
            cur_style = temp_styles[random.randint(0, len(temp_styles) - 1)]
            set_prompts = cur_style + ", " + set_prompts
    # prompts
    chance = max(3, int(len(optional_prompts)/2))
    for p in optional_prompts.split(", "):
        if p is not None and p != "":
            randomness = random.randint(1, chance)
            if random.randint(0, randomness) == 0:
                if len(set_prompts) == 0:
                    set_prompts = p
                else:
                    set_prompts += ", " + p

    # negative prompts
    for p in negative_prompts.split(", "):
        if p is not None and p != "":
            if random.randint(0, 1) == 0:
                set_negative_prompts += ", " + p

    return set_prompts, set_negative_prompts


def create_img_model(model_id=""):
    model_short_name = model_id.split(r"/")[-1][0:3]

    try:
        if "xl" in model_id.lower():
            pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
        else:
            pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
    except AttributeError:
        if "xl" not in model_id.lower():
            pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
        else:
            pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
    pipe = pipe.to("cuda")

    pipe.safety_checker = None

    return pipe, model_short_name


def get_unique_name(temp_name):
    if not os.path.isfile(temp_name + ".png"):
        return temp_name + ".png"

    last_valid_name_counter = 0
    file_name = temp_name + "_" + str(last_valid_name_counter) + ".png"
    while os.path.isfile(file_name):
        last_valid_name_counter += 1
        file_name = temp_name + "_" + str(last_valid_name_counter) + ".png"
    last_valid_name_counter += 1
    return file_name


def generate_random_image(current_model="", num_images=1, styles=DEFAULT_STYLES, set_prompts=DEFAULT_SET_PROMPTS, optional_prompts=DEFAULT_OPTIONAL_PROMPTS, set_negative_prompts=DEFAULT_SET_NEG_PROMPTS, negative_prompts=DEFAULT_OPTIONAL_NEG_PROMPTS, num_inference_steps=-1, guidance_scale=-1):
    image_width, image_height = generate_img_dimensions()
    pipe, model_short_name = create_img_model(current_model)

    b_rand_steps = steps == -1
    b_rand_scale = scale == -1

    num_inference_steps_min = 40
    num_inference_steps_max = 100
    guidance_scale_min = 3
    guidance_scale_max = 10

    all_images = []
    for temp_loop in range(num_images):
        # Model settings
        if b_rand_steps:
            num_inference_steps = random.randint(num_inference_steps_min, num_inference_steps_max)  # 50
        if b_rand_scale:
            guidance_scale = random.randint(guidance_scale_min, guidance_scale_max)  # 12  # how accurate to the prompts

        current_pos_prompts, current_neg_prompts = generate_prompts(styles, set_prompts, optional_prompts, set_negative_prompts, negative_prompts)

        print(current_model)
        print(current_pos_prompts)
        print(current_neg_prompts)

        with torch.cuda.amp.autocast():
            images = pipe([current_pos_prompts],
                          negative_prompt=[current_neg_prompts],
                          width=image_width,
                          height=image_height,
                          guidance_scale=guidance_scale,
                          num_inference_steps=num_inference_steps,
                          ).images

        image = images[0]
        temp_name = DISCORD_IMAGE_PATH + model_short_name + "_" + str(num_inference_steps) + "_" + str(guidance_scale) + "_" + current_pos_prompts.replace(", ", "_").replace(" ", "")
        file_name = get_unique_name(temp_name)

        image.save(file_name)
        all_images.append(file_name)
        print("saved: " + str(file_name))

    return all_images


def read_settings(settings_file=DEFAULT_SETTINGS_FILE):
    with open(settings_file, 'r') as f:
        json_str = json.load(f)

    json_obj = json.loads(json_str)

    return json_obj["model_name"], int(json_obj["num_images"]), json_obj["prompts"], json_obj["negative_prompts"], json_obj["optional_prompts"], json_obj["inference_steps"], json_obj["guidance_scale"]


model_name, temp_num_images, pos_prompts, neg_prompts, opt_prompts, steps, scale = read_settings(settings_file=DEFAULT_SETTINGS_FILE)
move_files_to_backup_directory(DISCORD_IMAGE_PATH, DISCORD_IMAGE_BACKUP_PATH)
generate_random_image(current_model=model_name, num_images=temp_num_images, styles="", set_prompts=pos_prompts, optional_prompts=opt_prompts, set_negative_prompts=neg_prompts, num_inference_steps=steps, guidance_scale=scale)
