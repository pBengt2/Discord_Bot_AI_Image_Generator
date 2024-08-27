import pip
from git import Repo

pip.main(['install', 'upgrade'])

# non-cuda
#pip.main(['install', r'torch'])
#pip.main(['install', r'torchvision'])
#pip.main(['install', r'torchaudio'])

pip.main(['install', r'torch --extra-index-url https://download.pytorch.org/whl/cu117'])
pip.main(['install', r'torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117'])

pip.main(['install', 'accelerate'])
pip.main(['install', r'diffusers[torch]'])

pip.main(['install', r'git+https://github.com/huggingface/diffusers'])
pip.main(['install', r'GitPython'])

git_url = r"https://github.com/huggingface/diffusers.git"
repo_dir = r""  # TODO: Add full path to your repo directory
Repo.clone_from(git_url, repo_dir)

pip.main(['install', 'transformers'])
pip.main(['install', 'accelerate'])
pip.main(['install', 'scipy'])
pip.main(['install', 'safetensors'])
