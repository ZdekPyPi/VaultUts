#TEST FILE
from dotenv import load_dotenv
import sys
import os
sys.path.append("./vaultUts")
from vaultUts import *
load_dotenv()

#Pessoa = MyMeta("Pessoa", (Pessoa,), dict(Pessoa.__dict__))

#Pessoa.name
vlt = VaultLib("","",in_prd=True)


@vlt.link("Teste/data/auth")
class BotVault: 
    hehe      : str

@vlt.link("Teste/data/auth")
class BotVault2: 
    hehe      : str

#BotVault.hehe = "AI SIM"

#BotVault.save()
print(BotVault.hehe)
BotVault.refresh()


print(BotVault.hehe)


pass

