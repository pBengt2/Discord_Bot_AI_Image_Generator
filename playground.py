import image_gen as ig

model_name = r"stablediffusionapi/albedobase-xl"
temp_num_images = 4
styles = "pastel"
pos_prompts = "pastel,cherry_blossom,blue_eyes"
neg_prompts = "city,indoors"

ig.generate_random_image(current_model=model_name, num_images=temp_num_images, styles="", set_prompts=pos_prompts, optional_prompts="", set_negative_prompts=neg_prompts)
