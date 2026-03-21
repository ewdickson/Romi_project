import array
import gc
import pyb
import micropython


share_list = []
"""System-wide list of all queues and shares for diagnostics."""


type_code_strings = {
    'b': "int8",   'B': "uint8",
    'h': "int16",  'H': "uint16",
    'i': "int(?)", 'I': "uint(?)",
    'l': "int32",  'L': "uint32",
    'q': "int64",  'Q': "uint64",
    'f': "float",  'd': "double"
}
"""Dictionary mapping type codes to readable type names."""


def show_all():
    """
    Create a diagnostic summary of all queues and shares in the system.

    Returns:
        str: A newline-separated string describing each registered queue
        and share.
    """
    gen = (str(item) for item in share_list)
    return '\n'.join(gen)


class BaseShare:
    """
    Base class for queues and shares used to exchange data between tasks.

    This class stores configuration shared by Queue and Share objects and
    registers each instance in the global diagnostic list.
    """

    def __init__(self, type_code, thread_protect=True, name=None):
        """
        Initialize common data used by queues and shares.

        Args:
            type_code: Type code describing the stored data type.
            thread_protect: True if interrupt protection should be used.
            name: Optional name for diagnostics.
        """
        self._type_code = type_code
        self._thread_protect = thread_protect

        share_list.append(self)


class Queue(BaseShare):
    """
    Queue used to transfer buffered data from one task to another.
    """

    ser_num = 0
    """Serial number counter used to generate default queue names."""

    def __init__(self, type_code, size, thread_protect=False,
                 overwrite=False, name=None):
        """
        Initialize a queue object.

        Args:
            type_code: Type code for data stored in the queue.
            size: Maximum number of items the queue can hold.
            thread_protect: True if mutual exclusion protection is used.
            overwrite: True if old data may be overwritten when full.
            name: Optional diagnostic name for the queue.
        """
        super().__init__(type_code, thread_protect, name)

        self._size = size
        self._overwrite = overwrite
        self._name = str(name) if name is not None \
            else 'Queue' + str(Queue.ser_num)
        Queue.ser_num += 1

        try:
            self._buffer = array.array(type_code, range(size))
        except MemoryError:
            self._buffer = None
            raise
        except ValueError:
            self._buffer = None
            raise

        self.clear()
        gc.collect()

    @micropython.native
    def put(self, item, in_ISR=False):
        """
        Put an item into the queue.

        Args:
            item: Data item to place into the queue.
            in_ISR: True if called from within an interrupt service routine.
        """
        if self.full():
            if in_ISR:
                return

            if not self._overwrite:
                while self.full():
                    pass

        if self._thread_protect and not in_ISR:
            _irq_state = pyb.disable_irq()

        self._buffer[self._wr_idx] = item
        self._wr_idx += 1
        if self._wr_idx >= self._size:
            self._wr_idx = 0
        self._num_items += 1
        if self._num_items >= self._size:
            self._num_items = self._size
        if self._num_items > self._max_full:
            self._max_full = self._num_items

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(_irq_state)

    @micropython.native
    def get(self, in_ISR=False):
        """
        Read and return an item from the queue.

        Args:
            in_ISR: True if called from within an interrupt service routine.

        Returns:
            The next item stored in the queue.
        """
        while self.empty():
            pass

        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        to_return = self._buffer[self._rd_idx]

        self._rd_idx += 1
        if self._rd_idx >= self._size:
            self._rd_idx = 0
        self._num_items -= 1
        if self._num_items < 0:
            self._num_items = 0

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

        return to_return

    @micropython.native
    def any(self):
        """
        Check whether the queue contains any items.

        Returns:
            bool: True if at least one item is in the queue.
        """
        return self._num_items > 0

    @micropython.native
    def empty(self):
        """
        Check whether the queue is empty.

        Returns:
            bool: True if the queue contains no items.
        """
        return self._num_items <= 0

    @micropython.native
    def full(self):
        """
        Check whether the queue is full.

        Returns:
            bool: True if no more data can be added without overwriting.
        """
        return self._num_items >= self._size

    @micropython.native
    def num_in(self):
        """
        Return the number of items currently stored in the queue.

        Returns:
            int: Number of items in the queue.
        """
        return self._num_items

    def clear(self):
        """Remove all items from the queue and reset internal pointers."""
        self._rd_idx = 0
        self._wr_idx = 0
        self._num_items = 0
        self._max_full = 0

    def __repr__(self):
        """
        Return a diagnostic string describing the queue.

        Returns:
            str: Queue name, type, and maximum observed fill level.
        """
        return ('{:<12s} Queue<{:s}> Max Full {:d}/{:d}'.format(
            self._name,
            type_code_strings[self._type_code],
            self._max_full,
            self._size
        ))


class Share(BaseShare):
    """
    Shared data item used to transfer one value between tasks.

    A Share stores a single value and can optionally protect access from
    corruption caused by interrupts or pre-emptive execution.
    """

    ser_num = 0
    """Serial number counter used to generate default share names."""

    def __init__(self, type_code, thread_protect=True, name=None):
        """
        Create a shared data item.

        Args:
            type_code: Type code for the shared data item.
            thread_protect: True if mutual exclusion protection is used.
            name: Optional diagnostic name for the share.
        """
        super().__init__(type_code, thread_protect, name)

        self._buffer = array.array(type_code, [0])

        self._name = str(name) if name is not None \
            else 'Share' + str(Share.ser_num)
        Share.ser_num += 1

    @micropython.native
    def put(self, data, in_ISR=False):
        """
        Write data into the share.

        Args:
            data: Value to store in the share.
            in_ISR: True if called from within an interrupt service routine.
        """
        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        self._buffer[0] = data

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

    @micropython.native
    def get(self, in_ISR=False):
        """
        Read and return the current value stored in the share.

        Args:
            in_ISR: True if called from within an interrupt service routine.

        Returns:
            The current shared data value.
        """
        if self._thread_protect and not in_ISR:
            irq_state = pyb.disable_irq()

        to_return = self._buffer[0]

        if self._thread_protect and not in_ISR:
            pyb.enable_irq(irq_state)

        return to_return

    def __repr__(self):
        """
        Return a diagnostic string describing the share.

        Returns:
            str: Share name and data type.
        """
        return "{:<12s} Share<{:s}>".format(
            self._name,
            type_code_strings[self._type_code]
        )