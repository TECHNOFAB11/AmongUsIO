<div align="center">

![banner](https://cdn.technofab.de/images/amongusio-banner.png)

# AmongUsIO
[![ci](https://img.shields.io/gitlab/pipeline/technofab/amongusio/master?label=Pipeline&logo=gitlab)](https://gitlab.com/TECHNOFAB/amongusio/-/commits/master)
[![docs](https://img.shields.io/readthedocs/amongusio/latest?label=Docs&logo=read%20the%20docs&logoColor=%23fff)](https://amongusio.readthedocs.io/en/latest/)
[![codacy](https://img.shields.io/codacy/grade/7a406c97da5546488d4a28829ce7134e?label=Code%20Quality&logo=codacy)](https://www.codacy.com/gl/TECHNOFAB/amongusio)
[![python versions](https://img.shields.io/pypi/pyversions/amongus?label=Versions&logo=python&logoColor=white)](https://pypi.org/project/amongus/)
[![project version](https://img.shields.io/pypi/v/amongus?label=PyPi&logo=pypi&color=%23FFD43B&logoColor=white)](https://pypi.org/project/amongus/)
[![discord](https://img.shields.io/discord/747858042007060613?color=7289da&label=Discord&logo=discord&logoColor=white)](https://tecf.de/amongusio-discord)
[![made with python](https://img.shields.io/badge/Made%20with-Python-007ec6.svg?logo=python&logoColor=white)](https://www.python.org/)
[![black](https://img.shields.io/badge/Code%20Style-black-000.svg)](https://github.com/psf/black)

</div>

## Note
> This repository is mirrored from [Gitlab][gitlab-repo] to [Github][github-repo].
> Most features like Issues, MRs/PRs etc. are disabled on [Github][github-repo], please use the
> [Gitlab repository][gitlab-repo] for these

## Info
AmongUsIO is an asynchronous Among Us client written in Python. 
It tries to expose methods for features of the official Among Us client, like meeting starts and ends

Made by reverse engineering with [Wireshark](https://www.wireshark.org/) and by reading the source code of an [unofficial Among Us server][impostor/impostor]

## Features
- Supports custom Among Us servers like [Impostor][impostor/impostor] 
  (this server does not support "spectating" though as it's kinda hacky)
- Join Among Us lobbies
- Receive and send chat messages
- Get information about the lobby and the other players
- Move the character around, for example letting it follow people
- "Spectate". This makes the connection kind of read only, you cannot move etc.
  but the Client can receive events like meetings while being completely invisible
  (one drawback: we still need one player slot for this, as the client technically 
  counts as a player)

## Documentation
- [Stable](https://amongusio.readthedocs.io/en/stable)
- [Latest](https://amongusio.readthedocs.io/en/latest)

## Installation
```sh
# currently only released on testpypi by CI
python -m pip install --index-url https://test.pypi.org/simple/ amongusio
```

Development version:
```sh
python -m pip install git+https://gitlab.com/TECHNOFAB/amongusio.git
# or
python -m pip install git+https://github.com/TECHNOFAB11/amongusio.git
```

## Example
```python
import amongus

client = amongus.Client(name="Bot")

@client.event
async def on_ready():
    # connected and ready to send commands, eg:
    await client.join_lobby("ABCDEF")

client.run(region="EU")
```
> see [the examples folder](examples) for more

## Roadmap / TODO

> see [TODO.md](TODO.md)

## Development & Tools

Parse Wireshark data and print the parsed packets
```sh
python -m amongus --parse <Wireshark Data (example: 00112233445566)>
```

For more information:
```sh
python -m amongus --help
```

[gitlab-repo]: https://gitlab.com/TECHNOFAB/amongusio
[github-repo]: https://github.com/TECHNOFAB11/amongusio
[impostor/impostor]: https://github.com/Impostor/Impostor
