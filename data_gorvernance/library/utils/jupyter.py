from time import sleep

from IPython.display import display, Javascript
from IPython import get_ipython


class Jupyter:
    def __init__(self) -> None:
        self.params = None
        self.tag = None

    def target_func(self, comm, open_msg):
        # comm is the kernel Comm instance
        # open_msg is the comm_open message

        # register handler for later messages
        @comm.on_msg
        def _recv(msg):
            # data is in msg['content']['data']
            comm.send({'echo': msg['content']['data']})
            for k, v in msg['content']['data']:
                if k == self.tag:
                    self.params = v

        # send data to the front end on creation
        comm.send({'rf': 1})

    def get_cell_data(self):
        self.tag = 'cell_data_target'
        # register the comm target on the kernel side (back end)
        get_ipython().kernel.comm_manager.register_target(
            self.tag, self.target_func
        )
        sleep(0.2)
        # register the comm target on the browser side (front end)
        display(Javascript(f'''
const comm = Jupyter.notebook.kernel.comm_manager.new_comm('{self.tag}', {{'rf': 1}});
var index = Jupyter.notebook.get_selected_index();
comm.send({{'notebook_metadata': Jupyter.notebook.get_cell(index-1)}});

comm.on_msg(function(msg) {{
console.log(msg.content.data);
}});
'''))
        return self.params
