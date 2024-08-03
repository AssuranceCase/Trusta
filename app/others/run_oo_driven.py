from pycallgraph import Config
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from trusta_main import trusta_main

#  Create a new output class 
class TextGraphvizOutput(GraphvizOutput):
    def done(self):
        source = self.generate()
        self.output_text = source


def gen_dot():
    text_graphviz = TextGraphvizOutput()
    with PyCallGraph(output=text_graphviz):
        trusta_main()
    return text_graphviz.output_text

if __name__ == "__main__":
    output_text = gen_dot()
    with open('trusta_callgraph.dot', 'w', encoding='utf-8') as f:
        f.write(output_text)
    # print('-------', output_text)