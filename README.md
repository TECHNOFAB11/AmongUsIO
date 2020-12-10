<div align="center">

![banner](.images/banner.png)

# AmongUsIO
[![ci](https://gitlab.com/TECHNOFAB/amongusio/badges/master/pipeline.svg?key_text=Pipeline)](https://gitlab.com/TECHNOFAB/amongusio/-/commits/master)
[![codacy](https://img.shields.io/codacy/grade/7a406c97da5546488d4a28829ce7134e?label=Code%20Quality&logo=codacy)](https://www.codacy.com/gl/TECHNOFAB/amongusio)
[![python versions](https://img.shields.io/pypi/pyversions/amongus?label=Versions&logo=python&logoColor=white)](https://pypi.org/project/amongus/)
[![project version](https://img.shields.io/pypi/v/amongus?label=PyPi&logo=pypi&color=%23FFD43B&logoColor=white)](https://pypi.org/project/amongus/)
[![discord](https://img.shields.io/discord/747858042007060613?color=7289da&label=Discord&logo=discord&logoColor=white)](https://tecf.de/amongusio-discord)
[![made with python](https://img.shields.io/badge/Made%20with-Python-007ec6.svg)](https://www.python.org/)
[![black](https://img.shields.io/badge/Code%20Style-black-000.svg)](https://github.com/psf/black)

Asynchronous Python Among Us Client

</div>

## Note
> This repository is mirrored from [Gitlab][gitlab-repo] to [Github][github-repo].
> 
> Most features like Issues, MRs etc. are disabled on [Github][github-repo], please use the
> [Gitlab repository][gitlab-repo] for these

## Installation
```sh
git clone https://gitlab.com/TECHNOFAB/amongusio
// or 
git clone https://github.com/TECHNOFAB11/amongusio

cd amongusio
python -m pip install . 
```

## Example
```python
import amongus

client = amongus.Client(name="Bot")

client.run(region="EU")
```
> see [the examples folder](examples) for more


[gitlab-repo]: https://gitlab.com/TECHNOFAB/amongusio
[github-repo]: https://github.com/TECHNOFAB11/amongusio

## Roadmap / TODO

> see [TODO.md](TODO.md)
