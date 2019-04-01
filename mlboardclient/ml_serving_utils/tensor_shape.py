from ml_serving import tensor_shape_pb2
from ml_serving.utils import compat
from ml_serving.utils import dtypes


class TensorShape(object):
    """Represents the shape of a `Tensor`.
      A `TensorShape` represents a possibly-partial shape specification for a
      `Tensor`. It may be one of the following:
      * *Fully-known shape:* has a known number of dimensions and a known size
        for each dimension. e.g. `TensorShape([16, 256])`
      * *Partially-known shape:* has a known number of dimensions, and an unknown
        size for one or more dimension. e.g. `TensorShape([None, 256])`
      * *Unknown shape:* has an unknown number of dimensions, and an unknown
        size in all dimensions. e.g. `TensorShape(None)`
      If a tensor is produced by an operation of type `"Foo"`, its shape
      may be inferred if there is a registered shape function for
      `"Foo"`. See @{$adding_an_op#shape-functions-in-c$`Shape functions in C++`}
      for details of shape functions and how to register them. Alternatively,
      the shape may be set explicitly using @{tf.Tensor.set_shape}.
    """

    def __init__(self, dims):
        """Creates a new TensorShape with the given dimensions.
        Args:
          dims: A list of Dimensions, or None if the shape is unspecified.
            DEPRECATED: A single integer is treated as a singleton list.
        Raises:
          TypeError: If dims cannot be converted to a list of dimensions.
        """
        # TODO(irving): Eliminate the single integer special case.
        if dims is None:
            self._dims = None
        elif isinstance(dims, compat.bytes_or_text_types):
            raise TypeError("A string has ambiguous TensorShape, please wrap in a "
                            "list or convert to an int: %s" % dims)
        elif isinstance(dims, tensor_shape_pb2.TensorShapeProto):
            if dims.unknown_rank:
                self._dims = None
            else:
                self._dims = [
                    # Protos store variable-size dimensions as -1
                    as_dimension(dim.size if dim.size != -1 else None)
                    for dim in dims.dim
                ]
        elif isinstance(dims, TensorShape):
            self._dims = dims.dims
        else:
            try:
                dims_iter = iter(dims)
            except TypeError:
                # Treat as a singleton dimension
                self._dims = [as_dimension(dims)]
            else:
                # Got a list of dimensions
                self._dims = [as_dimension(d) for d in dims_iter]
        self._ndims = None

    def as_proto(self):
        """Returns this shape as a `TensorShapeProto`."""
        if self._dims is None:
            return tensor_shape_pb2.TensorShapeProto(unknown_rank=True)
        else:
            return tensor_shape_pb2.TensorShapeProto(dim=[
                tensor_shape_pb2.TensorShapeProto.Dim(
                    size=-1 if d.value is None else d.value
                )
                for d in self._dims
            ])


def as_dimension(value):
    """
    Converts the given value to a Dimension.

      A Dimension input will be returned unmodified.
      An input of `None` will be converted to an unknown Dimension.
      An integer input will be converted to a Dimension with that value.
      Args:
        value: The value to be converted.
      Returns:
        A Dimension corresponding to the given value.
    """
    if isinstance(value, Dimension):
        return value
    else:
        return Dimension(value)


class Dimension(object):
    """Represents the value of one dimension in a TensorShape."""

    def __init__(self, value):
        """Creates a new Dimension with the given value."""
        if value is None:
            self._value = None
        elif isinstance(value, dtypes.DType):
            raise TypeError("Cannot convert %s to Dimension" % value)
        else:
            self._value = int(value)
            if (not isinstance(value, compat.bytes_or_text_types) and
                    self._value != value):
                raise ValueError("Ambiguous dimension: %s" % value)
            if self._value < 0:
                raise ValueError("Dimension %d must be >= 0" % self._value)

    def __repr__(self):
        return "Dimension(%s)" % repr(self._value)

    def __str__(self):
        value = self._value
        return "?" if value is None else str(value)

    @property
    def value(self):
        """The value of this dimension, or None if it is unknown."""
        return self._value


def as_shape(shape):
    """Converts the given object to a TensorShape."""
    if isinstance(shape, TensorShape):
        return shape
    else:
        return TensorShape(shape)
