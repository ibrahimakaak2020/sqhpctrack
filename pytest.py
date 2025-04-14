from collections.abc import MutableSequence

class MyMutableSequence(MutableSequence):
    def __init__(self, data=None):
        self._data = list(data) if data else []

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
       del self._data[index]

    def __len__(self):
        return len(self._data)

    def insert(self, index, value):
        self._data.insert(index, value)
    def __repr__(self):
        return f"MyMutableSequence({self._data})"

# Example use
seq = MyMutableSequence([1, 2, 3])
seq.append(4)
seq[1] = 99
del seq[0]

print(seq)        # Output: [99, 3, 4]
print(list(seq))  # Output: [99, 3, 4]
