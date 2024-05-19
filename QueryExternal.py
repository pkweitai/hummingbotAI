
def QueryExternalToolTable(self,bottype):
        table = None

        if bottype == "devops":
            from featuretable_devops import DevOpTools
            table = DevOpTools(username="xyz", 
                        token="<abcd>", 
                        base_url="localhost")
        return table
