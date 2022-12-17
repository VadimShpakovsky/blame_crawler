# Intro

Tool for searching authors of code which matches defined pattern. It finds lines across codebase 
matched defined pattern and extract author of last changes with `git blame`.

# Installation

```shell
pip install -r requirements.txt
```

# Usage

```shell
python crawler.py \
  -ru https://github.com/my-repo \ 
  -rp path/to/repo \
  -d dir/in/repo \
  -s "Boom!"
```

Run `python crawler.py --help` for more details.
