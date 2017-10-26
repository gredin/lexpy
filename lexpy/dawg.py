from lexpy._base.node import FSANode
from lexpy._base.automata import FSA


def build_dawg_from_file(infile=None):
    """
        Description:
            This method can be used to create a DAWG from an input file of words.
            Each word is expected to be on a new line.

        Args:
            :arg infile (str or File): Either absolute file path or a File object

        Returns:
            :returns dawg (`lexypy.dawg.DAWG`) : An instance of DAWG class created after inserting all the words.

        Raises:
            :raises `ValueError` : If the input file is `None`
        """
    if infile is None:
        raise ValueError("Please provide the file path")
    dawg = DAWG()
    dawg.add_all(infile)
    return dawg


class _DAWGNode(FSANode):

    def add_child(self, letter, _id=None):
        """
        Description:
            To add a child edge to the current Node.

        Args:
            :arg letter (str) The character label that the child node will have.
            :arg id (int) Unique numerical ID assigned to this node.

        """
        self.children[letter] = _DAWGNode(_id, letter)


class DAWG(FSA):

    def __init__(self):
        root = _DAWGNode(1, '')
        FSA.__init__(self, root)
        self.__prev_word = ''
        self.__minimized_nodes = {}
        self.__unchecked_nodes = []

    def add(self, word):
        if word < self.__prev_word:
            raise ValueError("Insert in alphabetical order.")
            # find common prefix between word and previous word
        common_prefix_index = 0
        for i in range(min(len(word), len(self.__prev_word))):
            if word[i] != self.__prev_word[i]: break
            common_prefix_index += 1
        self._reduce(common_prefix_index)
        if len(self.__unchecked_nodes) == 0:
            node = self.root
        else:
            node = self.__unchecked_nodes[-1][2]

        for letter in word[common_prefix_index:]:
            _id = self._id + 1
            node.add_child(letter, _id)
            self.__unchecked_nodes.append((node, letter, node[letter]))
            node = node[letter]

        node.eow = True
        self._num_of_words += 1
        self.__prev_word = word

    def reduce(self):
        self._reduce(0)

    def _reduce(self, to):
        for i in range(len(self.__unchecked_nodes)-1, to-1, -1):
            (parent, letter, child) = self.__unchecked_nodes[i]
            if child in self.__minimized_nodes:
                parent.children[letter] = child
            else:
                self.__minimized_nodes[child] = child
            self.__unchecked_nodes.pop()

    def __len__(self):
        """
        Description:
            Returns the number of nodes in the DAWG Data Structure

        Returns:
            :returns (int) Number of Nodes in the dawg data structure
        :return:
        """
        return 1+len(self.__minimized_nodes) # 1(for the root node) + Minimized list of nodes