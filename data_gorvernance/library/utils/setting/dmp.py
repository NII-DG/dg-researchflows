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
            if key != "title" and key != 'grdm-files':
                dmp_str += f'{value.get("label_jp")} : {value.get("value")}<br>'
        files = dmp['grdm-files']
        dmp_str += f'{files.get("label_jp")} :<br>'
        value = files.get("value")
        for file in value:
            dmp_str += f'&emsp;{file.get("path")}<br>'
        return dmp_str

