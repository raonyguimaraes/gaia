
from base import TestCase
from gaia.core import stream, task, port

Stream = stream.registry['Stream']


class ZeroStream(Stream):

    """A dumb streaming class that always returns 0."""

    def read(self):
        """Return 0."""
        return 0


class IPort(port.InputPort):

    """Test input port."""

    name = 'input port'

    def accepts(self):
        """Return ZeroStream accepted."""
        return set((ZeroStream,))


class OPort(port.OutputPort):

    """Test output port."""

    name = 'output port'

    def emits(self):
        """Return ZeroStream emitted."""
        return set((ZeroStream,))


class Task1(task.Task):

    """A task with an output port."""

    output_ports = [OPort]


class Task2(task.Task):

    """A task with an input port."""

    input_ports = [IPort]


class TestStream(Stream):

    """A testing streaming class that tracks calls."""

    def __init__(self, obj, *arg, **kw):
        """Initialize the streamer."""

        task1 = Task1()
        task2 = Task2()

        self.obj = obj
        self.obj['nclose'] = 0
        self.obj['nflush'] = 0

        super(TestStream, self).__init__(
            task1.get_output('output port'),
            task2.get_input('input port')
        )

        task2.set_input('input port', task1.get_output('output port'))

    def flush(self):
        """Flush the stream."""
        self.obj['nflush'] += 1
        super(TestStream, self).flush()

    def close(self):
        """Close the stream."""
        self.obj['nclose'] += 1
        super(TestStream, self).close()


class TestStreamCase(TestCase):

    """Test the base stream class."""

    def test_stream_registry(self):
        """Test the stream registry."""

        self.assertEquals(
            stream.registry.get('ZeroStream'),
            ZeroStream
        )

    def test_default_stream(self):
        """Test the default streaming behavior."""

        s = TestStream({})
        d = {}
        self.assertTrue(
            s.write(d)
        )

        self.assertTrue(
            s.read() is d
        )

        self.assertTrue(
            s.read() is None
        )

    def test_close_stream(self):
        """Test flush called when closing a stream."""
        s = TestStream({})

        s.close()

        self.assertEquals(
            s.obj['nflush'],
            1
        )
        self.assertEquals(
            s.obj['nclose'],
            1
        )

    def test_delete_stream(self):
        """Test flush called when deleting a stream."""
        o = {}
        s = TestStream(o)

        del s

        self.assertEqual(o['nflush'], 1)

        TestStream(o)
        self.assertEqual(o['nflush'], 1)