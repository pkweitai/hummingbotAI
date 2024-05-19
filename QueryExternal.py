
def QueryExternalToolTable(self,bottype):
        table = None

        if bottype == "devops":
            from featuretable_devops import DevOpTools
            table = DevOpTools(username="rex", 
                        token="11674e095f68011018a1ed0a413e999f39", 
                        base_url="192.168.1.26")
        return table