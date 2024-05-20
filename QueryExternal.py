
def QueryExternalToolTable(bottype,llm):
        table = None

        if bottype == "general":
            from featuretable_devops import DevOpTools
            table = DevOpTools(username="xyz", 
                        token="<abcd>", 
                        base_url="localhost",llm=llm)
        return table
