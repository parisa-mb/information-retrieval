import re


#Preprocess

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = text.split()
    return tokens

#Build Inverted Index
def build_index(docs):
    index = {}

    for docID, text in docs.items():
        tokens = preprocess(text)
        for tok in tokens:
            if tok not in index:
                index[tok] = []
            if len(index[tok]) == 0 or index[tok][-1][0] != docID:
                index[tok].append([docID, 0])
            index[tok][-1][1] += 1
    return index

#Write postings to file
def write_postings(index):
    offsets = {}
    with open("postings.txt", "w") as f:
        for term, plist in index.items():
            offsets[term] = f.tell()
            f.write(f"{term}: {plist}\n")
    return offsets

#Simple B-Tree implementation
class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t            # minimum degree
        self.keys = []        # (key, value) pairs
        self.children = []    # child pointers
        self.leaf = leaf

class BTree:
    def __init__(self, t=3):
        self.root = BTreeNode(t, leaf=True)
        self.t = t

    # Search traditional
    def search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1

        if i < len(node.keys) and node.keys[i][0] == key:
            return node.keys[i]

        if node.leaf:
            return None
        else:
            return self.search(node.children[i], key)

    # Split a full child
    def split_child(self, parent, index, child):
        t = child.t
        new_node = BTreeNode(t, leaf=child.leaf)

        parent.children.insert(index + 1, new_node)
        parent.keys.insert(index, child.keys[t - 1])

        new_node.keys = child.keys[t:(2 * t - 1)]
        child.keys = child.keys[0:t - 1]

        if not child.leaf:
            new_node.children = child.children[t:(2 * t)]
            child.children = child.children[0:t]

    # Insert key in non-full node
    def insert_nonfull(self, node, key):
        if node.leaf:
            node.keys.append(key)
            node.keys.sort(key=lambda x: x[0])
        else:
            i = len(node.keys) - 1
            while i >= 0 and key[0] < node.keys[i][0]:
                i -= 1
            i += 1

            if len(node.children[i].keys) == (2 * node.t - 1):
                self.split_child(node, i, node.children[i])
                if key[0] > node.keys[i][0]:
                    i += 1

            self.insert_nonfull(node.children[i], key)

    # Public insert
    def insert(self, k, v):
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            new_root = BTreeNode(self.t, leaf=False)
            new_root.children.append(root)
            self.split_child(new_root, 0, root)
            self.root = new_root
            self.insert_nonfull(new_root, (k, v))
        else:
            self.insert_nonfull(root, (k, v))

    # Pretty print
    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print("   " * level, node.keys)
        if not node.leaf:
            for child in node.children:
                self.print_tree(child, level + 1)


if __name__ == "__main__":
    # sample docs
    docs = {
        1: "Apple banana apple orange",
        2: "Banana fruit apple",
        3: "Car drives fast on the road"
    }

    index = build_index(docs)

    print("Inverted index:")
    for term, postings in index.items():
        print(term, postings)

    offsets = write_postings(index)

    print("\nOffsets:")
    print(offsets)

    tree = BTree(t=3)
    for term, off in offsets.items():
        tree.insert(term, off)

    print("\nB-Tree structure:")
    tree.print_tree()


