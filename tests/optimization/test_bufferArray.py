from code.optimization.bufferArray import BufferArray

class TestBufferArray():
    
   def test_capacity(self):
        self.bufferArray = BufferArray(1)
        self.bufferArray.push(1,None,None,None)
        assert(len(self.bufferArray)==1)
