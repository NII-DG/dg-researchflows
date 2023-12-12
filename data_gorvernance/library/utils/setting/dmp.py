from ..file import JsonFile

class DMPManager(JsonFile):

    def __init__(self, file_path: str):
        super().__init__(file_path)

    @staticmethod
    def create_dmp_options(contents):
        dmps = contents['dmp']
        options = {}
        for i, dmp in enumerate(dmps):
            title = dmp['title']
            options[title] = i
        return options

    @staticmethod
    def get_dmp(contents, index):
        return {"dmp": [contents['dmp'][index]]}

    @staticmethod
    def display_format(content):
        dmp = content['dmp'][0]
        dmp_str = f"### {dmp['title']}<br><hr><br>"
        for key, value in dmp.items():
            if key != "title" or key != 'grdm-files':
                dmp_str += f'{key} : {value}<br>'
        files = dmp['grdm-files']
        dmp_str += "grdm-files :<br>"
        for file in files:
            dmp_str += f'&emsp;{file["path"]}<br>'
        return dmp['title'], dmp_str

