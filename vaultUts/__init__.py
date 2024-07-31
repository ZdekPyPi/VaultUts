import configparser as cp
import requests
import json
from datetime import datetime

class VaultLib:
    def __init__(self,host,token:str,in_prd:bool=True,dev_ini_file=None):
        self.token        = token
        self.host         = host
        self.in_prd       = in_prd
        self.dev_ini_file = dev_ini_file
    
    def format_data(self,dtClass,k,v):
        cls = dtClass.__annotations__[k]
        if cls == tuple:
            name =  f"{str(dtClass)}_{k}"
            if not name in self.delimiters:
                isFormatDefined = k in [x for x in dir(dtClass) if not re.search("__.*__", x)]
                delimiter = getattr(dtClass,k) if isFormatDefined else ','
                self.delimiters[name]=delimiter
                a = 2

            v = tuple(v.split(self.delimiters[name]))
        elif cls == datetime:
            name =  f"{str(dtClass)}_{k}"
            if not name in self.dateFormats:
                isFormatDefined = k in [x for x in dir(dtClass) if not re.search("__.*__", x)]
                delimiter = getattr(dtClass,k) if isFormatDefined else '%Y-%m-%d'
                self.dateFormats[name]=delimiter
                a = 2

            v = datetime.strptime(v,self.dateFormats[name])
        elif cls == bool:
            val = v.strip().lower()
            v = True if val and val in ['true','1','y'] else False
            v = False if val in ['false','','0','n'] else True

        else:
            v = cls(v)
        return v
    
    def getVault(self,path):
        url = f"{self.host}/v1/{path}"

        headers = {'X-Vault-Token': self.token}

        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()['data']['data']

    def Section2Dict(self,section,fileIni,empty_as_null=False):
        config = cp.RawConfigParser(allow_no_value=True)
        config.optionxform = str
        config.read(fileIni)

        dc = dict(config[section])
        return dc if not empty_as_null else {x:(y or None) for x,y in dc.items()}

    def vault2DataClass(self,path,dtClass,create_missing=False,dev_section=None):
        vault = self.getVault(path)
        dt_dev = self.Section2Dict(dev_section,fileIni=self.dev_ini_file) if dev_section else None
        dtClass.vault_path = path
        for k, v in vault.items():
            if not k in dtClass.__annotations__:
                if not create_missing and not create_missing:
                    raise Exception(f"please create the key '{k}' in data class object")
                elif create_missing:
                    setattr(dtClass, k, v)
                else:
                    continue
            setattr(dtClass, k, v)

        if not self.in_prd and dev_section:
            for k, v in dt_dev.items():
                if not k in dtClass.__annotations__:
                    raise Exception(f"key '{k}' not found in data class object")
                v = self.format_data(dtClass,k,v)
                setattr(dtClass, k, v)
        
    def link(self,path,create_missing=False,dev_section=None):
        def wrap(function):
            self.vault2DataClass(path,function,create_missing,dev_section)
            return function
        return wrap

    def setVault(self,path,data):
        url = f"{self.host}/v1/{path}"

        headers = {'X-Vault-Token': self.token,'Content-Type':'application/json'}

        data2 = {"data": data}

        response = requests.request("POST", url, headers=headers, data=json.dumps(data2))
        if response.status_code != 200:
            raise Exception(response.text)




