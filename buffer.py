

class Buffer:

    def __init__(self, size):
        if Buffer._validate_num(size) < 1:
            raise ValueError('Size must be greater than 0')
        self._size = size
        self._queue = []

    def write(self, num):
        if len(self._queue) < self._size:
            self._queue.append(Buffer._validate_num(num))
        else:
            print('Buffer max size reached, cannot insert {}'.format(Buffer._validate_num(num)))

    def read(self):
        if self._queue:
            return self._queue.pop(0)
        else:
            print('Buffer is empty')

    def length(self):
        return len(self._queue)

    @staticmethod
    def _validate_num(num):
        if type(num) not in [int]:
            raise ValueError('Input must be an integer')
        return num


buffer1 = Buffer(10)
for i in range(10):
    buffer1.write(i)

print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
print(buffer1.read())
